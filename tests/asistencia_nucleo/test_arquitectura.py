"""El núcleo (domain/application/ports) no conoce infraestructura de I/O."""

from __future__ import annotations

import pathlib

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "asistencia_nucleo"


def _fuentes(*subs):
    for sub in subs:
        yield from (SRC / sub).glob("*.py")


def test_nucleo_sin_io():
    prohibidos = ("openpyxl", "import csv", "pandas")
    for f in _fuentes("domain", "application", "ports"):
        txt = f.read_text(encoding="utf-8")
        for lib in prohibidos:
            assert lib not in txt, f"{f.relative_to(SRC)} no debe usar {lib} (viola hexagonal)"


def test_domain_no_importa_capas_externas():
    for f in _fuentes("domain"):
        txt = f.read_text(encoding="utf-8")
        for capa in ("application", "adapters", "entrypoints", "ports"):
            assert f"asistencia_nucleo.{capa}" not in txt and f"..{capa}" not in txt, \
                f"{f.name} importa {capa} (el dominio debe ser puro)"
