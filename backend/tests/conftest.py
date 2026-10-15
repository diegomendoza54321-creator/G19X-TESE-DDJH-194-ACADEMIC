"""Fixtures que generan documentos sintéticos para las pruebas.

Los contratos de prueba se construyen en memoria con ``fpdf2`` y
``python-docx``. Nunca se usan contratos reales de la organización: ver la
nota de ``docs/plan-de-pruebas.md``.

Sobre los acentos: las fuentes base de ``fpdf2`` codifican en latin-1, así
que los textos de los PDF usan español sin tildes para mantener las
aserciones deterministas.

Advertencia de terceros
-----------------------
``fastapi.testclient`` emite un ``StarletteDeprecationWarning`` al
importarse cuando solo está instalado ``httpx``. Se resolvió instalando
``httpx2``, la dependencia recomendada, en lugar de silenciarla. No hay
filtros de advertencias en el proyecto a propósito: si aparece una, es un
problema real y debe verse.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from docx import Document
from fpdf import FPDF


def crear_pdf(ruta: Path, textos_por_pagina: list[str]) -> Path:
    """Crea un PDF real con una página por cada texto de la lista."""
    pdf = FPDF()
    for texto in textos_por_pagina:
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 6, texto)
    pdf.output(str(ruta))
    return ruta


def crear_pdf_sin_texto(ruta: Path, num_paginas: int = 1) -> Path:
    """Crea un PDF con páginas en blanco: simula un documento escaneado."""
    pdf = FPDF()
    for _ in range(num_paginas):
        pdf.add_page()
    pdf.output(str(ruta))
    return ruta


def crear_docx(
    ruta: Path,
    parrafos: list[str],
    tabla: list[list[str]] | None = None,
) -> Path:
    """Crea un DOCX real con párrafos y, opcionalmente, una tabla."""
    documento = Document()
    for texto in parrafos:
        documento.add_paragraph(texto)
    if tabla:
        filas = documento.add_table(rows=len(tabla), cols=len(tabla[0]))
        for i, fila in enumerate(tabla):
            for j, valor in enumerate(fila):
                filas.cell(i, j).text = valor
    documento.save(str(ruta))
    return ruta


@pytest.fixture
def pdf_servicios(tmp_path: Path) -> Path:
    """PDF de prestación de servicios, 3 páginas con texto (caso CA-01)."""
    paginas = [
        "CONTRATO DE PRESTACION DE SERVICIOS profesionales celebrado entre "
        "EL CLIENTE y EL PRESTADOR de servicios.",
        "CLAUSULA PRIMERA. OBJETO. El PRESTADOR se obliga a prestar los "
        "servicios descritos en el Anexo 1 del presente contrato.",
        "CLAUSULA SEGUNDA. VIGENCIA. El contrato tendra una duracion de "
        "doce meses contados a partir de su firma por las partes.",
    ]
    return crear_pdf(tmp_path / "contrato_servicios.pdf", paginas)


@pytest.fixture
def docx_proveedor(tmp_path: Path) -> Path:
    """DOCX de contrato de proveedor con tabla (caso CA-02)."""
    return crear_docx(
        tmp_path / "contrato_proveedor.docx",
        parrafos=[
            "CONTRATO DE SUMINISTRO CON PROVEEDOR de bienes y materiales "
            "para las instalaciones del CLIENTE.",
            "CLAUSULA PRIMERA. ENTREGA. El PROVEEDOR entregara los bienes "
            "descritos en el Anexo 1 del presente contrato.",
            "El PROVEEDOR sera responsable de las penalizaciones senaladas "
            "en la clausula de incumplimiento.",
        ],
        tabla=[
            ["Concepto", "Cantidad"],
            ["Material A", "100 piezas"],
            ["Material B", "50 piezas"],
        ],
    )


@pytest.fixture
def pdf_escaneado(tmp_path: Path) -> Path:
    """PDF de 2 páginas sin capa de texto (caso CG-01)."""
    return crear_pdf_sin_texto(tmp_path / "escaneado.pdf", num_paginas=2)


@pytest.fixture
def pdf_extraccion_parcial(tmp_path: Path) -> Path:
    """PDF con texto en la página 1 y página 2 en blanco (caso CG-02)."""
    return crear_pdf(
        tmp_path / "parcial.pdf",
        [
            "CLAUSULA PRIMERA. OBJETO DEL CONTRATO. El PRESTADOR prestara "
            "los servicios descritos en el Anexo 1.",
            "",
        ],
    )


@pytest.fixture
def pdf_corrupto(tmp_path: Path) -> Path:
    """Archivo .pdf con contenido que no es un PDF (caso CG-03)."""
    ruta = tmp_path / "corrupto.pdf"
    ruta.write_bytes(b"%PDF-1.4\nesto no es un pdf valido\n%%EOF\n")
    return ruta


@pytest.fixture
def pdf_truncado(tmp_path: Path) -> Path:
    """PDF válido cortado por la mitad (caso CG-03, archivo truncado)."""
    origen = crear_pdf(
        tmp_path / "original.pdf",
        ["Contrato de prestacion de servicios entre las partes. " * 5],
    )
    datos = origen.read_bytes()
    ruta = tmp_path / "truncado.pdf"
    ruta.write_bytes(datos[: max(1, len(datos) // 2)])
    return ruta


@pytest.fixture
def docx_corrupto(tmp_path: Path) -> Path:
    """DOCX truncado: no es un ZIP válido."""
    origen = crear_docx(
        tmp_path / "valido.docx",
        ["Contrato de suministro con el PROVEEDOR de bienes."],
    )
    datos = origen.read_bytes()
    ruta = tmp_path / "roto.docx"
    ruta.write_bytes(datos[: max(1, len(datos) // 3)])
    return ruta


@pytest.fixture
def docx_sin_texto(tmp_path: Path) -> Path:
    """DOCX válido pero sin contenido textual."""
    return crear_docx(tmp_path / "vacio.docx", parrafos=["", "   ", ""])


@pytest.fixture
def archivo_no_soportado(tmp_path: Path) -> Path:
    """Archivo de texto plano: formato no soportado (RF-01.3)."""
    ruta = tmp_path / "notas.txt"
    ruta.write_text("Contrato de prestacion de servicios\n", encoding="utf-8")
    return ruta


@pytest.fixture
def archivo_vacio(tmp_path: Path) -> Path:
    """Archivo .pdf de cero bytes."""
    ruta = tmp_path / "vacio.pdf"
    ruta.write_bytes(b"")
    return ruta
