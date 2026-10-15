"""Alta local de usuarios autorizados (RF-00.5).

No existe registro público (RF-00.2): las cuentas las crea quien opere el
servidor ejecutando este script en la máquina local.

Uso
---
    python backend/crear_usuario.py revisor
    python backend/crear_usuario.py revisor --contrasena "..."  # solo pruebas
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.auth import crear_usuario  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Da de alta un usuario autorizado del MVP."
    )
    parser.add_argument("usuario", help="Nombre de usuario (único).")
    parser.add_argument(
        "--contrasena",
        default=None,
        help="Si se omite, se pide sin mostrarla en pantalla.",
    )
    parser.add_argument(
        "--bd",
        default=None,
        help="Ruta SQLite (por defecto, la de la aplicación).",
    )
    args = parser.parse_args()

    clave = args.contrasena
    if clave is None:
        clave = getpass.getpass("Contraseña: ")

    try:
        crear_usuario(args.usuario, clave, args.bd)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f'Usuario "{args.usuario.strip()}" creado.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
