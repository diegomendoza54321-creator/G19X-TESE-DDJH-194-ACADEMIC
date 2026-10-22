"""API del backend — autenticación privada, carga y extracción de texto.

Endpoints
---------
``GET  /salud``         — comprobación de que el servicio está levantado (público).
``POST /login``         — inicia sesión con usuario y contraseña (RF-00.1).
``POST /logout``        — cierra la sesión actual (requiere sesión).
``GET  /yo``            — devuelve el usuario de la sesión (requiere sesión).
``POST /extraer``       — recibe un PDF o DOCX y devuelve el texto extraído
(requiere sesión, RF-00.1).
``POST /clasificar``    — propone el tipo de contrato del texto extraído de
forma local y determinista (requiere sesión, RF-03).
``POST /analizar-con-ia`` — analiza las cláusulas con IA local
(requiere sesión, RF-04, prototipo).
``GET  /analizar-con-ia/estado`` — ocupación del análisis local
(requiere sesión).

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
* **Análisis local con IA (RF-04, prototipo).** ``POST /analizar-con-ia``
  llama solo al servidor local en 127.0.0.1:9931, nunca a servicios
  externos. Toda cita se valida literalmente con ``app.citas``: lo que
  no existe en el texto se descarta y no llega al informe (RPJ-02).
* **Clasificación local (RF-03).** ``POST /clasificar`` usa el módulo
  ``app.clasificacion``: señales textuales del propio documento, sin IA,
  sin envío a terceros y sin guardar el contrato. La confianza baja se
  comunica sin fingir certeza.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import sqlite3

from fastapi import Cookie, FastAPI, File, Form, Response, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import auth
from .analisis_ia import (
    ErrorAnalisis,
    analizar_con_ia,
    consultar_ocupacion,
)
from .auth import NOMBRE_COOKIE, obtener_usuario_id_por_token, ruta_bd
from .clasificacion import ETIQUETAS, clasificar_tipo_contrato
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


class RespuestaAnalisis(BaseModel):
    """Cuerpo de respuesta de ``POST /analizar-con-ia``."""

    ok: bool
    hallazgos: list[dict] | None = None
    num_descartados: int = 0
    codigo: str | None = None
    motivo: str | None = None


class SolicitudAnalisis(BaseModel):
    """Cuerpo de la solicitud de ``POST /analizar-con-ia``."""

    texto: str
    tipo_confirmado: str


class RespuestaEstadoAnalisis(BaseModel):
    """Cuerpo de respuesta de ``GET /analizar-con-ia/estado``."""

    ocupado: bool
    fuente: str


class SolicitudClasificacion(BaseModel):
    """Cuerpo de la solicitud de ``POST /clasificar``."""

    texto: str


class RespuestaClasificacion(BaseModel):
    """Cuerpo de la respuesta de ``POST /clasificar`` (RF-03)."""

    ok: bool
    tipo: str | None = None
    etiqueta: str | None = None
    confianza: str | None = None
    evidencias: list[str] | None = None
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


@app.post("/clasificar")
def clasificar(
    solicitud: SolicitudClasificacion,
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Propone el tipo de contrato del texto extraído (RF-03).

    Requiere sesión (RF-00.1). Clasifica entre "prestación de servicios" y
    "contrato de proveedor" con señales textuales del propio documento:
    sin IA, sin enviar texto a terceros y sin guardar el contrato. Cuando
    las señales son débiles o ambiguas la confianza es baja y se pide
    revisión manual, sin fingir certeza.
    """
    if _usuario_de_sesion(sesion_mrl) is None:
        return _error_no_autenticado()

    texto = solicitud.texto or ""
    resultado = clasificar_tipo_contrato(texto)

    return JSONResponse(
        status_code=200,
        content=RespuestaClasificacion(
            ok=True,
            tipo=resultado.tipo,
            etiqueta=ETIQUETAS[resultado.tipo] if resultado.tipo else None,
            confianza=resultado.confianza,
            evidencias=resultado.evidencias or None,
            motivo=resultado.motivo,
        ).model_dump(),
    )


@app.get("/analizar-con-ia/estado")
async def estado_analisis(
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Devuelve si el análisis local está ocupado (requiere sesión).

    ``ocupado`` es ``True`` si el lock global del backend está tomado o
    si algún slot del servidor local tiene ``is_processing=true``. Si
    ``/slots`` no puede consultarse ni validarse estrictamente, se
    responde ocupado con ``fuente="desconocida"`` (fail-safe).
    """
    if _usuario_de_sesion(sesion_mrl) is None:
        return _error_no_autenticado()
    ocupado, fuente = await consultar_ocupacion()
    return JSONResponse(
        status_code=200,
        content=RespuestaEstadoAnalisis(
            ocupado=ocupado, fuente=fuente
        ).model_dump(),
    )


def _hallazgo_a_dict(hallazgo) -> dict:
    return {
        "tipo": hallazgo.tipo,
        "categoria": hallazgo.categoria,
        "descripcion": hallazgo.descripcion,
        "cita": hallazgo.cita,
        "explicacion": hallazgo.explicacion,
        "consecuencia": hallazgo.consecuencia,
        "recomendacion": hallazgo.recomendacion,
        "limitaciones": hallazgo.limitaciones,
    }


@app.post("/analizar-con-ia")
async def analizar_ia(
    solicitud: SolicitudAnalisis,
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Analiza las cláusulas con IA local (RF-04, prototipo).

    Requiere sesión (RF-00.1) y tipo confirmado (RF-03.5 exigible en
    backend: sin tipo válido no hay análisis). El texto va solo al
    servidor local en 127.0.0.1:9931, nunca a servicios externos.
    Toda cita se valida literalmente con ``app.citas``: lo descartado
    no llega al informe (RPJ-02).
    """
    if _usuario_de_sesion(sesion_mrl) is None:
        return _error_no_autenticado()

    usuario_id = obtener_usuario_id_por_token(sesion_mrl)
    if usuario_id is None:
        return _error_no_autenticado()

    texto = solicitud.texto or ""
    if not texto.strip():
        return JSONResponse(
            status_code=422,
            content=RespuestaAnalisis(
                ok=False,
                codigo="texto_vacio",
                motivo="No hay texto para analizar. Extraiga primero el "
                "texto del contrato.",
            ).model_dump(),
        )
    if solicitud.tipo_confirmado not in ETIQUETAS:
        return JSONResponse(
            status_code=422,
            content=RespuestaAnalisis(
                ok=False,
                codigo="tipo_no_confirmado",
                motivo="Confirme el tipo de contrato antes de analizar.",
            ).model_dump(),
        )

    try:
        resultado = await analizar_con_ia(texto, solicitud.tipo_confirmado)
    except ErrorAnalisis as error:
        return JSONResponse(
            status_code=error.estado_http,
            content=RespuestaAnalisis(
                ok=False,
                codigo=error.codigo,
                motivo=error.motivo,
            ).model_dump(),
        )

    hallazgos_dicts = [_hallazgo_a_dict(h) for h in resultado.hallazgos]
    _guardar_analisis(
        usuario_id=usuario_id,
        tipo_confirmado=solicitud.tipo_confirmado,
        hallazgos=hallazgos_dicts,
    )

    return JSONResponse(
        status_code=200,
        content=RespuestaAnalisis(
            ok=True,
            hallazgos=hallazgos_dicts,
            num_descartados=resultado.num_descartados,
        ).model_dump(),
    )


def _guardar_analisis(
    *, usuario_id: int, tipo_confirmado: str, hallazgos: list[dict]
) -> None:
    """Persiste metadatos y hallazgos de un analisis (sin texto del contrato).

    Se llama solo despues de validar las citas y completar el analisis con
    exito. Nunca se guarda el texto del contrato, el prompt ni el archivo.
    """
    destino = ruta_bd()
    auth.init_bd(destino)
    conexion = sqlite3.connect(str(destino))
    conexion.row_factory = sqlite3.Row
    try:
        conexion.execute(
            "INSERT INTO analisis (usuario_id, fecha, tipo_confirmado, "
            "num_hallazgos, hallazgos) VALUES (?, ?, ?, ?, ?)",
            (
                usuario_id,
                datetime.now(timezone.utc).isoformat(),
                tipo_confirmado,
                len(hallazgos),
                json.dumps(hallazgos, ensure_ascii=False),
            ),
        )
        conexion.commit()
    finally:
        conexion.close()


@app.get("/historial")
def historial(
    sesion_mrl: str | None = Cookie(default=None, alias=NOMBRE_COOKIE),
) -> JSONResponse:
    """Devuelve los analisis del usuario autenticado, mas reciente primero.

    Nunca acepta un usuario_id del cliente: se deriva unicamente de la
    sesion activa (cookie HttpOnly).
    """
    if _usuario_de_sesion(sesion_mrl) is None:
        return _error_no_autenticado()

    usuario_id = obtener_usuario_id_por_token(sesion_mrl)
    if usuario_id is None:
        return _error_no_autenticado()

    destino = ruta_bd()
    auth.init_bd(destino)
    conexion = sqlite3.connect(str(destino))
    conexion.row_factory = sqlite3.Row
    try:
        filas = conexion.execute(
            "SELECT id, fecha, tipo_confirmado, num_hallazgos, hallazgos "
            "FROM analisis WHERE usuario_id = ? "
            "ORDER BY fecha DESC, id DESC",
            (usuario_id,),
        ).fetchall()
    finally:
        conexion.close()

    registros = []
    for fila in filas:
        registros.append(
            {
                "id": fila["id"],
                "fecha": fila["fecha"],
                "tipo_confirmado": fila["tipo_confirmado"],
                "num_hallazgos": fila["num_hallazgos"],
                "hallazgos": json.loads(fila["hallazgos"]),
            }
        )

    return JSONResponse(
        status_code=200,
        content={"ok": True, "registros": registros},
    )
