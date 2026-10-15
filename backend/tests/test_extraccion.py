"""Pruebas del módulo de extracción (RF-01, RF-02, RPJ-06).

Los casos se nombran con los identificadores de ``docs/plan-de-pruebas.md``
para mantener la trazabilidad entre requisitos, plan y pruebas.
"""

from __future__ import annotations

from pathlib import Path

from app.extraccion import (
    COD_ARCHIVO_NO_LEIBLE,
    COD_ARCHIVO_VACIO,
    COD_EXTRACCION_INCOMPLETA,
    COD_FORMATO_NO_SOPORTADO,
    COD_SIN_TEXTO,
    COD_TAMANO_EXCEDIDO,
    TAMANO_MAXIMO_BYTES,
    detectar_formato,
    extraer_texto,
    extraer_texto_desde_ruta,
)
from tests.conftest import crear_docx, crear_pdf

# --------------------------------------------------------------------------
# CA-01 — PDF de prestación de servicios (RF-02.1)
# --------------------------------------------------------------------------
def test_ca01_pdf_con_texto_se_extrae_completo(pdf_servicios: Path) -> None:
    resultado = extraer_texto_desde_ruta(pdf_servicios)

    assert resultado.ok, resultado.motivo
    assert resultado.formato == "pdf"
    assert resultado.num_paginas == 3
    assert "CONTRATO DE PRESTACION DE SERVICIOS" in resultado.texto
    assert "CLAUSULA PRIMERA" in resultado.texto
    assert "CLAUSULA SEGUNDA" in resultado.texto


# --------------------------------------------------------------------------
# CA-02 — DOCX de proveedor, incluida la tabla (RF-02.2)
# --------------------------------------------------------------------------
def test_ca02_docx_se_extrae_incluyendo_tablas(docx_proveedor: Path) -> None:
    resultado = extraer_texto_desde_ruta(docx_proveedor)

    assert resultado.ok, resultado.motivo
    assert resultado.formato == "docx"
    assert "CONTRATO DE SUMINISTRO CON PROVEEDOR" in resultado.texto
    # El contenido de la tabla forma parte del texto extraído.
    assert "Material A" in resultado.texto
    assert "100 piezas" in resultado.texto
    # Un DOCX no declara páginas fiables.
    assert resultado.num_paginas is None


def test_docx_con_acentos_se_extrae_en_unicode(tmp_path: Path) -> None:
    """python-docx trabaja en UTF-8: los acentos se preservan."""
    ruta = crear_docx(
        tmp_path / "acentos.docx",
        ["El señor PROVEEDOR señala la cláusula de cumplimiento."],
    )

    resultado = extraer_texto_desde_ruta(ruta)

    assert resultado.ok, resultado.motivo
    assert "señor" in resultado.texto
    assert "cláusula" in resultado.texto


# --------------------------------------------------------------------------
# CG-01 — PDF escaneado sin capa de texto
# --------------------------------------------------------------------------
def test_cg01_pdf_sin_texto_se_rechaza(pdf_escaneado: Path) -> None:
    resultado = extraer_texto_desde_ruta(pdf_escaneado)

    assert not resultado.ok
    assert resultado.codigo == COD_SIN_TEXTO
    # RPJ-06 / RF-02.4: nunca se devuelve texto parcial.
    assert resultado.texto == ""
    assert "texto seleccionable" in resultado.motivo


# --------------------------------------------------------------------------
# CG-02 — Extracción incompleta: se detiene, sin texto parcial
# --------------------------------------------------------------------------
def test_cg02_extraccion_incompleta_detiene_el_proceso(
    pdf_extraccion_parcial: Path,
) -> None:
    resultado = extraer_texto_desde_ruta(pdf_extraccion_parcial)

    assert not resultado.ok
    assert resultado.codigo == COD_EXTRACCION_INCOMPLETA
    # El punto crítico: no se entrega el texto de la página que sí se leyó.
    assert resultado.texto == ""
    assert "OBJETO DEL CONTRATO" not in resultado.texto
    assert "incompleta" in resultado.motivo
    # El mensaje indica qué página quedó sin texto.
    assert "2" in resultado.motivo


# --------------------------------------------------------------------------
# CG-03 — Archivo corrupto o truncado
# --------------------------------------------------------------------------
def test_cg03_pdf_corrupto_se_rechaza(pdf_corrupto: Path) -> None:
    resultado = extraer_texto_desde_ruta(pdf_corrupto)

    assert not resultado.ok
    assert resultado.codigo == COD_ARCHIVO_NO_LEIBLE
    assert resultado.texto == ""


def test_cg03_pdf_truncado_se_rechaza(pdf_truncado: Path) -> None:
    resultado = extraer_texto_desde_ruta(pdf_truncado)

    assert not resultado.ok
    assert resultado.texto == ""


def test_cg03_docx_corrupto_se_rechaza(docx_corrupto: Path) -> None:
    resultado = extraer_texto_desde_ruta(docx_corrupto)

    assert not resultado.ok
    assert resultado.codigo == COD_ARCHIVO_NO_LEIBLE
    assert resultado.texto == ""


def test_docx_valido_sin_texto_se_rechaza(docx_sin_texto: Path) -> None:
    resultado = extraer_texto_desde_ruta(docx_sin_texto)

    assert not resultado.ok
    assert resultado.codigo == COD_SIN_TEXTO
    assert resultado.texto == ""


# --------------------------------------------------------------------------
# RF-01.3 — Formato no soportado
# --------------------------------------------------------------------------
def test_formato_no_soportado_se_rechaza(archivo_no_soportado: Path) -> None:
    resultado = extraer_texto_desde_ruta(archivo_no_soportado)

    assert not resultado.ok
    assert resultado.codigo == COD_FORMATO_NO_SOPORTADO
    assert resultado.texto == ""
    assert "PDF" in resultado.motivo
    assert "DOCX" in resultado.motivo


def test_extension_en_mayusculas_se_acepta() -> None:
    assert detectar_formato("CONTRATO.PDF") == "pdf"
    assert detectar_formato("Contrato.Docx") == "docx"


def test_sin_extension_se_rechaza() -> None:
    resultado = extraer_texto("contrato", b"algo")

    assert not resultado.ok
    assert resultado.codigo == COD_FORMATO_NO_SOPORTADO


# --------------------------------------------------------------------------
# RF-01.4 — Tamaño máximo
# --------------------------------------------------------------------------
def test_archivo_vacio_se_rechaza(archivo_vacio: Path) -> None:
    resultado = extraer_texto_desde_ruta(archivo_vacio)

    assert not resultado.ok
    assert resultado.codigo == COD_ARCHIVO_VACIO
    assert resultado.texto == ""


def test_tamano_maximo_se_valida(tmp_path: Path) -> None:
    """Un archivo que supera el límite se rechaza antes de procesarlo."""
    contenido_valido = crear_pdf(
        tmp_path / "base.pdf",
        ["Contrato de prestacion de servicios entre las partes. " * 5],
    ).read_bytes()

    datos = contenido_valido + b"x" * (TAMANO_MAXIMO_BYTES + 1)
    resultado = extraer_texto("grande.pdf", datos)

    assert not resultado.ok
    assert resultado.codigo == COD_TAMANO_EXCEDIDO
    assert resultado.texto == ""
    assert "10 MB" in resultado.motivo
