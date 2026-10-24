"""Persistencia y consulta del historial de analisis (RF-04).

El modulo concentra las operaciones SQL sobre la tabla ``analisis``. No toma
decisiones de autenticacion: recibe el ``usuario_id`` ya validado por la
capa de sesion de ``main.py``. Nunca guarda el texto del contrato, el
prompt ni el archivo original.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import auth


def guardar_analisis(
    *,
    usuario_id: int,
    tipo_confirmado: str,
    hallazgos: list[dict[str, Any]],
    ruta: str | Path | None = None,
) -> None:
    """Persiste metadatos y hallazgos de un analisis exitoso.

    Se llama solo despues de validar las citas y completar el analisis con
    exito. Nunca se guarda el texto del contrato, el prompt ni el archivo.
    """
    destino = auth.init_bd(ruta)
    conexion = sqlite3.connect(str(destino))
    conexion.row_factory = sqlite3.Row
    try:
        conexion.execute(
            "INSERT INTO analisis (usuario_id, fecha, tipo_confirmado, "
            "num_hallazgos, hallazgos) VALUES (?, ?, ?, ?, ?)",
            (
                usuario_id,
                datetime.now(timezone.utc).isoformat(),
                tipo_confirmado,
                len(hallazgos),
                json.dumps(hallazgos, ensure_ascii=False),
            ),
        )
        conexion.commit()
    finally:
        conexion.close()


def listar_historial(
    usuario_id: int, ruta: str | Path | None = None
) -> list[dict[str, Any]]:
    """Devuelve los analisis del usuario, mas reciente primero.

    El filtrado por ``usuario_id`` se hace en SQL con parametro, de modo que
    un usuario nunca ve registros de otro.
    """
    destino = auth.init_bd(ruta)
    conexion = sqlite3.connect(str(destino))
    conexion.row_factory = sqlite3.Row
    try:
        filas = conexion.execute(
            "SELECT id, fecha, tipo_confirmado, num_hallazgos, hallazgos "
            "FROM analisis WHERE usuario_id = ? "
            "ORDER BY fecha DESC, id DESC",
            (usuario_id,),
        ).fetchall()
    finally:
        conexion.close()

    registros: list[dict[str, Any]] = []
    for fila in filas:
        registros.append(
            {
                "id": fila["id"],
                "fecha": fila["fecha"],
                "tipo_confirmado": fila["tipo_confirmado"],
                "num_hallazgos": fila["num_hallazgos"],
                "hallazgos": json.loads(fila["hallazgos"]),
            }
        )
    return registros
