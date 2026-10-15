"""API del backend — autenticación privada, carga y extracción de texto.

Endpoints
---------
``GET  /salud``   — comprobación de que el servicio está levantado (público).
``POST /login``   — inicia sesión con usuario y contraseña (RF-00.1).
``POST /logout``  — cierra la sesión actual (requiere sesión).
``GET  /yo``      — devuelve el usuario de la sesión (requiere sesión).
``POST /extraer`` — recibe un PDF o DOCX y devuelve el texto extraído
(requiere sesión, RF-00.1).

Decisiones de diseño
--------------------
* **Sin registro público.** No existe endpoint de alta: las cuentas se
  crean con ``backend/crear_usuario.py`` (RF-00.2, RF-00.5).
* **Mensaje genérico.** Ante credenciales incorrectas se responde siempre
  ``Usuario o contraseña incorrectos``, exista o no el usuario (RF-00.3).
* **Códigos de estado.** El cliente distingue dos clases de fallo sin
  interpretar texto: ``400`` cuando el problema es del archivo enviado
  (formato no soportado, tamaño excedido, archivo vacío) y ``422`` cuando el
  archivo se recibió pero no pudo procesarse (corrupto, sin texto o
  extracción incompleta). Sin sesión: ``401``.
* **Nunca se devuelve texto parcial.** Ante extracción incompleta la
  respuesta trae ``texto: null`` (RF-02.4, RPJ-06).
* **No se guardan los archivos originales.** La subida vive solo en memoria
  durante la extracción; nunca se escribe a disco.
* **No se registra contenido.** Los logs no incluyen el texto de los
  contratos (RNF-03.3).
* **Sin IA y sin criterios jurídicos.** Este bloque solo extrae texto.
"""

from __future__ import annotations

from fastapi import Cookie, FastAPI, File, Form, Response, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import auth
from .auth import NOMBRE_COOKIE
from .extraccion import (
    COD_ARCHIVO_NO_LEIBLE,
    COD_ARCHIVO_VACIO,
    COD_EXTRACCION_INCOMPLETA,
    COD_FORMATO_NO_SOPORTADO,
    COD_SIN_TEXTO,
    COD_TAMANO_EXCEDIDO,
    TAMANO_MAXIMO_BYTES,
    Formato,
    extraer_texto,
)

#: Fallos atribuibles al archivo enviado por el cliente.
CODIGOS_ERROR_CLIENTE = frozenset(
    {
        COD_FORMATO_NO_SOPORTADO,
        COD_TAMANO_EXCEDIDO,
        COD_ARCHIVO_VACIO,
    }
)

#: Tamaño de lectura por bloque al consumir la subida.
TAMANO_BLOQUE_LECTURA = 64 * 1024

app = FastAPI(
    title="MotorRevisionLegal — API",
    description=(
        "Revisión de cláusulas contractuales. Bloque actual: carga y "
        "extracción de texto de PDF y DOCX."
    ),
    version="0.1.0",
)


class RespuestaExtraccion(BaseModel):
    """Cuerpo de respuesta de ``POST /extraer``."""

    ok: bool
    texto: str | None = None
    formato: Formato | None = None
    num_paginas: int | None = None
    codigo: str | None = None
    motivo: str | None = None


@app.get("/salud")
def salud() -> dict[str, str]:
    """Comprobación de que el servicio responde."""
    return {"estado": "ok", "servicio": "MotorRevisionLegal"}


async def _leer_con_limite(archivo: UploadFile) -> bytes | None:
    """Lee la subida sin superar ``TAMANO_MAXIMO_BYTES``.

    Devuelve ``None`` si el archivo excede el límite, de modo que no se
    carga en memoria más datos de los permitidos (RF-01.4).
    """
    bloques: list[bytes] = []
    total = 0
    while True:
        bloque = await archivo.read(TAMANO_BLOQUE_LECTURA)
        if not bloque:
            break
        total += len(bloque)
        if total > TAMANO_MAXIMO_BYTES:
            return None
        bloques.append(bloque)
    return b"".join(bloques)


class RespuestaSesion(BaseModel):
    """Cuerpo de respuesta de ``POST /login``, ``POST /logout`` y ``GET /yo``."""

    ok: bool
    usuario: str | None = None
    codigo: str | None = None
    motivo: str | None = None


def _error_no_autenticado() -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=RespuestaSesion(
            ok=False,
            codigo=auth.COD_NO_AUTENTICADO,
            motivo=auth.MENSAJE_NO_AUTENTICADO,
        ).model_dump(),
    )


def _usuario_de_sesion(token: str | None) -> str | None:
    return auth.obtener_usuario_por_token(token)


def _fijar_cookie_sesion(respuesta: Response, token: str) -> None:
    respuesta.set_cookie(
        NOMBRE_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=int(auth.DURACION_SESION.total_seconds()),
    )


def _limpiar_cookie_sesion(respuesta: Response) -> None:
    respuesta.delete_cookie(NOMBRE_COOKIE, path="/")


@app.post("/login")
def login(
    respuesta: Response,
    usuario: str = Form(...),
    contrasena: str = Form(...),
) -> JSONResponse:
    """Inicia sesión con usuario y contraseña (RF-00.1).

    Ante credenciales incorrectas el mensaje es genérico (RF-00.3).
    """
    usuario_id = auth.comprobar_credenciales(usuario, contrasena)
    if usuario_id is None:
        return JSONResponse(
            status_code=401,
            content=RespuestaSesion(
                ok=False,
                codigo=auth.COD_CREDENCIALES_INVALIDAS,
                motivo=auth.MENSAJE_CREDENCIALES_INVALIDAS,
            ).model_dump(),
        )
    nombre = (usuario or "").strip()
    token = auth.crear_sesion(usuario_id)
    cuerpo = JSONResponse(
        status_code=200,
        content=RespuestaSesion(ok=True, usuario=nombre).model_dump(),
    )
    _fijar_cookie_sesion(cuerpo, token)
    return cuerpo


@app.post("/logout")
def logout(
    respuesta: Response,
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Cierra la sesión actual e invalida su cookie."""
    auth.cerrar_sesion(sesion_mrl)
    cuerpo = JSONResponse(
        status_code=200, content=RespuestaSesion(ok=True).model_dump()
    )
    _limpiar_cookie_sesion(cuerpo)
    return cuerpo


@app.get("/yo")
def yo(
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Devuelve el usuario de la sesión (RF-00.1)."""
    nombre = _usuario_de_sesion(sesion_mrl)
    if nombre is None:
        return _error_no_autenticado()
    return JSONResponse(
        status_code=200,
        content=RespuestaSesion(ok=True, usuario=nombre).model_dump(),
    )


@app.post("/extraer")
async def extraer(
    archivo: UploadFile = File(...),
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Extrae el texto de un PDF con texto seleccionable o de un DOCX.

    Requiere sesión (RF-00.1). Si la extracción falla o resulta incompleta,
    responde con error y ``texto: null``: el análisis no puede continuar
    (RF-02.3, RF-02.4).
    """
    if _usuario_de_sesion(sesion_mrl) is None:
        return _error_no_autenticado()

    contenido = await _leer_con_limite(archivo)

    if contenido is None:
        limite_mb = TAMANO_MAXIMO_BYTES // (1024 * 1024)
        return JSONResponse(
            status_code=400,
            content=RespuestaExtraccion(
                ok=False,
                texto=None,
                codigo=COD_TAMANO_EXCEDIDO,
                motivo=f"El archivo supera el tamaño máximo permitido de "
                f"{limite_mb} MB.",
            ).model_dump(),
        )

    nombre = archivo.filename or ""
    resultado = extraer_texto(nombre, contenido)

    if resultado.ok:
        return JSONResponse(
            status_code=200,
            content=RespuestaExtraccion(
                ok=True,
                texto=resultado.texto,
                formato=resultado.formato,
                num_paginas=resultado.num_paginas,
            ).model_dump(),
        )

    estado = 400 if resultado.codigo in CODIGOS_ERROR_CLIENTE else 422
    return JSONResponse(
        status_code=estado,
        content=RespuestaExtraccion(
            ok=False,
            texto=None,
            codigo=resultado.codigo,
            motivo=resultado.motivo,
        ).model_dump(),
    )
