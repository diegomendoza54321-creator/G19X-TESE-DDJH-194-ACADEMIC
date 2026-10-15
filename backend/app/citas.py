"""Verificación de citas textuales (RPJ-02, RF-05.2, RF-05.3).

Una cita solo se acepta si aparece **literalmente** en el texto extraído del
documento. Si no coincide, el hallazgo se marca como inválido y **no se
devuelve**, de modo que no puede llegar al informe.

Reglas que implementa (``docs/requisitos.md``):

- RPJ-02  — nunca generar, inferir ni inventar citas que no estén en el
  documento analizado.
- RF-05.2 — las citas textuales deben corresponder exactamente a fragmentos
  del documento analizado.
- RF-05.3 — el sistema no debe generar citas que no existan en el documento.

Caso particular: las omisiones
------------------------------
Los casos CC-01 y CC-02 de ``docs/plan-de-pruebas.md`` exigen que un hallazgo
por omisión **no** lleve cita, porque no hay texto que citar: inventarla
violaría RPJ-02. Por eso los hallazgos de tipo ``omision`` no requieren cita,
pero si aportan una, esa cita se verifica igual. Los demás tipos la exigen.

Decisiones de este módulo
-------------------------
1. **Se normalizan los espacios** antes de comparar. La extracción de PDF y
   DOCX inserta saltos de línea dentro de una misma cláusula, así que una
   cita copiada fielmente casi nunca coincidiría carácter a carácter. Se
   colapsan las secuencias de espacios en uno solo; **ningún carácter se
   agrega, elimina ni modifica**. El resultado se reporta en ``exacta`` para
   distinguir coincidencia estricta de coincidencia normalizada.
   *(decisión pendiente de confirmar)*
2. **Se distingue mayúsculas de minúsculas.** Cambiar la capitalización
   altera el texto: se considera cita alterada. *(pendiente de confirmar)*
3. **Longitud mínima** ``MIN_CARACTERES_CITA``. Una cita de dos caracteres
   coincidiría por azuidad y no respalda nada. *(pendiente de confirmar)*
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Literal

#: Tipos de hallazgo definidos en RF-04.3 a RF-04.6.
TipoHallazgo = Literal["ambiguedad", "omision", "contradiccion", "riesgo"]

#: Tipos que, por definición, no tienen texto que citar (CC-01, CC-02).
TIPOS_SIN_CITA: frozenset[str] = frozenset({"omision"})

#: Longitud mínima aceptada para una cita.
MIN_CARACTERES_CITA: int = 20

#: Códigos de resultado de la verificación de una cita.
COD_CITA_VALIDA = "cita_valida"
COD_CITA_VACIA = "cita_vacia"
COD_CITA_MUY_CORTA = "cita_muy_corta"
COD_CITA_NO_ENCONTRADA = "cita_no_encontrada"
COD_TEXTO_VACIO = "texto_vacio"
COD_HALLAZGO_VALIDO = "hallazgo_valido"
COD_HALLAZGO_DESCARTADO = "hallazgo_descartado"

_PATRON_ESPACIOS = re.compile(r"\s+")


def normalizar(texto: str) -> str:
    """Colapsa cualquier secuencia de espacios en un solo espacio.

    Incluye saltos de línea, tabuladores y espacios duros. No altera ningún
    otro carácter, por lo que el texto sigue siendo literal.
    """
    return _PATRON_ESPACIOS.sub(" ", texto or "").strip()


@dataclass(frozen=True)
class ResultadoCita:
    """Resultado de verificar una cita contra el texto extraído."""

    valida: bool
    codigo: str
    motivo: str | None = None
    ocurrencias: int = 0
    #: ``True`` si la cita coincide sin necesidad de normalizar espacios.
    exacta: bool = False


def verificar_cita(texto_documento: str, cita: str) -> ResultadoCita:
    """Verifica que ``cita`` aparezca literalmente en ``texto_documento``.

    Args:
        texto_documento: texto extraído del contrato.
        cita: fragmento que se pretende citar en el informe.

    Returns:
        :class:`ResultadoCita`. Cuando ``valida`` es ``False``, ``motivo``
        explica en español por qué se rechaza.
    """
    cita_limpia = (cita or "").strip()

    if not cita_limpia:
        return ResultadoCita(
            valida=False,
            codigo=COD_CITA_VACIA,
            motivo="La cita está vacía: no respalda el hallazgo con texto "
            "del documento.",
        )

    if len(cita_limpia) < MIN_CARACTERES_CITA:
        return ResultadoCita(
            valida=False,
            codigo=COD_CITA_MUY_CORTA,
            motivo=f"La cita tiene {len(cita_limpia)} caracteres y el mínimo "
            f"es {MIN_CARACTERES_CITA}: un fragmento tan corto puede "
            "coincidir por azar y no respalda el hallazgo.",
        )

    if not normalizar(texto_documento):
        return ResultadoCita(
            valida=False,
            codigo=COD_TEXTO_VACIO,
            motivo="No hay texto extraído contra el cual verificar la cita. "
            "El análisis no puede continuar.",
        )

    documento = texto_documento or ""
    # Coincidencia estricta: la cita tal cual, dentro del texto tal cual.
    ocurrencias_exactas = documento.count(cita_limpia)
    if ocurrencias_exactas > 0:
        return ResultadoCita(
            valida=True,
            codigo=COD_CITA_VALIDA,
            ocurrencias=ocurrencias_exactas,
            exacta=True,
        )

    # Coincidencia normalizada: mismo contenido, distintos espacios.
    documento_normalizado = normalizar(documento)
    cita_normalizada = normalizar(cita_limpia)
    ocurrencias = documento_normalizado.count(cita_normalizada)

    if ocurrencias > 0:
        return ResultadoCita(
            valida=True,
            codigo=COD_CITA_VALIDA,
            motivo="La cita coincide con el documento; difiere solo en "
            "saltos de línea o espacios.",
            ocurrencias=ocurrencias,
            exacta=False,
        )

    return ResultadoCita(
        valida=False,
        codigo=COD_CITA_NO_ENCONTRADA,
        motivo="La cita no aparece en el texto del documento analizado. El "
        "hallazgo se descarta para no presentar texto que no está en el "
        "contrato.",
    )


def es_cita_valida(texto_documento: str, cita: str) -> bool:
    """Atajo booleano de :func:`verificar_cita`."""
    return verificar_cita(texto_documento, cita).valida


@dataclass(frozen=True)
class Hallazgo:
    """Estructura provisional de un hallazgo del informe.

    Los campos siguen RF-05.1. **No define criterios jurídicos**: qué se
    busca en cada tipo de contrato sigue pendiente de validación con el
    tutor. Este módulo solo verifica que la cita exista en el documento.
    """

    tipo: TipoHallazgo
    categoria: str
    descripcion: str
    cita: str = ""
    explicacion: str = ""
    consecuencia: str = ""
    recomendacion: str = ""
    limitaciones: str = ""


@dataclass(frozen=True)
class HallazgoValidado:
    """Un hallazgo con el resultado de su verificación."""

    hallazgo: Hallazgo
    valido: bool
    codigo: str
    motivo: str | None = None
    detalle_cita: ResultadoCita | None = None


@dataclass(frozen=True)
class ResultadoFiltrado:
    """Hallazgos separados entre válidos y descartados."""

    validos: tuple[Hallazgo, ...] = field(default_factory=tuple)
    descartados: tuple[HallazgoValidado, ...] = field(default_factory=tuple)

    @property
    def total(self) -> int:
        return len(self.validos) + len(self.descartados)


def validar_hallazgo(
    hallazgo: Hallazgo, texto_documento: str
) -> HallazgoValidado:
    """Verifica un hallazgo contra el texto extraído.

    Un hallazgo es válido solo si su cita existe literalmente en el
    documento. Las omisiones no requieren cita (CC-01, CC-02), pero si
    aportan una, también se verifica.
    """
    if hallazgo.tipo in TIPOS_SIN_CITA and not (hallazgo.cita or "").strip():
        return HallazgoValidado(
            hallazgo=hallazgo,
            valido=True,
            codigo=COD_HALLAZGO_VALIDO,
            motivo="Hallazgo por omisión: no lleva cita, conforme a CC-01 y "
            "CC-02. No se inventa texto para respaldarlo.",
            detalle_cita=None,
        )

    detalle = verificar_cita(texto_documento, hallazgo.cita)

    if detalle.valida:
        return HallazgoValidado(
            hallazgo=hallazgo,
            valido=True,
            codigo=COD_HALLAZGO_VALIDO,
            detalle_cita=detalle,
        )

    return HallazgoValidado(
        hallazgo=hallazgo,
        valido=False,
        codigo=COD_HALLAZGO_DESCARTADO,
        motivo=detalle.motivo,
        detalle_cita=detalle,
    )


def filtrar_hallazgos(
    hallazgos: Iterable[Hallazgo], texto_documento: str
) -> ResultadoFiltrado:
    """Verifica una colección de hallazgos y devuelve solo los válidos.

    Los descartados se conservan en ``descartados`` con su motivo para poder
    auditar cuántos se rechazaron y por qué, pero **no** se devuelven como
    hallazgos del informe.
    """
    validos: list[Hallazgo] = []
    descartados: list[HallazgoValidado] = []

    for hallazgo in hallazgos:
        resultado = validar_hallazgo(hallazgo, texto_documento)
        if resultado.valido:
            validos.append(resultado.hallazgo)
        else:
            descartados.append(resultado)

    return ResultadoFiltrado(validos=tuple(validos), descartados=tuple(descartados))

    """Atajo booleano de :func:`verificar_cita`."""
    return verificar_cita(texto_documento, cita).valida
