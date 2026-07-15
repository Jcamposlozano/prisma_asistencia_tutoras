"""Parseo de la 'Duración de la reunión' de Zoom a minutos (dominio puro).

Formato: "2 h 6 min 30s", "5 min 52s", "7s", "1 h 57s", "3 h 53 min 43s".
Robusto: si ya viene un número, lo devuelve tal cual.
"""

from __future__ import annotations

import re

_H = re.compile(r"(\d+)\s*h(?![a-z])", re.IGNORECASE)
_MIN = re.compile(r"(\d+)\s*min", re.IGNORECASE)
_S = re.compile(r"(\d+)\s*s(?![a-z])", re.IGNORECASE)


def a_minutos(valor) -> float:
    """Convierte una duracion (texto Zoom o numero) a minutos (float)."""
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().lower()
    if not texto:
        return 0.0
    # Si es un numero puro (p.ej. "126.05"), usarlo directo.
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        pass
    h = _H.search(texto)
    m = _MIN.search(texto)
    s = _S.search(texto)
    horas = int(h.group(1)) if h else 0
    minutos = int(m.group(1)) if m else 0
    segundos = int(s.group(1)) if s else 0
    return horas * 60 + minutos + segundos / 60
