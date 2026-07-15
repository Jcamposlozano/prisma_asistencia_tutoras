"""Adapters: lectores de los CSV crudos de la plataforma (encuesta, evaluación
docente, calificaciones). Todo el I/O vive aquí; las reglas en domain/."""

from __future__ import annotations

import csv
import re
import unicodedata
from typing import Any

from ..domain.calificaciones import NotaFinal
from ..domain.encuesta import PREGUNTAS, limpiar_comentario, media_pregunta

# columnas de la encuesta (export "Survey Student Analysis Report", delimitado por ;)
_COLS_ESCALA = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]
_COL_GUSTO, _COL_CAMBIA = 29, 31


def _leer_csv(path: str, delimiter: str) -> list[list[str]]:
    """Lee un CSV probando encodings comunes (utf-8-sig, cp1252, latin-1)."""
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, newline="", encoding=enc) as fh:
                return list(csv.reader(fh, delimiter=delimiter))
        except UnicodeDecodeError:
            continue
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        return list(csv.reader(fh, delimiter=delimiter))


def _sniff_delim(path: str) -> str:
    head = open(path, encoding="latin-1").readline()
    return ";" if head.count(";") > head.count(",") else ","


def _num(x: Any) -> float | None:
    try:
        return float(str(x).replace(",", "."))
    except (ValueError, TypeError):
        return None


def _sin_tildes(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    ).lower()


class LectorEncuestaCsv:
    def leer(self, path: str) -> dict[str, Any]:
        rows = _leer_csv(path, ";")
        data = rows[2:]  # fila 0 = ColumnN, fila 1 = textos de pregunta
        n = len(data)
        preguntas = [
            {
                "texto": texto,
                "media": media_pregunta([r[c] for r in data if c < len(r)], n),
            }
            for texto, c in zip(PREGUNTAS, _COLS_ESCALA)
        ]
        gusto = [
            limpiar_comentario(r[_COL_GUSTO])
            for r in data
            if _COL_GUSTO < len(r) and limpiar_comentario(r[_COL_GUSTO])
        ]
        cambia = [
            limpiar_comentario(r[_COL_CAMBIA])
            for r in data
            if _COL_CAMBIA < len(r) and limpiar_comentario(r[_COL_CAMBIA])
        ]
        return {
            "n_respondientes": n,
            "preguntas": preguntas,
            "comentarios": {"gusto": gusto, "cambiarias": cambia},
        }


class LectorEvaluacionDocenteCsv:
    def leer(self, path: str, profesor: str) -> dict[str, float]:
        rows = _leer_csv(path, _sniff_delim(path))
        hdr = rows[0]
        cols_clase = [i for i, c in enumerate(hdr) if re.search(r"clase\s*\d.*docenc", c, re.I)]
        ap = _sin_tildes(profesor)
        fila = None
        for r in rows[2:]:  # rows[1] = Points Possible
            if (
                r
                and r[0].strip()
                and any(tok in _sin_tildes(r[0]) for tok in ap.split() if len(tok) > 3)
            ):
                fila = r
                break
        clases = [_num(fila[i]) if fila and i < len(fila) else None for i in cols_clase][:3]
        clases = [c if c is not None else 100.0 for c in clases]
        while len(clases) < 3:
            clases.append(100.0)
        return {"clase1": clases[0], "clase2": clases[1], "clase3": clases[2]}


class LectorCalificacionesCsv:
    def leer(self, path: str) -> list[NotaFinal]:
        rows = _leer_csv(path, _sniff_delim(path))
        hdr = rows[0]
        idx = max(
            (i for i, c in enumerate(hdr) if c.strip().lower() == "final score"), default=None
        )
        notas: list[NotaFinal] = []
        for r in rows[1:]:
            nombre = (r[0] or "").strip()
            if not nombre or nombre.lower().startswith("points possible"):
                continue
            score = _num(r[idx]) if idx is not None and idx < len(r) else None
            if score is not None:
                notas.append(NotaFinal(nombre=nombre, score=round(score, 2)))
        return notas
