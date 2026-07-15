"""Deduplicación por identidad canónica (dominio puro).

Una persona puede aparecer en varias filas de una sesión (varias conexiones /
dispositivos). Se suma su duración por persona canónica antes de decidir el estado.
"""

from __future__ import annotations

from collections.abc import Iterable

from .modelos import Persona


def sumar_por_persona(pares: Iterable[tuple[Persona, float]]) -> dict[str, float]:
    """{clave_persona: minutos_sumados} a partir de (Persona, minutos)."""
    total: dict[str, float] = {}
    for persona, minutos in pares:
        total[persona.clave] = total.get(persona.clave, 0.0) + float(minutos)
    return total
