"""Puerto de entrada: un extractor normaliza UNA fuente al modelo canónico."""

from __future__ import annotations

from typing import Protocol

from ..domain.modelos import DatasetCanonico


class ExtractorPort(Protocol):
    def extraer(self) -> DatasetCanonico:
        ...
