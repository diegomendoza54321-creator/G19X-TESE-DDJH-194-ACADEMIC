"""Análisis de cláusulas con IA local (RF-04, prototipo).

Llama al servidor local llama.cpp en ``http://127.0.0.1:9931`` (loopback,
sin red externa). No usa servicios de terceros, no guarda contratos y no
registra el texto en logs (RNF-03.3).
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

# Tupla compartida de excepciones de conexión para consistencia en el manejo de errores.
# Usada por _contar_prompt y _analizar_bajo_lock; el bloque A de verificación de /slots
# usa su propia firma porque devuelve (True, "desconocida").
EXCEPCIONES_CONEXION = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.ReadTimeout,
)

from .citas import Hallazgo, filtrar_hallazgos
from .clasificacion import ETIQUETAS

#: Nombre de la variable de entorno para la URL del servidor local de IA.
URL_SERVIDOR_IA_ENV = "URL_SERVIDOR_IA"

#: Nombre de la variable de entorno para el límite de contexto.
LIMITE_CONTEXTO_IA_ENV = "LIMITE_CONTEXTO_IA"

#: Valor predeterminado de la URL del servidor local de IA.
_URL_SERVIDOR_LOCAL_POR_DEFECTO = "http://127.0.0.1:9931"

#: Valor predeterminado del límite de contexto.
_LIMITE_CONTEXTO_POR_DEFECTO = 2048


def _validar_host_local(url: str) -> None:
    """Rechaza URLs cuyo host no sea ``127.0.0.1`` ni ``localhost``.

    Mantiene la conexión estrictamente local: nunca apunta a un
    servicio externo (RNF-03.4).
    """
    host = urlparse(url).hostname
    if host not in ("127.0.0.1", "localhost"):
        raise ValueError(
            f"El servidor local de IA debe estar en loopback. "
            f"Host no permitido: {host}"
        )


def _leer_url_servidor_local() -> str:
    """Lee la URL del servidor local de IA desde el entorno.

    Usa ``http://127.0.0.1:9931`` como valor predeterminado.
    """
    url = os.environ.get(URL_SERVIDOR_IA_ENV, _URL_SERVIDOR_LOCAL_POR_DEFECTO)
    _validar_host_local(url)
    return url


def _leer_limite_contexto() -> int:
    """Lee el límite de contexto desde el entorno.

    Usa ``2048`` como valor predeterminado. Debe ser un entero positivo.
    """
    valor = os.environ.get(LIMITE_CONTEXTO_IA_ENV, str(_LIMITE_CONTEXTO_POR_DEFECTO))
    try:
        n = int(valor)
    except (TypeError, ValueError):
        raise ValueError(
            f"LIMITE_CONTEXTO_IA debe ser un entero positivo, "
            f"se recibió: {valor!r}"
        )
    if n <= 0:
        raise ValueError(
            f"LIMITE_CONTEXTO_IA debe ser un entero positivo, "
            f"se recibió: {n}"
        )
    return n


#: Servidor local de inferencia. Se lee de la variable de entorno
#: ``URL_SERVIDOR_IA`` (predeterminado: ``http://127.0.0.1:9931``).
#: Nunca apunta a un servicio externo (RNF-03.4).
URL_SERVIDOR_LOCAL = _leer_url_servidor_local()

#: Contexto efectivo del servidor en marcha. Se lee de la variable de
#: entorno ``LIMITE_CONTEXTO_IA`` (predeterminado: ``2048``).
N_CTX = _leer_limite_contexto()

#: Reserva de tokens para la respuesta del modelo.
MAX_TOKENS_SALIDA = 512

#: Margen para BOS/EOS que el servidor inserta al inferir y desviación
#: del tokenizador. Pesimista a propósito hasta medirlo en vivo.
MARGEN_TOKENS = 32

#: Un solo vuelo a la vez desde este backend (un proceso uvicorn en el
#: prototipo; con N workers el lock es por proceso y se documenta).
_LOCK_ANALISIS = asyncio.Lock()


class ErrorAnalisis(Exception):
    """Error tipado del análisis con código y estado HTTP."""

    def __init__(self, codigo: str, motivo: str, estado_http: int) -> None:
        super().__init__(motivo)
        self.codigo = codigo
        self.motivo = motivo
        self.estado_http = estado_http


def _error(codigo: str, motivo: str, estado_http: int) -> ErrorAnalisis:
    return ErrorAnalisis(codigo, motivo, estado_http)

def _es_lista_slots_valida(cuerpo: object) -> list | None:
    """Extrae la lista de slots si la forma es conocida, o ``None``.

    Formas aceptadas sobre el JSON crudo: lista directa ``[...]`` u
    objeto envolvente reconocido ``{"slots": [...]}``. Cualquier otra
    forma es desconocida y falla de manera segura (devuelve ``None``).
    """
    if isinstance(cuerpo, list):
        return cuerpo
    if isinstance(cuerpo, dict) and set(cuerpo.keys()) == {"slots"}:
        valor = cuerpo["slots"]
        return valor if isinstance(valor, list) else None
    return None


def _validar_slots_estricto(cuerpo: object) -> bool:
    """Devuelve ``True`` si algún slot está procesando.

    Exige lista no vacía donde **cada** elemento sea un dict con
    ``is_processing`` booleano exacto. Ante lo primero desconocido
    (lista vacía, no-dict, clave ausente, no-booleano) lanza
    ``ValueError``: el llamante debe fallar de forma segura.
    """
    lista = _es_lista_slots_valida(cuerpo)
    if lista is None or len(lista) == 0:
        raise ValueError("Respuesta de /slots con forma desconocida o vacía.")
    ocupado = False
    for elemento in lista:
        if not isinstance(elemento, dict):
            raise ValueError("Elemento de /slots no es objeto.")
        if "is_processing" not in elemento:
            raise ValueError("Elemento de /slots sin is_processing.")
        valor = elemento["is_processing"]
        if type(valor) is not bool:
            raise ValueError("is_processing no es booleano.")
        if valor is True:
            ocupado = True
    return ocupado


async def consultar_ocupacion() -> tuple[bool, str]:
    """Consulta ``GET /slots`` y devuelve ``(ocupado, fuente)``.

    ``fuente`` es ``"slots"`` cuando la respuesta se validó
    estrictamente, o ``"desconocida"`` cuando no se pudo consultar o
    validar (entonces ``ocupado`` es ``True`` pesimista).
    """
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=3.0, read=10.0, write=10.0, pool=5.0)
        ) as cliente:
            respuesta = await cliente.get(f"{URL_SERVIDOR_LOCAL}/slots")
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.WriteTimeout,
            httpx.PoolTimeout, httpx.ReadTimeout):
        return True, "desconocida"
    if respuesta.status_code != 200:
        return True, "desconocida"
    try:
        cuerpo = respuesta.json()
    except ValueError:
        return True, "desconocida"
    try:
        ocupado_slots = _validar_slots_estricto(cuerpo)
    except ValueError:
        return True, "desconocida"
    ocupado = _LOCK_ANALISIS.locked() or ocupado_slots
    return ocupado, "slots"

#: Ruta del archivo de criterios de revision por tipo de contrato.
_RUTA_CRITERIOS = Path(__file__).with_name("criterios.json")


def _cargar_criterios() -> dict[str, list[str]]:
    """Lee los criterios de revision desde ``criterios.json``.

    Si el archivo no se puede leer o no contiene un objeto JSON, la
    excepcion se propaga (no se oculta). El llamador decide como manejar
    la ausencia de criterios para un tipo concreto.
    """
    with _RUTA_CRITERIOS.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, dict):
        raise ValueError(
            "criterios.json debe contener un objeto JSON con tipos de contrato."
        )
    return datos


def construir_mensajes(texto: str, tipo_confirmado: str) -> list[dict]:
    """Construye ``messages[]`` con un solo mensaje de usuario.

    La plantilla Phi-3 de la build b11683 no admite rol ``system`` ni
    herramientas, así que toda la instrucción va en el mensaje ``user``.
    """
    etiqueta = ETIQUETAS[tipo_confirmado]  # type: ignore[index]
    # Criterios de revision correspondientes al tipo confirmado. Si el
    # tipo no tiene criterios configurados (o la lista esta vacia), no se
    # incluyen criterios en el prompt; el analisis continua sin guia
    # adicional. Si el archivo no se puede leer, la excepcion se propaga
    # (no se oculta el error) y no se cambia la clasificacion.
    criterios_datos = _cargar_criterios()
    criterios_tipo = criterios_datos.get(tipo_confirmado)
    if not isinstance(criterios_tipo, list):
        criterios_tipo = []
    criterios_texto = ""
    if criterios_tipo:
        criterios_texto = (
            "CRITERIOS DE REVISION (guia no exhaustiva, no es asesoria "
            "juridica) para el tipo confirmado: "
            + "; ".join(str(c) for c in criterios_tipo)
            + ". "
        )

    instruccion = (
        "Analizas un contrato sintético de prueba. Tipo confirmado: "
        f"{etiqueta}. Devuelve SOLO un array JSON, sin texto adicional, "
        "con objetos de la forma "
        '{"tipo": "ambiguedad|omision|contradiccion|riesgo", '
        '"categoria": "texto breve", '
        '"descripcion": "qué se detectó", '
        '"cita": "fragmento literal del texto, mínimo 20 caracteres; '
        'cadena vacía solo si es omisión", '
        '"explicacion": "por qué se marca, sin afirmar certeza jurídica", '
        '"consecuencia": "posible consecuencia genérica, prudente y no '
        "vinculante\", "
        '"recomendacion": "recomendación genérica de revisión, no '
        "vinculante\", "
        '"limitaciones": "qué no puede afirmar el sistema"}. '
        "Cada coincidencia es una señal para revisar, no una conclusión "
        "jurídica. No afirmes validez ni legalidad. "
        + criterios_texto
        + "Usa los criterios como guía para revisar el texto, pero no "
        "afirmes incumplimientos ni conclusiones legales; no inventes "
        "hechos ni citas; incluye solo citas literales presentes en el "
        "contrato; conserva el formato de respuesta JSON indicado. "
        "TEXTO DEL CONTRATO (sintético):\n" + texto
    )
    return [{"role": "user", "content": instruccion}]


def _extraer_contenido_respuesta(cuerpo: object) -> str:
    """Extrae el texto generado del cuerpo OpenAI-compatible."""
    if not isinstance(cuerpo, dict):
        raise ValueError("Respuesta no es objeto.")
    opciones = cuerpo.get("choices")
    if not isinstance(opciones, list) or len(opciones) == 0:
        raise ValueError("Sin choices.")
    primera = opciones[0]
    if not isinstance(primera, dict):
        raise ValueError("Choice no es objeto.")
    mensaje = primera.get("message")
    if not isinstance(mensaje, dict):
        raise ValueError("Sin message.")
    contenido = mensaje.get("content")
    if not isinstance(contenido, str) or not contenido.strip():
        raise ValueError("Sin content.")
    return contenido


def _parsear_hallazgos_json(texto_json: str) -> list:
    """Parsea el array JSON del modelo, tolerando cercas markdown."""
    limpio = texto_json.strip()
    if limpio.startswith("```"):
        lineas = limpio.splitlines()[1:]
        if lineas and lineas[-1].strip().startswith("```"):
            lineas = lineas[:-1]
        limpio = "\n".join(lineas).strip()
    datos = json.loads(limpio)
    if not isinstance(datos, list):
        raise ValueError("La respuesta no es un array JSON.")
    return datos


_TIPOS_VALIDOS: frozenset = frozenset(
    {"ambiguedad", "omision", "contradiccion", "riesgo"}
)


def _convertir_hallazgo(item: object) -> Hallazgo | None:
    """Convierte un objeto del modelo a :class:`Hallazgo`, o ``None``."""
    if not isinstance(item, dict):
        return None
    if item.get("tipo") not in _TIPOS_VALIDOS:
        return None
    for clave in (
        "categoria", "descripcion", "explicacion", "consecuencia",
        "recomendacion", "limitaciones",
    ):
        if not isinstance(item.get(clave), str):
            return None
    cita = item.get("cita", "")
    if not isinstance(cita, str):
        return None
    return Hallazgo(
        tipo=item["tipo"],
        categoria=item["categoria"],
        descripcion=item["descripcion"],
        cita=cita,
        explicacion=item["explicacion"],
        consecuencia=item["consecuencia"],
        recomendacion=item["recomendacion"],
        limitaciones=item["limitaciones"],
    )

@dataclass(frozen=True)
class ResultadoAnalisisIA:
    """Hallazgos válidos tras la verificación literal de citas."""

    hallazgos: tuple = ()
    num_descartados: int = 0


async def _contar_prompt(
    mensajes: list[dict], cliente_aux: httpx.AsyncClient
) -> int:
    """Renderiza con /apply-template y cuenta con /tokenize."""
    motivo_ctx = (
        "No se pudo verificar que el texto quepa en el contexto local "
        "(2048). No se analiza para evitar truncar o analizar solo una "
        "parte."
    )
    try:
        r_plantilla = await cliente_aux.post(
            f"{URL_SERVIDOR_LOCAL}/apply-template", json={"messages": mensajes}
        )
    except EXCEPCIONES_CONEXION:
        raise _error(
            "modelo_no_disponible",
            "No se pudo conectar con el servidor local de análisis.",
            503,
        )
    if r_plantilla.status_code == 404:
        raise _error("contexto_no_verificable", motivo_ctx, 422)
    if r_plantilla.status_code != 200:
        raise _error(
            "modelo_no_disponible",
            "El servidor local de análisis no responde correctamente.",
            503,
        )
    try:
        cuerpo_plantilla = r_plantilla.json()
    except ValueError:
        raise _error("contexto_no_verificable", motivo_ctx, 422)
    if isinstance(cuerpo_plantilla, dict) and isinstance(
        cuerpo_plantilla.get("prompt"), str
    ):
        prompt = cuerpo_plantilla["prompt"]
    elif isinstance(cuerpo_plantilla, str):
        prompt = cuerpo_plantilla
    else:
        raise _error("contexto_no_verificable", motivo_ctx, 422)
    try:
        r_tokens = await cliente_aux.post(
            f"{URL_SERVIDOR_LOCAL}/tokenize",
            json={"content": prompt, "add_special": False},
        )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.WriteTimeout,
            httpx.PoolTimeout, httpx.ReadTimeout):
        raise _error(
            "modelo_no_disponible",
            "No se pudo conectar con el servidor local de análisis.",
            503,
        )
    if r_tokens.status_code == 404:
        raise _error("contexto_no_verificable", motivo_ctx, 422)
    if r_tokens.status_code != 200:
        raise _error(
            "modelo_no_disponible",
            "El servidor local de análisis no responde correctamente.",
            503,
        )
    try:
        cuerpo_tokens = r_tokens.json()
    except ValueError:
        raise _error("contexto_no_verificable", motivo_ctx, 422)
    if isinstance(cuerpo_tokens, dict) and isinstance(
        cuerpo_tokens.get("tokens"), list
    ):
        return len(cuerpo_tokens["tokens"])
    if isinstance(cuerpo_tokens, list):
        return len(cuerpo_tokens)
    raise _error("contexto_no_verificable", motivo_ctx, 422)

async def _analizar_bajo_lock(
    texto: str, tipo_confirmado: str
) -> ResultadoAnalisisIA:
    """Pre-chequeo de slots, conteo, inferencia y filtrado literal."""
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=3.0, read=10.0, write=10.0, pool=5.0)
        ) as cliente_slots:
            r_slots = await cliente_slots.get(f"{URL_SERVIDOR_LOCAL}/slots")
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.WriteTimeout,
            httpx.PoolTimeout, httpx.ReadTimeout):
        raise _error(
            "modelo_no_disponible",
            "No se pudo conectar con el servidor local de análisis.",
            503,
        )
    if r_slots.status_code != 200:
        raise _error(
            "modelo_no_disponible",
            "El servidor local de análisis no responde correctamente.",
            503,
        )
    try:
        cuerpo_slots = r_slots.json()
    except ValueError:
        raise _error(
            "modelo_no_disponible",
            "El servidor local de análisis devolvió una respuesta inválida.",
            503,
        )
    try:
        ocupado = _validar_slots_estricto(cuerpo_slots)
    except ValueError:
        raise _error(
            "modelo_no_disponible",
            "El servidor local de análisis devolvió un estado no "
            "verificable.",
            503,
        )
    if ocupado:
        raise _error(
            "modelo_ocupado",
            "El servidor local está procesando otro análisis. "
            "Reintente más tarde.",
            409,
        )

    mensajes = construir_mensajes(texto, tipo_confirmado)
    timeout_aux = httpx.Timeout(connect=3.0, read=10.0, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout_aux) as cliente_aux:
        n_prompt = await _contar_prompt(mensajes, cliente_aux)
    if n_prompt + MAX_TOKENS_SALIDA + MARGEN_TOKENS > N_CTX:
        raise _error(
            "contexto_excedido",
            f"El texto necesita {n_prompt} tokens de prompt más "
            f"{MAX_TOKENS_SALIDA} de salida y el contexto local es de "
            f"{N_CTX}. Use un documento sintético más corto. No se trunca "
            "ni se analiza por partes en este prototipo.",
            422,
        )

    cuerpo_inferencia = {
        "messages": mensajes,
        "temperature": 0,
        "stream": False,
        "max_tokens": MAX_TOKENS_SALIDA,
    }
    timeout_inf = httpx.Timeout(connect=5.0, write=10.0, read=330.0, pool=5.0)
    try:
        async with httpx.AsyncClient(timeout=timeout_inf) as cliente:
            r_inf = await cliente.post(
                f"{URL_SERVIDOR_LOCAL}/v1/chat/completions",
                json=cuerpo_inferencia,
            )
    except httpx.ReadTimeout:
        raise _error(
            "tiempo_excedido",
            "El análisis superó el tiempo de espera de lectura. "
            "Reintente con un texto más corto.",
            503,
        )
    except EXCEPCIONES_CONEXION:
        raise _error(
            "modelo_no_disponible",
            "No se pudo conectar con el servidor local de análisis.",
            503,
        )
    if r_inf.status_code != 200:
        raise _error(
            "modelo_no_disponible",
            "El servidor local de análisis no responde correctamente.",
            503,
        )
    try:
        cuerpo_resp = r_inf.json()
        contenido = _extraer_contenido_respuesta(cuerpo_resp)
        items = _parsear_hallazgos_json(contenido)
    except (ValueError, json.JSONDecodeError):
        raise _error(
            "respuesta_invalida",
            "El servidor local devolvió una respuesta que no pudo "
            "interpretarse como lista de hallazgos.",
            502,
        )
    hallazgos: list = []
    convertibles = 0
    for item in items:
        hallazgo = _convertir_hallazgo(item)
        if hallazgo is None:
            continue
        convertibles += 1
        hallazgos.append(hallazgo)
    if items and convertibles == 0:
        raise _error(
            "respuesta_invalida",
            "El servidor local devolvió hallazgos con formato inválido.",
            502,
        )
    filtrado = filtrar_hallazgos(hallazgos, texto)
    return ResultadoAnalisisIA(
        hallazgos=filtrado.validos,
        num_descartados=len(filtrado.descartados),
    )

async def analizar_con_ia(
    texto: str, tipo_confirmado: str
) -> ResultadoAnalisisIA:
    """Ejecuta el análisis con IA local bajo lock global no bloqueante.

    El lock se adquiere **antes** de construir el prompt, tokenizar o
    inferir, y se libera en ``finally`` en todos los caminos (éxito,
    errores, timeout total y cancelación del cliente).
    """
    if _LOCK_ANALISIS.locked():
        raise _error(
            "modelo_ocupado",
            "El servidor local está procesando otro análisis. "
            "Reintente más tarde.",
            409,
        )
    await _LOCK_ANALISIS.acquire()
    try:
        return await asyncio.wait_for(
            _analizar_bajo_lock(texto, tipo_confirmado), timeout=360.0
        )
    except asyncio.TimeoutError:
        raise _error(
            "tiempo_excedido",
            "El análisis superó el límite de 6 minutos. Reintente con un "
            "texto más corto.",
            503,
        )
    finally:
        if _LOCK_ANALISIS.locked():
            _LOCK_ANALISIS.release()





