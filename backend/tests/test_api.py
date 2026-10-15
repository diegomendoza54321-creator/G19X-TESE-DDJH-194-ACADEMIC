"""Pruebas de la API ``POST /extraer``.

Verifican sobre todo que la API nunca devuelve texto parcial: es la garantía
que el frontend necesita para detener el flujo (RF-02.4, RPJ-06).

``/extraer`` requiere sesión (RF-00.1): el cliente de estas pruebas inicia
sesión con un usuario autorizado en una base temporal. Las pruebas del
acceso sin sesión están en ``test_auth.py``.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import auth
from app.main import app


@pytest.fixture
def cliente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    ruta = tmp_path / "api.db"
    monkeypatch.setenv(auth.NOMBRE_VARIABLE_BD, str(ruta))
    auth.init_bd(ruta)
    auth.crear_usuario("revisor", "ClaveSegura123")
    with TestClient(app) as sesion:
        respuesta = sesion.post(
            "/login",
            data={"usuario": "revisor", "contrasena": "ClaveSegura123"},
        )
        assert respuesta.status_code == 200
        yield sesion


def _subir(cliente: TestClient, ruta: Path, nombre: str | None = None):
    with open(ruta, "rb") as manejador:
        return cliente.post(
            "/extraer",
            files={"archivo": (nombre or ruta.name, manejador)},
        )


# --------------------------------------------------------------------------
# Casos de éxito
# --------------------------------------------------------------------------
def test_salud_responde(cliente: TestClient) -> None:
    respuesta = cliente.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_api_pdf_valido_devuelve_texto(cliente: TestClient, pdf_servicios: Path) -> None:
    respuesta = _subir(cliente, pdf_servicios)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["formato"] == "pdf"
    assert cuerpo["num_paginas"] == 3
    assert "CONTRATO DE PRESTACION DE SERVICIOS" in cuerpo["texto"]
    assert cuerpo["motivo"] is None


def test_api_docx_valido_devuelve_texto(cliente: TestClient, docx_proveedor: Path) -> None:
    respuesta = _subir(cliente, docx_proveedor)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["formato"] == "docx"
    assert "Material A" in cuerpo["texto"]


# --------------------------------------------------------------------------
# Fallos atribuibles al archivo enviado → 400
# --------------------------------------------------------------------------
def test_api_formato_no_soportado_devuelve_400(
    cliente: TestClient, archivo_no_soportado: Path
) -> None:
    respuesta = _subir(cliente, archivo_no_soportado)

    assert respuesta.status_code == 400
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "formato_no_soportado"
    assert cuerpo["texto"] is None


def test_api_archivo_vacio_devuelve_400(cliente: TestClient, archivo_vacio: Path) -> None:
    respuesta = _subir(cliente, archivo_vacio)

    assert respuesta.status_code == 400
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "archivo_vacio"
    assert cuerpo["texto"] is None


# --------------------------------------------------------------------------
# Fallos de procesamiento → 422, siempre con texto nulo
# --------------------------------------------------------------------------
def test_api_pdf_escaneado_devuelve_422(cliente: TestClient, pdf_escaneado: Path) -> None:
    respuesta = _subir(cliente, pdf_escaneado)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "sin_texto"
    assert cuerpo["texto"] is None


def test_api_extraccion_incompleta_no_devuelve_texto_parcial(
    cliente: TestClient, pdf_extraccion_parcial: Path
) -> None:
    """Garantía central del bloque: nada de texto parcial en la respuesta."""
    respuesta = _subir(cliente, pdf_extraccion_parcial)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "extraccion_incompleta"
    assert cuerpo["texto"] is None
    # El texto de la página legible no se filtra en ningún campo.
    assert "OBJETO DEL CONTRATO" not in respuesta.text


def test_api_pdf_corrupto_devuelve_422(cliente: TestClient, pdf_corrupto: Path) -> None:
    respuesta = _subir(cliente, pdf_corrupto)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "archivo_no_leible"
    assert cuerpo["texto"] is None


def test_api_docx_corrupto_devuelve_422(cliente: TestClient, docx_corrupto: Path) -> None:
    respuesta = _subir(cliente, docx_corrupto)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["texto"] is None


def test_api_sin_archivo_devuelve_error_de_validacion(cliente: TestClient) -> None:
    respuesta = cliente.post("/extraer")

    assert respuesta.status_code == 422
