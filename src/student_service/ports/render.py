"""Ports: renderers de los dos entregables (informe comité e informe final)."""

from __future__ import annotations

from typing import Any, Protocol

from ..domain.asistencia import ResumenEstudiante


class RenderInformeComitePort(Protocol):
    def render(
        self,
        resumenes: list[ResumenEstudiante],
        n_sesiones: int,
        salida: str,
        incidencias: dict[str, Any] | None = None,
    ) -> str:
        """Genera el informe para comité (PPTX [+PDF]). Devuelve la ruta escrita."""
        ...


class RenderInformeFinalPort(Protocol):
    def render(self, datos: dict[str, Any], salida: str) -> str:
        """Genera el informe final (HTML+PDF) desde el contrato de datos. Devuelve la ruta."""
        ...
