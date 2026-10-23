"""Pruebas de ``POST /analizar-con-ia`` y ``GET /analizar-con-ia/estado`` (RF-04).

Cubren: sesi\u00f3n obligatoria, validaci\u00f3n de entrada, fallos del servidor
local (modelo_no_disponible, tiempo_excedido, modelo_ocupado,
respuesta_invalida, contexto_excedido), cita literal aceptada, cita
inventada descartada, y estado de ocupaci\u00f3n incluido fail-safe /slots.

No tocan auth.py, clasificacion.py, citas.py ni el frontend. Todas las
llamadas al servidor local se mockean para no depender de llama-server.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import auth
import app.analisis_ia as analisis_ia_mod
from app.analisis_ia import ErrorAnalisis, ResultadoAnalisisIA
from app.auth import NOMBRE_COOKIE
from app.citas import Hallazgo
from app.clasificacion import ETIQUETAS
from app.main import app

USUARIO = "revisor"
CLAVE = "ClaveSegura123"

TEXTO_CORTO = "CONTRATO DE PRESTACION DE SERVICIOS"
TIPO_VALIDO = "prestacion_de_servicios"


@pytest.fixture
def cliente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    """Cliente HTTP con sesi\u00f3n activa (mismo patr\u00f3n que test_api.py)."""
    ruta = tmp_path / "analisis.db"
    monkeypatch.setenv(auth.NOMBRE_VARIABLE_BD, str(ruta))
    auth.init_bd(ruta)
    auth.crear_usuario(USUARIO, CLAVE)
    with TestClient(app) as sesion:
        respuesta = sesion.post(
            "/login",
            data={"usuario": USUARIO, "contrasena": CLAVE},
        )
        assert respuesta.status_code == 200
        yield sesion


def _post_analisis(
    cliente: TestClient,
    texto: str = TEXTO_CORTO,
    tipo: str = TIPO_VALIDO,
):
    return cliente.post(
        "/analizar-con-ia",
        json={"texto": texto, "tipo_confirmado": tipo},
    )


# --------------------------------------------------------------------------
# POST /analizar-con-ia — sesi\u00f3n obligatoria y validaci\u00f3n de entrada
# --------------------------------------------------------------------------


def test_sin_sesion_devuelve_401() -> None:
    """Sin cookie de sesi\u00f3n, el endpoint rechaza con 401 (RF-00.1)."""
    with TestClient(app) as c:
        respuesta = _post_analisis(c)
        assert respuesta.status_code == 401


def test_texto_vacio_devuelve_422(cliente: TestClient) -> None:
    """Texto vac\u00edo tras strip devuelve 422 con c\u00f3digo texto_vacio."""
    respuesta = _post_analisis(cliente, texto="")
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "texto_vacio"
    assert cuerpo["hallazgos"] is None


def test_texto_solo_espacios_devuelve_422(cliente: TestClient) -> None:
    """Texto solo espacios tambi\u00e9n se considera vac\u00edo."""
    respuesta = _post_analisis(cliente, texto="   ")
    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "texto_vacio"


def test_tipo_no_confirmado_devuelve_422(cliente: TestClient) -> None:
    """tipo_confirmado fuera de ETIQUETAS devuelve 422 con c\u00f3digo tipo_no_confirmado."""
    respuesta = _post_analisis(cliente, tipo="tipo_inexistente")
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "tipo_no_confirmado"


def test_tipo_invalido_no_analiza(cliente: TestClient) -> None:
    """Con tipo inv\u00e1lido no se llama al servidor local."""
    assert TIPO_VALIDO in ETIQUETAS
    respuesta = _post_analisis(cliente, tipo="no_existe")
    assert respuesta.status_code == 422


# --------------------------------------------------------------------------
# POST /analizar-con-ia — fallos del servidor local (mockeados)
# --------------------------------------------------------------------------


def _mock_analizar(
    monkeypatch: pytest.MonkeyPatch,
    error: ErrorAnalisis | None = None,
    resultado: ResultadoAnalisisIA | None = None,
) -> None:
    """Sustituye ``app.main.analizar_con_ia`` por un mock async."""

    async def _llamar(texto: str, tipo: str):
        if error is not None:
            raise error
        if resultado is not None:
            return resultado
        raise AssertionError("Mock sin error ni resultado")

    monkeypatch.setattr("app.main.analizar_con_ia", _llamar)


def test_modelo_no_disponible_devuelve_503(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ConnectError del servidor local -> 503 modelo_no_disponible."""
    _mock_analizar(
        monkeypatch,
        error=ErrorAnalisis("modelo_no_disponible", "No hay servidor", 503),
    )
    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 503
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is False
    assert cuerpo["codigo"] == "modelo_no_disponible"


def test_tiempo_excedido_devuelve_503(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Timeout de lectura/total -> 503 tiempo_excedido."""
    _mock_analizar(
        monkeypatch,
        error=ErrorAnalisis("tiempo_excedido", "Tiempo excedido", 503),
    )
    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 503
    assert respuesta.json()["codigo"] == "tiempo_excedido"


def test_modelo_ocupado_devuelve_409(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lock tomado -> 409 modelo_ocupado."""
    _mock_analizar(
        monkeypatch,
        error=ErrorAnalisis("modelo_ocupado", "Ocupado", 409),
    )
    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "modelo_ocupado"


def test_respuesta_invalida_devuelve_502(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Respuesta inv\u00e1lida del modelo -> 502 respuesta_invalida."""
    _mock_analizar(
        monkeypatch,
        error=ErrorAnalisis("respuesta_invalida", "Formato inv\u00e1lido", 502),
    )
    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 502
    assert respuesta.json()["codigo"] == "respuesta_invalida"


def test_contexto_excedido_devuelve_422(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Contexto excedido -> 422 contexto_excedido."""
    _mock_analizar(
        monkeypatch,
        error=ErrorAnalisis("contexto_excedido", "Contexto excedido", 422),
    )
    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "contexto_excedido"


# --------------------------------------------------------------------------
# POST /analizar-con-ia — cita literal aceptada / inventada descartada
# --------------------------------------------------------------------------


def _hallazgo_prueba(cita: str) -> Hallazgo:
    return Hallazgo(
        tipo="ambiguedad",
        categoria="Vigencia",
        descripcion="No se define la vigencia del contrato.",
        cita=cita,
        explicacion="Explicaci\u00f3n de prueba.",
        consecuencia="Consecuencia de prueba.",
        recomendacion="Recomendaci\u00f3n de prueba.",
        limitaciones="Limitaciones de prueba.",
    )


def test_cita_literal_aceptada_devuelve_hallazgo(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cita que existe en el texto se acepta y se devuelve en hallazgos."""
    hallazgo = _hallazgo_prueba("CONTRATO DE PRESTACION DE SERVICIOS")

    async def _exitoso(texto: str, tipo: str) -> ResultadoAnalisisIA:
        return ResultadoAnalisisIA(hallazgos=[hallazgo], num_descartados=0)

    monkeypatch.setattr("app.main.analizar_con_ia", _exitoso)

    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["num_descartados"] == 0
    assert len(cuerpo["hallazgos"]) == 1
    assert cuerpo["hallazgos"][0]["cita"] == "CONTRATO DE PRESTACION DE SERVICIOS"


def test_cita_inventada_descartada_no_renderer(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cita que no existe en el texto se descarta y no aparece en hallazgos."""
    async def _con_descartados(texto: str, tipo: str) -> ResultadoAnalisisIA:
        return ResultadoAnalisisIA(hallazgos=[], num_descartados=1)

    monkeypatch.setattr("app.main.analizar_con_ia", _con_descartados)

    respuesta = _post_analisis(cliente)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ok"] is True
    assert cuerpo["num_descartados"] == 1
    assert cuerpo["hallazgos"] == []


# --------------------------------------------------------------------------
# GET /analizar-con-ia/estado
# --------------------------------------------------------------------------


def test_estado_sin_sesion_devuelve_401() -> None:
    """Sin cookie de sesi\u00f3n, el estado tambi\u00e9n rechaza con 401."""
    with TestClient(app) as c:
        respuesta = c.get("/analizar-con-ia/estado")
        assert respuesta.status_code == 401


def _mock_estado(
    monkeypatch: pytest.MonkeyPatch, ocupado: bool, fuente: str
) -> None:
    """Sustituye ``app.main.consultar_ocupacion`` por un mock async."""

    async def _consultar() -> tuple[bool, str]:
        return (ocupado, fuente)

    monkeypatch.setattr("app.main.consultar_ocupacion", _consultar)


def test_estado_libre_devuelve_ocupado_falso(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """/slots reporta sin procesar -> ocupado:false, fuente:\"slots\"."""
    _mock_estado(monkeypatch, False, "slots")
    respuesta = cliente.get("/analizar-con-ia/estado")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ocupado"] is False
    assert cuerpo["fuente"] == "slots"


def test_estado_ocupado_slots_devuelve_verdadero(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """/slots reporta procesando -> ocupado:true, fuente:\"slots\"."""
    _mock_estado(monkeypatch, True, "slots")
    respuesta = cliente.get("/analizar-con-ia/estado")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ocupado"] is True
    assert cuerpo["fuente"] == "slots"


def test_estado_fuente_desconocida_fail_safe(
    cliente: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """/slots inv\u00e1ldo o no verificable -> ocupado:true, fuente:\"desconocida\"."""
    _mock_estado(monkeypatch, True, "desconocida")
    respuesta = cliente.get("/analizar-con-ia/estado")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["ocupado"] is True
    assert cuerpo["fuente"] == "desconocida"


# --------------------------------------------------------------------------
# Configuración del servidor local de IA mediante variables de entorno
# --------------------------------------------------------------------------


def test_url_servidor_local_valor_por_defecto() -> None:
    """Sin variable de entorno, la URL es http://127.0.0.1:9931."""
    assert analisis_ia_mod.URL_SERVIDOR_LOCAL == "http://127.0.0.1:9931"


def test_limite_contexto_valor_por_defecto() -> None:
    """Sin variable de entorno, el límite de contexto es 2048."""
    assert analisis_ia_mod.N_CTX == 2048


def test_url_sobrescrita_por_variable_entorno(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """URL_SERVIDOR_IA sobrescribe la URL predeterminada."""
    monkeypatch.setenv("URL_SERVIDOR_IA", "http://localhost:9931")
    assert analisis_ia_mod._leer_url_servidor_local() == "http://localhost:9931"


def test_limite_contexto_sobrescrito_por_variable_entorno(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LIMITE_CONTEXTO_IA sobrescribe el límite predeterminado."""
    monkeypatch.setenv("LIMITE_CONTEXTO_IA", "4096")
    assert analisis_ia_mod._leer_limite_contexto() == 4096


def test_host_no_local_es_rechazado(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un host distinto de 127.0.0.1 o localhost lanza ValueError."""
    monkeypatch.setenv("URL_SERVIDOR_IA", "http://example.com:9931")
    with pytest.raises(ValueError, match="Host no permitido"):
        analisis_ia_mod._leer_url_servidor_local()


def test_localhost_es_valido(monkeypatch: pytest.MonkeyPatch) -> None:
    """localhost es un host válido para el servidor local."""
    monkeypatch.setenv("URL_SERVIDOR_IA", "http://localhost:9931")
    assert analisis_ia_mod._leer_url_servidor_local() == "http://localhost:9931"


def test_limite_contexto_no_entero_es_rechazado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LIMITE_CONTEXTO_IA con valor no entero lanza ValueError."""
    monkeypatch.setenv("LIMITE_CONTEXTO_IA", "abc")
    with pytest.raises(ValueError, match="entero positivo"):
        analisis_ia_mod._leer_limite_contexto()


def test_limite_contexto_cero_es_rechazado(monkeypatch: pytest.MonkeyPatch) -> None:
    """LIMITE_CONTEXTO_IA igual a cero lanza ValueError."""
    monkeypatch.setenv("LIMITE_CONTEXTO_IA", "0")
    with pytest.raises(ValueError, match="entero positivo"):
        analisis_ia_mod._leer_limite_contexto()


def test_limite_contexto_negativo_es_rechazado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LIMITE_CONTEXTO_IA negativo lanza ValueError."""
    monkeypatch.setenv("LIMITE_CONTEXTO_IA", "-100")
    with pytest.raises(ValueError, match="entero positivo"):
        analisis_ia_mod._leer_limite_contexto()


# --------------------------------------------------------------------------
# Pruebas unitarias de ``construir_mensajes`` — integración de criterios
# --------------------------------------------------------------------------


def _mock_cargar_criterios(monkeypatch, datos: dict) -> None:
    """Simula ``analisis_ia_mod._cargar_criterios`` devolviendo ``datos`` en memoria."""
    monkeypatch.setattr("app.analisis_ia._cargar_criterios", lambda: datos)


def test_construir_mensajes_incluye_criterios(monkeypatch) -> None:
    """Para cada tipo de contrato, el prompt incluye sus criterios configurados."""
    from app.analisis_ia import construir_mensajes

    _mock_cargar_criterios(monkeypatch, {
        "prestacion_de_servicios": ["Criterio A", "Criterio B"],
        "proveedor": [],
    })

    texto = "CONTRATO DE PRESTACION DE SERVICIOS"
    msgs = construir_mensajes(texto, "prestacion_de_servicios")
    contenido = msgs[0]["content"]

    # Los criterios deben aparecer en el prompt
    assert "CRITERIOS DE REVISION" in contenido
    assert "Criterio A" in contenido
    assert "Criterio B" in contenido


def test_construir_mensajes_no_mistura_criterios(monkeypatch) -> None:
    """El prompt no mezcla criterios del otro tipo."""
    from app.analisis_ia import construir_mensajes

    _mock_cargar_criterios(monkeypatch, {
        "prestacion_de_servicios": ["C1", "C2"],
        "proveedor": ["C3", "C4"],
    })

    # Con tipo "prestacion_de_servicios", aparecen C1 y C2, no C3 ni C4
    msgs = construir_mensajes("texto", "prestacion_de_servicios")
    contenido = msgs[0]["content"]
    assert "C1" in contenido
    assert "C2" in contenido
    assert "C3" not in contenido
    assert "C4" not in contenido

    # Con tipo "proveedor", aparecen C3 y C4, no C1 ni C2
    msgs2 = construir_mensajes("texto", "proveedor")
    contenido2 = msgs2[0]["content"]
    assert "C3" in contenido2
    assert "C4" in contenido2
    assert "C1" not in contenido2
    assert "C2" not in contenido2


def test_construir_mensajes_sin_criterios_tipo_valido(monkeypatch) -> None:
    """Si un tipo válido no tiene criterios configurados, construir_mensajes sigue funcionando."""
    from app.analisis_ia import construir_mensajes

    _mock_cargar_criterios(monkeypatch, {})

    texto = "CONTRATO DE PRESTACION DE SERVICIOS"
    msgs = construir_mensajes(texto, "prestacion_de_servicios")
    contenido = msgs[0]["content"]

    # No debe aparecer la sección CRITERIOS DE REVISION
    assert "CRITERIOS DE REVISION" not in contenido
    # Debe seguir conteniendo la instrucción y el texto
    assert "Analizas un contrato sintético" in contenido
    assert "TEXTO DEL CONTRATO" in contenido


