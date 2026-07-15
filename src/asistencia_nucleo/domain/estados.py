"""Deriva el estado canónico desde los minutos asistidos (dominio puro)."""

from __future__ import annotations

from .modelos import EstadoCanonico


def estado_por_minutos(minutos: float, presente_min: float = 60,
                       parcial_min: float = 29) -> EstadoCanonico:
    if minutos >= presente_min:
        return EstadoCanonico.PRESENTE
    if minutos >= parcial_min:
        return EstadoCanonico.PARCIAL
    return EstadoCanonico.AUSENTE
