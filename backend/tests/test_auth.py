"""Pruebas de autenticación privada (RF-00).

Verifican que la extracción exige sesión, que el login/logout funciona y
que no existe registro público. Usan una base SQLite temporal por prueba
(``MOTORREVISIONLEGAL_DB``); nunca tocan la base real ni usan contratos
reales: los documentos son los sintéticos de ``conftest.py``.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import auth
from app.auth import NOMBRE_COOKIE
from app.main import app

USUARIO = "revisor"
CLAVE = "ClaveSegura123"


@pytest.fixture
def bd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Base SQLite aislada para cada prueba."""
    ruta = tmp_path / "auth.db"
    monkeypatch.setenv(auth.NOMBRE_VARIABLE_BD, str(ruta))
    auth.init_bd(ruta)
    return ruta


@pytest.fixture
def cliente(bd: Path) -> Generator[TestClient, None, None]:
    with TestClient(app) as sesion:
        yield sesion


@pytest.fixture
def cliente_autenticado(bd: Path) -> Generator[TestClient, None, None]:
    auth.crear_usuario(USUARIO, CLAVE)
    with TestClient(app) as sesion:
        respuesta = sesion.post(
            "/login", data={"usuario": USUARIO, "contrasena": CLAVE}
        )
        assert respuesta.status_code == 200
        yield sesion


def _subir_pdf(cliente: TestClient, ruta: Path):
    with open(ruta, "rb") as manejador:
        return cliente.post(
            "/extraer", files={"archivo": (ruta.name, manejador)}
        )


# --------------------------------------------------------------------------
# Acceso sin sesión (RF-00.1)
# --------------------------------------------------------------------------
def test_extraer_sin_sesion_devuelve_401(
    cliente: TestClient, pdf_servicios: Path
) -> None:
    respuesta = _subir_pdf(cliente, pdf_servicios)

    assert respuesta.status_code == 401


def test_yo_sin_sesion_devuelve_401(cliente: TestClient) -> None:
    respuesta = cliente.get("/yo")

    assert respuesta.status_code == 401


def test_cookie_manipulada_se_rechaza(cliente: TestClient) -> None:
    cliente.cookies.set(NOMBRE_COOKIE, "token-falso")

    assert cliente.get("/yo").status_code == 401


# --------------------------------------------------------------------------
# Login y logout (RF-00.1, RF-00.3)
# --------------------------------------------------------------------------
def test_login_correcto_crea_sesion(cliente: TestClient, bd: Path) -> None:  # noqa: ARG001
    auth.crear_usuario(USUARIO, CLAVE)

    respuesta = cliente.post(
        "/login", data={"usuario": USUARIO, "contrasena": CLAVE}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["usuario"] == USUARIO
    assert cliente.cookies.get(NOMBRE_COOKIE)


def test_login_permite_usar_la_extraccion(
    cliente_autenticado: TestClient, pdf_servicios: Path
) -> None:
    respuesta = _subir_pdf(cliente_autenticado, pdf_servicios)

    assert respuesta.status_code == 200
    assert respuesta.json()["ok"] is True


def test_yo_devuelve_el_usuario(cliente_autenticado: TestClient) -> None:
    respuesta = cliente_autenticado.get("/yo")

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"] == USUARIO


def test_mismo_mensaje_para_usuario_inexistente_y_clave_erronea(
    cliente: TestClient, bd: Path  # noqa: ARG001
) -> None:
    """RF-00.3: el mensaje es genérico; no revela qué campo falló."""
    auth.crear_usuario(USUARIO, CLAVE)

    con_clave_erronea = cliente.post(
        "/login", data={"usuario": USUARIO, "contrasena": "OtraClave123"}
    )
    con_usuario_inexistente = cliente.post(
        "/login", data={"usuario": "nadie", "contrasena": "OtraClave123"}
    )

    assert con_clave_erronea.status_code == 401
    assert con_usuario_inexistente.status_code == 401
    assert (
        con_clave_erronea.json()["motivo"]
        == con_usuario_inexistente.json()["motivo"]
        == auth.MENSAJE_CREDENCIALES_INVALIDAS
    )


def test_logout_invalida_la_sesion(cliente_autenticado: TestClient) -> None:
    respuesta = cliente_autenticado.post("/logout")

    assert respuesta.status_code == 200
    assert respuesta.json()["ok"] is True
    assert cliente_autenticado.cookies.get(NOMBRE_COOKIE) is None
    assert cliente_autenticado.get("/yo").status_code == 401


def test_sesion_expirada_se_rechaza(
    cliente_autenticado: TestClient, bd: Path
) -> None:
    token = cliente_autenticado.cookies.get(NOMBRE_COOKIE)
    assert token
    resumen = hashlib.sha256(token.encode("utf-8")).hexdigest()
    conexion = sqlite3.connect(str(bd))
    try:
        conexion.execute(
            "UPDATE sesiones SET expira = '2000-01-01T00:00:00+00:00' "
            "WHERE token_hash = ?",
            (resumen,),
        )
        conexion.commit()
    finally:
        conexion.close()

    assert cliente_autenticado.get("/yo").status_code == 401


# --------------------------------------------------------------------------
# Sin registro público (RF-00.2) y almacenamiento seguro
# --------------------------------------------------------------------------
@pytest.mark.parametrize("ruta", ["/usuarios", "/registro", "/registrar"])
def test_no_existe_registro_publico(cliente: TestClient, ruta: str) -> None:
    respuesta = cliente.post(
        ruta, data={"usuario": "nuevo", "contrasena": CLAVE}
    )

    assert respuesta.status_code == 404


def test_contrasena_no_se_guarda_en_claro(bd: Path) -> None:
    auth.crear_usuario(USUARIO, CLAVE)

    conexion = sqlite3.connect(str(bd))
    try:
        fila = conexion.execute(
            "SELECT nombre, hash_contrasena, sal FROM usuarios"
        ).fetchone()
    finally:
        conexion.close()

    assert fila is not None
    assert CLAVE not in "|".join(str(valor) for valor in fila)

    with pytest.raises(ValueError):
        auth.crear_usuario(USUARIO, "OtraClave123")
    with pytest.raises(ValueError):
        auth.crear_usuario("nuevo", "corta")
