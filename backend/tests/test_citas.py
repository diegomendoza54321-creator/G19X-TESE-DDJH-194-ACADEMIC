"""Pruebas del verificador de citas (RPJ-02, RF-05.2, RF-05.3).

Casos CH-01 y CH-02 de ``docs/plan-de-pruebas.md``.
"""

from __future__ import annotations

import pytest

from app.citas import (
    COD_CITA_MUY_CORTA,
    COD_CITA_NO_ENCONTRADA,
    COD_CITA_VACIA,
    COD_TEXTO_VACIO,
    Hallazgo,
    es_cita_valida,
    filtrar_hallazgos,
    normalizar,
    validar_hallazgo,
    verificar_cita,
)

#: Texto de un contrato sintético, con saltos de línea como los que genera
#: la extracción real de un PDF.
TEXTO_CONTRATO = """CONTRATO DE PRESTACION DE SERVICIOS

CLAUSULA PRIMERA. OBJETO. El PRESTADOR se obliga a prestar los servicios de
desarrollo de software descritos en el Anexo 1 del presente contrato.

CLAUSULA SEGUNDA. VIGENCIA. El presente contrato tendra una duracion de doce
meses contados a partir de su firma.

CLAUSULA TERCERA. CONTRAPRESTACION. El CLIENTE pagara al PRESTADOR la
cantidad senalada en el Anexo 2."""

CITA_REAL = (
    "El PRESTADOR se obliga a prestar los servicios de desarrollo de "
    "software descritos en el Anexo 1"
)


# --------------------------------------------------------------------------
# Cita exacta
# --------------------------------------------------------------------------
def test_cita_exacta_es_valida() -> None:
    resultado = verificar_cita(TEXTO_CONTRATO, CITA_REAL)

    assert resultado.valida
    assert resultado.codigo == "cita_valida"
    assert resultado.ocurrencias == 1
    assert resultado.exacta is False  # el documento parte la línea
    assert resultado.motivo is not None


def test_cita_exacta_sin_saltos_intermedios_es_exacta() -> None:
    """Si el documento no parte la línea, la coincidencia es estricta."""
    texto = "El PRESTADOR se obliga a prestar los servicios descritos en el Anexo 1."

    resultado = verificar_cita(texto, CITA_REAL.replace("de desarrollo de software ", ""))

    assert resultado.valida
    assert resultado.exacta is True
    assert resultado.motivo is None


def test_cita_con_ene_y_acentos_se_verifica_literal() -> None:
    texto = "El señor PROVEEDOR señala la cláusula de cumplimiento del Anexo 1."

    assert es_cita_valida(texto, "la cláusula de cumplimiento del Anexo 1")
    assert not es_cita_valida(texto, "la clausula de cumplimiento del Anexo 1")


def test_cita_que_cruza_saltos_de_linea_se_acepta() -> None:
    """La normalización de espacios no altera el contenido (decisión 1)."""
    cita = (
        "CLAUSULA SEGUNDA. VIGENCIA. El presente contrato tendra una "
        "duracion de doce meses contados a partir de su firma."
    )

    assert es_cita_valida(TEXTO_CONTRATO, cita)


def test_normalizar_solo_colapsa_espacios() -> None:
    assert normalizar("a  b\n\tc") == "a b c"
    # No cambia mayúsculas, acentos ni signos.
    assert normalizar("El Señor, ¿vígencia?") == "El Señor, ¿vígencia?"


# --------------------------------------------------------------------------
# Cita alterada
# --------------------------------------------------------------------------
def test_cita_alterada_es_invalida() -> None:
    """Una palabra cambiada invalida la cita (RPJ-02)."""
    alterada = CITA_REAL.replace("desarrollo de software", "desarrollo de hardware")

    resultado = verificar_cita(TEXTO_CONTRATO, alterada)

    assert not resultado.valida
    assert resultado.codigo == COD_CITA_NO_ENCONTRADA
    assert resultado.ocurrencias == 0
    assert "no aparece en el texto" in resultado.motivo


def test_cita_con_capitalizacion_alterada_es_invalida() -> None:
    """Cambiar mayúsculas altera el texto (decisión 2)."""
    resultado = verificar_cita(TEXTO_CONTRATO, CITA_REAL.upper())

    assert not resultado.valida
    assert resultado.codigo == COD_CITA_NO_ENCONTRADA


def test_cita_inventada_por_completo_es_invalida() -> None:
    """Cita plausible pero que no está en el documento."""
    inventada = (
        "El CLIENTE podra rescindir el contrato en cualquier momento sin "
        "penalizacion alguna para las partes."
    )

    assert not es_cita_valida(TEXTO_CONTRATO, inventada)


def test_cita_con_numero_alterado_es_invalida() -> None:
    """Cambiar doce por catorce meses sigue siendo cita alterada."""
    alterada = CITA_REAL  # cita real de otra cláusula
    assert es_cita_valida(TEXTO_CONTRATO, alterada)

    falsa = "duracion de catorce meses contados a partir de su firma"
    assert not es_cita_valida(TEXTO_CONTRATO, falsa)


# --------------------------------------------------------------------------
# Cita vacía
# --------------------------------------------------------------------------
def test_cita_vacia_es_invalida() -> None:
    resultado = verificar_cita(TEXTO_CONTRATO, "")

    assert not resultado.valida
    assert resultado.codigo == COD_CITA_VACIA
    assert "vacía" in resultado.motivo


def test_cita_de_solo_espacios_es_invalida() -> None:
    resultado = verificar_cita(TEXTO_CONTRATO, "   \n\t  ")

    assert not resultado.valida
    assert resultado.codigo == COD_CITA_VACIA


def test_cita_none_se_trata_como_vacia() -> None:
    assert not es_cita_valida(TEXTO_CONTRATO, None)  # type: ignore[arg-type]


def test_cita_muy_corta_es_invalida() -> None:
    """Un fragmento diminuto coincidiría por azar (decisión 3)."""
    resultado = verificar_cita(TEXTO_CONTRATO, "El CLIENTE")

    assert not resultado.valida
    assert resultado.codigo == COD_CITA_MUY_CORTA
    assert "por azar" in resultado.motivo


def test_sin_texto_extraido_no_se_puede_verificar() -> None:
    resultado = verificar_cita("", CITA_REAL)

    assert not resultado.valida
    assert resultado.codigo == COD_TEXTO_VACIO
    assert "no puede continuar" in resultado.motivo


# --------------------------------------------------------------------------
# Hallazgos: los inválidos no se devuelven
# --------------------------------------------------------------------------
def _hallazgo(cita: str, tipo: str = "ambiguedad") -> Hallazgo:
    return Hallazgo(
        tipo=tipo,  # type: ignore[arg-type]
        categoria="Vigencia",
        descripcion="La vigencia no establece una fecha de término.",
        cita=cita,
        explicacion="El plazo queda abierto a interpretación.",
        consecuencia="Ninguna de las partes sabe cuándo termina.",
        recomendacion="Precisar la fecha o el mecanismo de terminación.",
        limitaciones="Análisis orientativo; requiere revisión profesional.",
    )


def test_hallazgo_con_cita_valida_se_acepta() -> None:
    resultado = validar_hallazgo(_hallazgo(CITA_REAL), TEXTO_CONTRATO)

    assert resultado.valido
    assert resultado.codigo == "hallazgo_valido"
    assert resultado.detalle_cita is not None
    assert resultado.detalle_cita.valida


def test_hallazgo_con_cita_alterada_se_marca_invalido() -> None:
    alterada = CITA_REAL.replace("Anexo 1", "Anexo 9")

    resultado = validar_hallazgo(_hallazgo(alterada), TEXTO_CONTRATO)

    assert not resultado.valido
    assert resultado.codigo == "hallazgo_descartado"
    assert resultado.motivo is not None


def test_hallazgo_con_cita_vacia_se_marca_invalido() -> None:
    resultado = validar_hallazgo(_hallazgo(""), TEXTO_CONTRATO)

    assert not resultado.valido
    assert resultado.detalle_cita is not None
    assert resultado.detalle_cita.codigo == COD_CITA_VACIA


def test_omision_sin_cita_es_valida() -> None:
    """CC-01 y CC-02: una omisión no debe llevar cita inventada."""
    hallazgo = Hallazgo(
        tipo="omision",
        categoria="Confidencialidad",
        descripcion="No se encontró cláusula de confidencialidad.",
        recomendacion="Incluir una cláusula de confidencialidad.",
        limitaciones="Análisis orientativo; requiere revisión profesional.",
    )

    resultado = validar_hallazgo(hallazgo, TEXTO_CONTRATO)

    assert resultado.valido
    assert resultado.detalle_cita is None
    assert "CC-01" in resultado.motivo


def test_omision_con_cita_inventada_se_descarta() -> None:
    """Si una omisión trae cita, esa cita también debe existir."""
    hallazgo = Hallazgo(
        tipo="omision",
        categoria="Confidencialidad",
        descripcion="No se encontró cláusula de confidencialidad.",
        cita="Las partes acuerdan mantener confidencialidad total del Anexo 1.",
    )

    assert not validar_hallazgo(hallazgo, TEXTO_CONTRATO).valido


def test_filtrar_devuelve_solo_los_validos() -> None:
    hallazgos = [
        _hallazgo(CITA_REAL),
        _hallazgo(CITA_REAL.replace("Anexo 1", "Anexo 7")),
        _hallazgo(""),
        Hallazgo(
            tipo="omision",
            categoria="Jurisdicción",
            descripcion="No se encontró cláusula de jurisdicción aplicable.",
        ),
    ]

    resultado = filtrar_hallazgos(hallazgos, TEXTO_CONTRATO)

    assert resultado.total == 4
    assert len(resultado.validos) == 2
    assert len(resultado.descartados) == 2

    # Sobrevive el hallazgo con cita real y la omisión, que no lleva cita.
    categorias_validas = {h.categoria for h in resultado.validos}
    assert categorias_validas == {"Vigencia", "Jurisdicción"}

    con_cita = [h for h in resultado.validos if h.cita]
    assert len(con_cita) == 1
    assert con_cita[0].cita == CITA_REAL

    # Los descartados no se devuelven como hallazgos y traen su motivo.
    assert {d.hallazgo.categoria for d in resultado.descartados} == {"Vigencia"}
    assert all(d.motivo for d in resultado.descartados)
    assert all(not d.valido for d in resultado.descartados)


def test_filtrar_sin_hallazgos_devuelve_vacio() -> None:
    resultado = filtrar_hallazgos([], TEXTO_CONTRATO)

    assert resultado.total == 0
    assert resultado.validos == ()
    assert resultado.descartados == ()


def test_filtrar_descarta_todo_si_no_hay_texto() -> None:
    """Sin texto extraído no puede haber hallazgos respaldados (RPJ-06)."""
    hallazgos = [
        _hallazgo(CITA_REAL),
        _hallazgo(CITA_REAL.replace("Anexo 1", "Anexo 3")),
    ]

    resultado = filtrar_hallazgos(hallazgos, "")

    assert resultado.validos == ()
    assert len(resultado.descartados) == 2


@pytest.mark.parametrize(
    "cita",
    [
        "El PRESTADOR se obliga a prestar los servicios de desarrollo de software descritos en el Anexo 1",
        "CLAUSULA SEGUNDA. VIGENCIA. El presente contrato tendra una duracion",
        "El CLIENTE pagara al PRESTADOR la cantidad senalada en el Anexo 2",
    ],
)
def test_citas_reales_del_contrato_se_aceptan(cita: str) -> None:
    assert es_cita_valida(TEXTO_CONTRATO, cita)


@pytest.mark.parametrize(
    "cita",
    [
        "El PRESTADOR se obliga a prestar los servicios de desarrollo web descritos en el Anexo 1",
        "CLAUSULA SEGUNDA. VIGENCIA. El presente contrato tendra una duracion de veinte",
        "El CLIENTE pagara al PROVEEDOR la cantidad senalada en el Anexo 2",
    ],
)
def test_citas_con_una_palabra_distinta_se_rechazan(cita: str) -> None:
    assert not es_cita_valida(TEXTO_CONTRATO, cita)
