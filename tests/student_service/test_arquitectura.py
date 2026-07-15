"""La arquitectura hexagonal se cumple: domain/application/ports no tocan I/O."""

import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "student_service"

PROHIBIDOS = re.compile(
    r"^\s*(?:import|from)\s+(csv|sqlite3|pptx|subprocess|requests|urllib)\b", re.M
)


def _archivos(capa: str):
    return list((SRC / capa).rglob("*.py"))


def test_capas_puras_sin_io():
    for capa in ("domain", "application", "ports"):
        for f in _archivos(capa):
            contenido = f.read_text(encoding="utf-8")
            m = PROHIBIDOS.search(contenido)
            assert not m, f"{f.relative_to(SRC)} importa I/O ({m.group(1)}) en capa {capa}"


def test_domain_no_importa_de_otras_capas():
    for f in _archivos("domain"):
        contenido = f.read_text(encoding="utf-8")
        assert "from ..adapters" not in contenido
        assert "from ..application" not in contenido
        assert "from ..entrypoints" not in contenido
