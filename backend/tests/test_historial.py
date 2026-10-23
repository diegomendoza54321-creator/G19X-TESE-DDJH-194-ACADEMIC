"""Pruebas del historial privado de análisis con IA (RF-04).

Verifican que:
- GET /historial requiere sesión (401 si no hay cookie).
- Un análisis exitoso guarda un registro consultable en GET /historial.
- Un usuario autenticado no puede consultar los registros de otro usuario.
- Si el análisis falla, no se guarda ningún registro en el historial.

Se usa una base SQLite temporal y se hace mock de ``analizar_con_ia``; no se
usa llama-server ni IA real.
"""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from app import auth
from app.main import app


USUARIO = "revisor"
CLAVE = "ClaveSegura123"
@pytest.fixture
def bd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Base SQLite aislada para cada prueba."""
    ruta = tmp_path / "historial.db"
    monkeypatch.setenv(auth.NOMBRE_VARIABLE_BD, str(ruta))
    auth.init_bd(ruta)
    return ruta


@pytest.fixture
def cliente(bd: Path) -> Generator[TestClient, None, None]:
    """Cliente de prueba sin sesión."""
    with TestClient(app) as sesion:
        yield sesion


@pytest.fixture
def cliente_autenticado(bd: Path) -> Generator[TestClient, None, None]:
    """Cliente de prueba con sesión activa."""
    auth.crear_usuario(USUARIO, CLAVE)
    with TestClient(app) as sesion:
        respuesta = sesion.post(
            "/login", data={"usuario": USUARIO, "contrasena": CLAVE}
        )
        assert respuesta.status_code == 200
        yield sesion
def _analisis_exitoso(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hace que analizar_con_ia retorne resultados falsos sin llamar al servidor."""

    async def _falso_analizar(texto: str, tipo_confirmado: str) -> object:
        from app.analisis_ia import ResultadoAnalisisIA

        return ResultadoAnalisisIA(hallazgos=[], num_descartados=0)

    monkeypatch.setattr("app.main.analizar_con_ia", _falso_analizar)


def _analisis_fallido(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hace que analizar_con_ia levante ErrorAnalisis para simular fallo."""

    from app.analisis_ia import ErrorAnalisis

    async def _falso_fallar(texto: str, tipo_confirmado: str) -> None:
        raise ErrorAnalisis(
            codigo="simulado_error",
            motivo="Error simulado en el análisis",
            estado_http=500,
        )

    monkeypatch.setattr("app.main.analizar_con_ia", _falso_fallar)


def _subir_archivo(cliente: TestClient, ruta: Path):
    """Sube un archivo PDF válido."""
    with open(ruta, "rb") as f:
        return cliente.post(
            "/extraer",
            files={"archivo": (ruta.name, f, "application/pdf")},
        )
def test_historial_sin_sesion_responde_401(cliente: TestClient) -> None:
    respuesta = cliente.get("/historial")
    assert respuesta.status_code == 401


def test_analisis_exitoso_guarda_registro_historial(
    cliente_autenticado: TestClient, pdf_servicios: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _analisis_exitoso(monkeypatch)

    resp_subir = _subir_archivo(cliente_autenticado, pdf_servicios)
    assert resp_subir.status_code == 200

    texto_muestra = "CLÁUSULA DE PRESTACIÓN DE SERVICIOS."
    tipo_muestra = "prestacion_de_servicios"

    resp_analisis = cliente_autenticado.post(
        "/analizar-con-ia",
        json={"texto": texto_muestra, "tipo_confirmado": tipo_muestra},
    )

    assert resp_analisis.status_code == 200

    resp_historial = cliente_autenticado.get("/historial")
    assert resp_historial.status_code == 200
    cuerpo = resp_historial.json()
    assert cuerpo["ok"] is True
    assert len(cuerpo["registros"]) >= 1
    registro = cuerpo["registros"][0]
    assert registro["tipo_confirmado"] == tipo_muestra
    assert "hallazgos" in registro


def test_usuario_no_ve_registros_de_otro(
    cliente_autenticado: TestClient,
    pdf_servicios: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _analisis_exitoso(monkeypatch)

    # 1. El primer usuario sube un archivo y hace un análisis exitoso
    resp_subir = _subir_archivo(cliente_autenticado, pdf_servicios)
    assert resp_subir.status_code == 200

    texto_muestra = "CLÁUSULA DE PRESTACIÓN DE SERVICIOS."
    tipo_muestra = "prestacion_de_servicios"

    resp_analisis = cliente_autenticado.post(
        "/analizar-con-ia",
        json={"texto": texto_muestra, "tipo_confirmado": tipo_muestra},
    )
    assert resp_analisis.status_code == 200

    # 2. Verificar que el historial del primer usuario contiene al menos un registro
    resp_historial_revisor = cliente_autenticado.get("/historial")
    assert resp_historial_revisor.status_code == 200
    cuerpo_revisor = resp_historial_revisor.json()
    assert cuerpo_revisor["ok"] is True
    assert len(cuerpo_revisor["registros"]) >= 1

    # 3. Crear un segundo usuario y hacer login con un TestClient separado
    auth.crear_usuario("otro_revisor", "OtraClave456")
    with TestClient(app) as cliente_otro:
        resp_login_otro = cliente_otro.post(
            "/login",
            data={"usuario": "otro_revisor", "contrasena": "OtraClave456"},
        )
        assert resp_login_otro.status_code == 200

        # 4. Consultar el historial del segundo usuario
        resp_historial_otro = cliente_otro.get("/historial")
        assert resp_historial_otro.status_code == 200
        cuerpo_otro = resp_historial_otro.json()
        assert cuerpo_otro["ok"] is True

        # 5. El segundo usuario no debe ver el registro del primero
        assert len(cuerpo_otro["registros"]) == 0


def test_analisis_fallido_no_guarda_registro(
    cliente_autenticado: TestClient, pdf_servicios: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _analisis_fallido(monkeypatch)

    resp_subir = _subir_archivo(cliente_autenticado, pdf_servicios)
    assert resp_subir.status_code == 200

    resp_analisis = cliente_autenticado.post(
        "/analizar-con-ia",
        json={"texto": "some text", "tipo_confirmado": "prestacion_de_servicios"},
    )

    assert resp_analisis.status_code == 500

    resp_historial = cliente_autenticado.get("/historial")
    assert resp_historial.status_code == 200
    cuerpo = resp_historial.json()
    assert cuerpo["ok"] is True
    assert len(cuerpo["registros"]) == 0
