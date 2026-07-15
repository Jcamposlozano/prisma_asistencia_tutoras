"""Normalizacion de nombres para comparacion (dominio puro, sin I/O).

Minusculas, sin tildes (NFKD->ASCII), sin \\xa0, sin parentesis (apodos), solo
letras y espacios, espacios colapsados. Conserva el original aparte.
"""

from __future__ import annotations

import re
import unicodedata

NBSP = "\xa0"

_RE_PARENTESIS = re.compile(r"\([^)]*\)")
_RE_NO_LETRA = re.compile(r"[^a-z\s]")
_RE_ESPACIOS = re.compile(r"\s+")


def quitar_diacriticos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar(nombre: str | None) -> str:
    if nombre is None:
        return ""
    texto = str(nombre).replace(NBSP, " ")
    texto = _RE_PARENTESIS.sub(" ", texto)
    texto = quitar_diacriticos(texto)
    texto = texto.lower()
    texto = _RE_NO_LETRA.sub(" ", texto)
    return _RE_ESPACIOS.sub(" ", texto).strip()


def tokens(nombre: str | None) -> list[str]:
    norm = normalizar(nombre)
    return norm.split() if norm else []
