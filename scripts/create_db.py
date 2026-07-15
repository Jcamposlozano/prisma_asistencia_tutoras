"""Crea la base de datos SQLite local del Reporte Materias.

Uso:
    python3 scripts/create_db.py           # solo el esquema (vacía)
    python3 scripts/create_db.py --demo    # esquema + demo de asistencias procesadas

Genera student_service.db en la raíz del proyecto, lista para abrir en DBeaver.
Solo librería estándar: sin dependencias externas.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "student_service.db"
SCHEMA = ROOT / "scripts" / "schema.sql"
SEED_DEMO = ROOT / "scripts" / "seed_demo_asistencias.sql"


def main() -> None:
    with_demo = "--demo" in sys.argv

    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Base anterior eliminada: {DB_PATH.name}")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        print(f"Esquema creado desde {SCHEMA.name}")

        if with_demo:
            conn.executescript(SEED_DEMO.read_text(encoding="utf-8"))
            print(f"Demo cargado desde {SEED_DEMO.name}")

        conn.commit()

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        print(f"\nBase de datos: {DB_PATH}")
        for (table,) in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  - {table}: {count} filas")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
