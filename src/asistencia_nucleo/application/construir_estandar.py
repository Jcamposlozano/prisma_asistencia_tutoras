"""Caso de uso: datasets canónicos -> Estandar (merge + dedup, vía dominio)."""

from __future__ import annotations

from ..domain import estandar as dominio_estandar
from ..domain.modelos import DatasetCanonico, Estandar


class ConstruirEstandar:
    def ejecutar(self, datasets: list[DatasetCanonico], *, generado: str = "") -> Estandar:
        return dominio_estandar.merge(datasets, generado=generado)
