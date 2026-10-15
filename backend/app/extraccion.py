"""Extracción de texto de contratos en PDF y DOCX.

Cubre los requisitos de ``docs/requisitos.md``:

- RF-01.1 / RF-01.2 — aceptar PDF con texto seleccionable y DOCX.
- RF-01.3        — rechazar formatos no soportados con mensaje claro.
- RF-01.4        — validar un tamaño máximo de archivo.
- RF-02.1 / RF-02.2 — extraer el texto completo del documento.
- RF-02.3 / RF-02.4 — si la extracción falla o resulta incompleta, notificar
  con un mensaje claro y **detener el análisis**.
- RPJ-06         — no presentar resultados como si se hubiera leído el
  documento completo.

Regla de diseño central de este módulo
-------------------------------------
Cuando la extracción no puede completarse, la función **no devuelve texto
parcial**. Devuelve ``ok=False`` con ``texto=""`` y un ``motivo`` legible.
Así el módulo de análisis no puede continuar con información incompleta
(RF-02.4) ni simular haber leído el documento (RPJ-06).

Criterio de "extracción incompleta"
-----------------------------------
Un PDF se considera incompleto si declara N páginas y alguna de ellas no
aporta texto. Es el comportamiento que pide el caso CG-02 del plan de
pruebas. El umbral por página es configurable mediante
``MIN_CARACTERES_POR_PAGINA``; cambiarlo es una decisión de producto, no un
detalle de implementación, y por eso queda explícita y documentada.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Formato = Literal["pdf", "docx"]

#: Extensiones aceptadas (RF-01.1, RF-01.2).
EXTENSIONES_SOPORTADAS: dict[str, Formato] = {
    ".pdf": "pdf",
    ".docx": "docx",
}

#: Tamaño máximo aceptado, 10 MB (RF-01.4). Pendiente de confirmar.
TAMANO_MAXIMO_BYTES: int = 10 * 1024 * 1024

#: Nombres legibles de cada formato, para los mensajes al usuario.
NOMBRES_FORMATO: dict[str, str] = {
    ".pdf": "PDF",
    ".docx": "DOCX",
}


#: Mínimo de caracteres para considerar que una página tiene texto.
MIN_CARACTERES_POR_PAGINA: int = 20

#: Códigos de motivo de fallo. El frontend puede usarlos para decidir el
#: mensaje a mostrar sin interpretar cadenas de texto.
COD_FORMATO_NO_SOPORTADO = "formato_no_soportado"
COD_TAMANO_EXCEDIDO = "tamano_excedido"
COD_ARCHIVO_VACIO = "archivo_vacio"
COD_ARCHIVO_NO_LEIBLE = "archivo_no_leible"
COD_SIN_TEXTO = "sin_texto"
COD_EXTRACCION_INCOMPLETA = "extraccion_incompleta"


class ErrorExtraccion(Exception):
    """Fallo interno de extracción con un código de motivo asociado."""

    def __init__(self, codigo: str, mensaje: str) -> None:
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje


@dataclass(frozen=True)
class ResultadoExtraccion:
    """Resultado de intentar extraer el texto de un documento.

    Cuando ``ok`` es ``False``, ``texto`` siempre es la cadena vacía: nunca
    se entrega texto parcial (RF-02.4).
    """

    ok: bool
    texto: str
    formato: Formato | None
    num_paginas: int | None
    codigo: str | None
    motivo: str | None


def _resultado_fallo(codigo: str, motivo: str) -> ResultadoExtraccion:
    return ResultadoExtraccion(
        ok=False,
        texto="",
        formato=None,
        num_paginas=None,
        codigo=codigo,
        motivo=motivo,
    )


def detectar_formato(nombre_archivo: str) -> Formato:
    """Devuelve el formato a partir de la extensión del archivo.

    Lanza :class:`ErrorExtraccion` si la extensión no está soportada.
    """
    extension = Path(nombre_archivo or "").suffix.lower()
    formato = EXTENSIONES_SOPORTADAS.get(extension)
    if formato is None:
        soportados = ", ".join(
            NOMBRES_FORMATO[ext] for ext in sorted(EXTENSIONES_SOPORTADAS)
        )
        raise ErrorExtraccion(
            COD_FORMATO_NO_SOPORTADO,
            f"Formato no soportado ({extension or 'sin extensión'}). "
            f"Formatos aceptados: {soportados}.",
        )
    return formato


def _validar_tamano(contenido: bytes) -> None:
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        limite_mb = TAMANO_MAXIMO_BYTES // (1024 * 1024)
        raise ErrorExtraccion(
            COD_TAMANO_EXCEDIDO,
            f"El archivo supera el tamaño máximo permitido de {limite_mb} MB.",
        )
    if not contenido:
        raise ErrorExtraccion(
            COD_ARCHIVO_VACIO,
            "El archivo está vacío. Verifica el documento e inténtalo de nuevo.",
        )


def _extraer_pdf(contenido: bytes) -> tuple[str, int]:
    """Extrae el texto de un PDF página por página.

    Devuelve ``(texto, num_paginas)``. Lanza :class:`ErrorExtraccion` si el
    archivo no es un PDF legible, si no tiene texto o si la extracción
    quedó incompleta.
    """
    import io

    from pypdf import PdfReader

    try:
        lector = PdfReader(io.BytesIO(contenido))
        num_paginas = len(lector.pages)
    except Exception as error:  # PDF corrupto, truncado o cifrado
        raise ErrorExtraccion(
            COD_ARCHIVO_NO_LEIBLE,
            "No se pudo abrir el archivo PDF. Puede estar dañado o "
            "protegido. Verifica el documento o inténtalo con otro.",
        ) from error

    if num_paginas == 0:
        raise ErrorExtraccion(
            COD_ARCHIVO_NO_LEIBLE,
            "El archivo PDF no contiene páginas legibles.",
        )

    textos: list[str] = []
    paginas_sin_texto: list[int] = []

    for indice, pagina in enumerate(lector.pages, start=1):
        try:
            texto_pagina = pagina.extract_text() or ""
        except Exception as error:
            raise ErrorExtraccion(
                COD_ARCHIVO_NO_LEIBLE,
                f"No se pudo leer la página {indice} del documento.",
            ) from error

        if len(texto_pagina.strip()) < MIN_CARACTERES_POR_PAGINA:
            paginas_sin_texto.append(indice)
        textos.append(texto_pagina)

    texto = "\n".join(textos).strip()

    # Caso CG-01: PDF escaneado sin capa de texto.
    if not texto:
        raise ErrorExtraccion(
            COD_SIN_TEXTO,
            "No se pudo extraer texto del documento. Si es un PDF, "
            "verifica que tenga texto seleccionable y no sea una imagen "
            "escaneada, o inténtalo con otro archivo.",
        )

    # Caso CG-02: extracción parcial. Se detiene; no se devuelve texto parcial.
    if paginas_sin_texto:
        detalle = ", ".join(str(p) for p in paginas_sin_texto)
        total = len(paginas_sin_texto)
        raise ErrorExtraccion(
            COD_EXTRACCION_INCOMPLETA,
            f"La extracción resultó incompleta: {total} de {num_paginas} "
            f"páginas no contienen texto seleccionable (páginas {detalle}). "
            "El análisis se detuvo para no emitir hallazgos basados en una "
            "lectura parcial. Verifica el archivo o inténtalo con otro.",
        )

    return texto, num_paginas


def _extraer_docx(contenido: bytes) -> tuple[str, int | None]:
    """Extrae párrafos y tablas de un DOCX.

    Un DOCX no expone un número fiable de páginas sin renderizarlo, por lo
    que ``num_paginas`` se devuelve como ``None``.
    """
    import io

    from docx import Document as DocumentoDocx

    try:
        documento = DocumentoDocx(io.BytesIO(contenido))
    except Exception as error:
        raise ErrorExtraccion(
            COD_ARCHIVO_NO_LEIBLE,
            "No se pudo abrir el archivo DOCX. Puede estar dañado o no ser "
            "un documento de Word válido. Verifica el archivo o inténtalo "
            "con otro.",
        ) from error

    fragmentos: list[str] = []

    for parrafo in documento.paragraphs:
        if parrafo.text and parrafo.text.strip():
            fragmentos.append(parrafo.text)

    # Las tablas forman parte del contenido contractual (montos, plazos).
    for tabla in documento.tables:
        for fila in tabla.rows:
            celdas = [
                celda.text.strip()
                for celda in fila.cells
                if celda.text and celda.text.strip()
            ]
            if celdas:
                fragmentos.append(" | ".join(celdas))

    texto = "\n".join(fragmentos).strip()

    if not texto:
        raise ErrorExtraccion(
            COD_SIN_TEXTO,
            "No se pudo extraer texto del documento. El archivo no contiene "
            "texto legible. Verifica el documento o inténtalo con otro.",
        )

    return texto, None


def extraer_texto(nombre_archivo: str, contenido: bytes) -> ResultadoExtraccion:
    """Extrae el texto de un PDF o DOCX.

    Args:
        nombre_archivo: nombre original, usado para validar la extensión.
        contenido: bytes completos del archivo.

    Returns:
        :class:`ResultadoExtraccion`. Si ``ok`` es ``False``, ``texto`` es la
        cadena vacía y ``motivo`` explica el fallo en español (RF-02.3).
    """
    try:
        formato = detectar_formato(nombre_archivo)
        _validar_tamano(contenido)

        if formato == "pdf":
            texto, num_paginas = _extraer_pdf(contenido)
        else:
            texto, num_paginas = _extraer_docx(contenido)

        return ResultadoExtraccion(
            ok=True,
            texto=texto,
            formato=formato,
            num_paginas=num_paginas,
            codigo=None,
            motivo=None,
        )

    except ErrorExtraccion as error:
        return _resultado_fallo(error.codigo, error.mensaje)
    except Exception:  # noqa: BLE001 — ningún error escapa sin control
        # No se registra el contenido del documento en logs (RNF-03.3).
        return _resultado_fallo(
            COD_ARCHIVO_NO_LEIBLE,
            "Ocurrió un error inesperado al procesar el archivo. "
            "Verifica el documento o inténtalo con otro.",
        )


def extraer_texto_desde_ruta(ruta: str | Path) -> ResultadoExtraccion:
    """Conveniencia para uso interno y pruebas: extrae desde una ruta local."""
    ruta = Path(ruta)
    return extraer_texto(ruta.name, ruta.read_bytes())
