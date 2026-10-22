"""Autenticacion privada del MVP (RF-00).

RF-00.1: todo salvo /salud y /login exige sesion. RF-00.2: sin registro
publico; las cuentas se crean con backend/crear_usuario.py. RF-00.3: mensaje
generico ante credenciales incorrectas. RF-00.4: sesion con token opaco en
cookie HttpOnly (decision tomada aqui, reversible).

Contrasenas con PBKDF2-HMAC-SHA256 (210 000 iteraciones, sal unica). En
SQLite solo se guarda el hash del token, con caducidad de 12 horas. Base en
backend/datos.db o en MOTORREVISIONLEGAL_DB (pruebas). Sin IA ni criterios.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

NOMBRE_COOKIE = "sesion_mrl"
DURACION_SESION = timedelta(hours=12)
ITERACIONES_PBKDF2 = 210_000
LONGITUD_MINIMA_CONTRASENA = 8
LONGITUD_MAXIMA_NOMBRE = 64
NOMBRE_VARIABLE_BD = "MOTORREVISIONLEGAL_DB"
MENSAJE_CREDENCIALES_INVALIDAS = "Usuario o contraseña incorrectos."
MENSAJE_NO_AUTENTICADO = "Se requiere iniciar sesión para usar esta función."
COD_CREDENCIALES_INVALIDAS = "credenciales_invalidas"
COD_NO_AUTENTICADO = "no_autenticado"


def ruta_bd() -> Path:
    """Ruta SQLite: la de entorno o ``backend/datos.db``."""
    personalizada = os.environ.get(NOMBRE_VARIABLE_BD)
    if personalizada:
        return Path(personalizada)
    return Path(__file__).resolve().parent.parent / "datos.db"


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _conectar(ruta: Path) -> sqlite3.Connection:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(str(ruta))
    conexion.row_factory = sqlite3.Row
    return conexion


def init_bd(ruta: str | Path | None = None) -> Path:
    """Crea las tablas si no existen y devuelve la ruta usada."""
    destino = Path(ruta) if ruta is not None else ruta_bd()
    conexion = _conectar(destino)
    try:
        conexion.execute(
            "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY "
            "AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE, hash_contrasena "
            "TEXT NOT NULL, sal TEXT NOT NULL, creado TEXT NOT NULL)"
        )
        conexion.execute(
            "CREATE TABLE IF NOT EXISTS sesiones (token_hash TEXT PRIMARY "
            "KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON "
            "DELETE CASCADE, creado TEXT NOT NULL, expira TEXT NOT NULL)"
        )
        conexion.execute(
            "CREATE INDEX IF NOT EXISTS idx_sesiones_expira "
            "ON sesiones(expira)"
        )
        conexion.execute(
            "CREATE TABLE IF NOT EXISTS analisis ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON "
            "DELETE CASCADE, "
            "fecha TEXT NOT NULL, "
            "tipo_confirmado TEXT NOT NULL, "
            "num_hallazgos INTEGER NOT NULL, "
            "hallazgos TEXT NOT NULL)"
        )
        conexion.execute(
            "CREATE INDEX IF NOT EXISTS idx_analisis_usuario_fecha "
            "ON analisis(usuario_id, fecha DESC)"
        )
        conexion.commit()
    finally:
        conexion.close()
    return destino


def _resumir(contrasena: str, sal: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"), sal, ITERACIONES_PBKDF2
    ).hex()


def crear_usuario(
    nombre: str, contrasena: str, ruta: str | Path | None = None
) -> int:
    """Da de alta un usuario autorizado; devuelve su id.

    Lanza ValueError si el nombre esta vacio, ya existe o la clave es
    corta. La contrasena nunca se guarda en claro.
    """
    limpio = (nombre or "").strip()
    if not limpio:
        raise ValueError("El nombre de usuario no puede estar vacío.")
    if len(limpio) > LONGITUD_MAXIMA_NOMBRE:
        raise ValueError("El nombre de usuario es demasiado largo.")
    if len(contrasena or "") < LONGITUD_MINIMA_CONTRASENA:
        raise ValueError(
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_CONTRASENA} "
            "caracteres."
        )
    destino = init_bd(ruta)
    sal = secrets.token_bytes(16)
    resumen = _resumir(contrasena, sal)
    conexion = _conectar(destino)
    try:
        cursor = conexion.execute(
            "INSERT INTO usuarios (nombre, hash_contrasena, sal, creado) "
            "VALUES (?, ?, ?, ?)",
            (limpio, resumen, sal.hex(), _ahora().isoformat()),
        )
        conexion.commit()
        return int(cursor.lastrowid)
    except sqlite3.IntegrityError:
        raise ValueError(f'El usuario "{limpio}" ya existe.') from None
    finally:
        conexion.close()

def reestablecer_contrasena(
    nombre: str, contrasena_nueva: str, ruta: str | Path | None = None
) -> None:
    """Cambia la contraseña de un usuario existente y revoca sus sesiones.

    Reutiliza el mismo hash PBKDF2 que el alta. Lanza ``ValueError`` si el
    usuario no existe o la contraseña nueva es demasiado corta. Al cambiar
    la clave se invalidan todas las sesiones activas del usuario, para que
    quien tuviera una sesión abierta deba volver a iniciar sesión.
    """
    limpio = (nombre or "").strip()
    if not limpio:
        raise ValueError("El nombre de usuario no puede estar vacío.")
    if len(contrasena_nueva or "") < LONGITUD_MINIMA_CONTRASENA:
        raise ValueError(
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_CONTRASENA} "
            "caracteres."
        )
    destino = init_bd(ruta)
    sal = secrets.token_bytes(16)
    resumen = _resumir(contrasena_nueva, sal)
    conexion = _conectar(destino)
    try:
        fila = conexion.execute(
            "SELECT id FROM usuarios WHERE nombre = ?", (limpio,)
        ).fetchone()
        if fila is None:
            raise ValueError(f'El usuario "{limpio}" no existe.')
        conexion.execute(
            "UPDATE usuarios SET hash_contrasena = ?, sal = ? "
            "WHERE id = ?",
            (resumen, sal.hex(), int(fila["id"])),
        )
        conexion.execute(
            "DELETE FROM sesiones WHERE usuario_id = ?", (int(fila["id"]),)
        )
        conexion.commit()
    finally:
        conexion.close()


def comprobar_credenciales(
    nombre: str, contrasena: str, ruta: str | Path | None = None
) -> int | None:
    """Devuelve el id si las credenciales son validas, o None.

    Tanto si el usuario no existe como si la clave es incorrecta devuelve
    None tras un trabajo equivalente: no se puede distinguir por tiempo ni
    por mensaje (RF-00.3).
    """
    destino = init_bd(ruta)
    conexion = _conectar(destino)
    try:
        fila = conexion.execute(
            "SELECT id, hash_contrasena, sal FROM usuarios WHERE nombre = ?",
            ((nombre or "").strip(),),
        ).fetchone()
    finally:
        conexion.close()
    if fila is None:
        _resumir(contrasena or "", b"\x00" * 16)
        return None
    calculado = _resumir(contrasena or "", bytes.fromhex(fila["sal"]))
    if hmac.compare_digest(calculado, fila["hash_contrasena"]):
        return int(fila["id"])
    return None


def crear_sesion(usuario_id: int, ruta: str | Path | None = None) -> str:
    """Crea una sesion y devuelve el token opaco (solo se guarda su hash)."""
    destino = init_bd(ruta)
    token = secrets.token_urlsafe(32)
    resumen = hashlib.sha256(token.encode("utf-8")).hexdigest()
    ahora = _ahora()
    conexion = _conectar(destino)
    try:
        conexion.execute(
            "DELETE FROM sesiones WHERE expira <= ?", (ahora.isoformat(),)
        )
        conexion.execute(
            "INSERT INTO sesiones (token_hash, usuario_id, creado, expira) "
            "VALUES (?, ?, ?, ?)",
            (
                resumen, usuario_id, ahora.isoformat(),
                (ahora + DURACION_SESION).isoformat(),
            ),
        )
        conexion.commit()
    finally:
        conexion.close()
    return token


def obtener_usuario_por_token(
    token: str | None, ruta: str | Path | None = None
) -> str | None:
    """Nombre del usuario de una sesion valida, o None."""
    if not token:
        return None
    destino = init_bd(ruta)
    resumen = hashlib.sha256(token.encode("utf-8")).hexdigest()
    conexion = _conectar(destino)
    try:
        fila = conexion.execute(
            "SELECT u.nombre AS nombre FROM sesiones s JOIN usuarios u "
            "ON u.id = s.usuario_id WHERE s.token_hash = ? AND s.expira > ?",
            (resumen, _ahora().isoformat()),
        ).fetchone()
    finally:
        conexion.close()
    return str(fila["nombre"]) if fila is not None else None


def obtener_usuario_id_por_token(
    token: str | None, ruta: str | Path | None = None
) -> int | None:
    """Devuelve el id de usuario de una sesion valida, o None."""
    if not token:
        return None
    destino = init_bd(ruta)
    resumen = hashlib.sha256(token.encode("utf-8")).hexdigest()
    conexion = _conectar(destino)
    try:
        fila = conexion.execute(
            "SELECT s.usuario_id FROM sesiones s "
            "WHERE s.token_hash = ? AND s.expira > ?",
            (resumen, _ahora().isoformat()),
        ).fetchone()
    finally:
        conexion.close()
    return int(fila["usuario_id"]) if fila is not None else None


def cerrar_sesion(token: str | None, ruta: str | Path | None = None) -> None:
    """Invalida la sesion del token, si existe. Nunca falla."""
    if not token:
        return
    destino = init_bd(ruta)
    resumen = hashlib.sha256(token.encode("utf-8")).hexdigest()
    conexion = _conectar(destino)
    try:
        conexion.execute(
            "DELETE FROM sesiones WHERE token_hash = ?", (resumen,)
        )
        conexion.commit()
    finally:
        conexion.close()
