"""Adapter de salida: exporta el estándar a un archivo JSON."""

from __future__ import annotations

import logging

from ...domain.modelos import Estandar

log = logging.getLogger(__name__)


class JsonExporter:
    def exportar(self, estandar: Estandar, salida: str) -> None:
        with open(salida, "w", encoding="utf-8") as f:
            f.write(estandar.to_json())
        log.info("Estándar JSON escrito en %s", salida)
