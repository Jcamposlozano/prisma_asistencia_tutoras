"""Caso de uso: correr uno o varios extractores -> datasets canónicos."""

from __future__ import annotations

from ..domain.modelos import DatasetCanonico
from ..ports.extraccion import ExtractorPort


class Extraer:
    def __init__(self, extractores: list[ExtractorPort]) -> None:
        self.extractores = extractores

    def ejecutar(self) -> list[DatasetCanonico]:
        return [e.extraer() for e in self.extractores]
