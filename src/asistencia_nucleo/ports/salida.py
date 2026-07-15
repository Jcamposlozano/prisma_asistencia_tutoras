"""Puertos de salida: exportar el estándar (JSON) y renderizar a un formato."""

from __future__ import annotations

from typing import Protocol

from ..domain.modelos import Estandar


class EstandarExporterPort(Protocol):
    def exportar(self, estandar: Estandar, salida: str) -> None:
        ...


class RendererPort(Protocol):
    """Toma el estándar y produce un formato concreto (detalle, consolidado, ...)."""

    def render(self, estandar: Estandar, salida: str) -> None:
        ...
