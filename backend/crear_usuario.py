"""Alta y mantenimiento local de usuarios autorizados (RF-00.5).

No existe registro público (RF-00.2): las cuentas las crea y mantiene quien
opere el servidor ejecutando este script en la máquina local. No hay ruta
HTTP para estas operaciones.

Uso
---
    python backend/crear_usuario.py revisor
    python backend/crear_usuario.py revisor --contrasena "..."  # solo pruebas
    python backend/crear_usuario.py revisor --reestablecer
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.auth import crear_usuario, reestablecer_contrasena  # noqa: E402


def _pedir_clave_confirmada() -> str:
    """Pide la contraseña dos veces sin mostrarla; deben coincidir."""
    primera = getpass.getpass("Contraseña nueva: ")
    segunda = getpass.getpass("Confirma la contraseña nueva: ")
    if primera != segunda:
        raise ValueError("Las contraseñas no coinciden.")
    return primera


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Da de alta un usuario autorizado del MVP o "
        "reestablece su contraseña."
    )
    parser.add_argument("usuario", help="Nombre de usuario (único).")
    parser.add_argument(
        "--contrasena",
        default=None,
        help="Si se omite, se pide sin mostrarla en pantalla.",
    )
    parser.add_argument(
        "--reestablecer",
        action="store_true",
        help="Cambia la contraseña de un usuario existente y revoca "
        "sus sesiones activas.",
    )
    parser.add_argument(
        "--bd",
        default=None,
        help="Ruta SQLite (por defecto, la de la aplicación).",
    )
    args = parser.parse_args()

    try:
        if args.reestablecer:
            if args.contrasena is not None:
                clave = args.contrasena
            else:
                clave = _pedir_clave_confirmada()
            reestablecer_contrasena(args.usuario, clave, args.bd)
            print(
                f'Contraseña de "{args.usuario.strip()}" actualizada; '
                "sus sesiones activas quedaron revocadas."
            )
            return 0

        clave = args.contrasena
        if clave is None:
            clave = getpass.getpass("Contraseña: ")
        crear_usuario(args.usuario, clave, args.bd)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f'Usuario "{args.usuario.strip()}" creado.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
