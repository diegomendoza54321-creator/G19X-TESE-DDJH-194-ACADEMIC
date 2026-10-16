"""Clasificación determinista y local del tipo de contrato (RF-03).

Clasifica entre "prestación de servicios" y "contrato de proveedor" usando
únicamente señales textuales del propio documento extraído. No usa IA, no
envía texto a terceros, no guarda contratos y no aplica criterios jurídicos.

Cada tipo define señales textuales. El algoritmo busca esas señales
(literalmente, sin distinguir mayúsculas) en el texto y puntúa cada tipo:
las señales principales pesan el doble que las secundarias.

Resultado:
- tipo ``None`` cuando no hay señal suficiente para decidir.
- confianza ``alta`` cuando un tipo suma suficientes puntos y supera al otro.
- confianza ``baja`` cuando las señales son débiles, ambiguas o divididas;
  el sistema lo indica y pide revisión manual, sin fingir certeza.

Cada evidencia devuelta es un fragmento literal del texto, por lo que
siempre existe en el documento analizado (RF-03.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TipoContrato = Literal["prestacion_de_servicios", "proveedor"]

ETIQUETAS: dict[TipoContrato, str] = {
    "prestacion_de_servicios": "Prestación de servicios",
    "proveedor": "Contrato de proveedor",
}

OPCIONES_TIPO: list[dict[str, str]] = [
    {"id": "prestacion_de_servicios", "etiqueta": "Prestación de servicios"},
    {"id": "proveedor", "etiqueta": "Contrato de proveedor"},
]

# Señales textuales por tipo. Se busca cada una literalmente en el texto
# (búsqueda sin distinguir mayúsculas). Las principales pesan el doble.
_SENALES: dict[TipoContrato, dict[str, list[str]]] = {
    "prestacion_de_servicios": {
        "principales": [
            "prestación de servicios",
            "prestacion de servicios",
            "contrato de prestación de servicios",
            "contrato de prestacion de servicios",
        ],
        "secundarias": [
            "prestador de servicios",
            "el prestador",
            "prestará los servicios",
            "prestara los servicios",
            "servicios profesionales",
            "objeto del contrato de prestación",
            "objeto del contrato de prestacion",
        ],
    },
    "proveedor": {
        "principales": [
            "contrato de proveedor",
            "contrato de suministro",
            "suministro con proveedor",
        ],
        "secundarias": [
            "el proveedor",
            "proveedor de bienes",
            "entrega de los bienes",
            "materiales",
            "penalizaciones",
            "anexo 1",
        ],
    },
}

_PUNTAJE_PRINCIPAL = 2
_PUNTAJE_SECUNDARIO = 1
_PUNTAJE_MINIMO_CLARO = 2


@dataclass(frozen=True)
class ResultadoClasificacion:
    """Resultado de la clasificación local y determinista (RF-03.1, RF-03.2).

    ``tipo`` es ``None`` cuando no hay suficiente señal para decidir.
    ``confianza`` es ``"alta"`` solo cuando un tipo supera claramente al otro;
    en cualquier otro caso es ``"baja"`` y se pide revisión manual.
    """

    tipo: TipoContrato | None
    confianza: Literal["alta", "baja"]
    evidencias: list[str]
    motivo: str | None


def _fragmento_literal(texto: str, senal: str, ventana: int = 70) -> str:
    """Devuelve un fragmento literal de ``texto`` alrededor de ``senal``.

    La búsqueda no distingue mayúsculas, pero el fragmento devuelto conserva
    el texto original del documento, así que existe literalmente en él.
    """
    indice = texto.lower().find(senal.lower())
    if indice == -1:
        return ""
    inicio = max(0, indice - ventana // 2)
    fin = min(len(texto), indice + len(senal) + ventana // 2)
    return texto[inicio:fin].strip()


def _contar_senales(
    texto: str, tipo: TipoContrato
) -> tuple[int, list[str]]:
    """Devuelve (puntaje ponderado, evidencias literales encontradas)."""
    puntaje = 0
    evidencias: list[str] = []
    for grupo, peso in (
        ("principales", _PUNTAJE_PRINCIPAL),
        ("secundarias", _PUNTAJE_SECUNDARIO),
    ):
        for senal in _SENALES[tipo][grupo]:
            if senal.lower() in texto.lower():
                puntaje += peso
                evidencia = _fragmento_literal(texto, senal)
                if evidencia:
                    evidencias.append(evidencia)
    return puntaje, evidencias


def clasificar_tipo_contrato(texto: str) -> ResultadoClasificacion:
    """Clasifica el texto extraído en uno de los dos tipos de contrato.

    La decisión es determinista: mismo texto siempre da mismo resultado.
    Nunca devuelve certeza fingida: si las señales son débiles, la confianza
    es ``"baja"`` y ``tipo`` puede ser ``None`` (RF-03.2).
    """
    puntajes: dict[TipoContrato, int] = {}
    evidencias_por_tipo: dict[TipoContrato, list[str]] = {}
    tipos: list[TipoContrato] = [
        "prestacion_de_servicios",
        "proveedor",
    ]
    for tipo in tipos:
        puntaje, evidencias = _contar_senales(texto, tipo)
        puntajes[tipo] = puntaje
        evidencias_por_tipo[tipo] = evidencias

    mejor_tipo = max(tipos, key=lambda t: puntajes[t])
    mejor_puntaje = puntajes[mejor_tipo]
    otro_tipo = (
        "proveedor" if mejor_tipo == "prestacion_de_servicios"
        else "prestacion_de_servicios"
    )
    otro_puntaje = puntajes[otro_tipo]

    if mejor_puntaje == 0:
        return ResultadoClasificacion(
            tipo=None,
            confianza="baja",
            evidencias=[],
            motivo=(
                "No se identificaron señales textuales de ninguno de los dos "
                "tipos de contrato conocidos (prestación de servicios o "
                "contrato de proveedor). Confirme el tipo manualmente."
            ),
        )

    if (
        mejor_puntaje >= _PUNTAJE_MINIMO_CLARO
        and mejor_puntaje > otro_puntaje
    ):
        return ResultadoClasificacion(
            tipo=mejor_tipo,
            confianza="alta",
            evidencias=evidencias_por_tipo[mejor_tipo],
            motivo=None,
        )

    # Señales débiles, ambiguas o divididas entre los dos tipos: no se
    # impone una decisión; se propone el tipo con más puntos (si lo hay)
    # con confianza baja y se pide revisión manual.
    tipo_propuesto = mejor_tipo if mejor_puntaje > otro_puntaje else None
    return ResultadoClasificacion(
        tipo=tipo_propuesto,
        confianza="baja",
        evidencias=evidencias_por_tipo[mejor_tipo] if mejor_puntaje > 0 else [],
        motivo=(
            "Las señales textuales son débiles o ambiguas. Confirme o corrija "
            "el tipo de contrato antes de continuar."
        ),
    )