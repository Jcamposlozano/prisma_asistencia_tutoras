"""Caso de uso: renderizar el estándar a un formato (vía RendererPort)."""

from __future__ import annotations

from ..domain.modelos import Estandar
from ..ports.salida import RendererPort


class Renderizar:
    def __init__(self, renderer: RendererPort) -> None:
        self.renderer = renderer

    def ejecutar(self, estandar: Estandar, salida: str) -> None:
        self.renderer.render(estandar, salida)
