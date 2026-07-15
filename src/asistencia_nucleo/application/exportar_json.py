"""Caso de uso: exportar el estándar a JSON (vía EstandarExporterPort)."""

from __future__ import annotations

from ..domain.modelos import Estandar
from ..ports.salida import EstandarExporterPort


class ExportarJson:
    def __init__(self, exporter: EstandarExporterPort) -> None:
        self.exporter = exporter

    def ejecutar(self, estandar: Estandar, salida: str) -> None:
        self.exporter.exportar(estandar, salida)
