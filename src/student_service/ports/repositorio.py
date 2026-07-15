"""Port: repositorio de asistencia (el estándar canónico aterrizado a una base)."""

from __future__ import annotations

from typing import Protocol

from ..domain.asistencia import ResumenEstudiante


class RepositorioAsistenciaPort(Protocol):
    """Persiste el estandar.json del integrador y responde las consultas del informe."""

    def cargar_estandar(self, estandar_json: str) -> tuple[int, int, int]:
        """Carga personas/sesiones/asistencias. Devuelve (n_personas, n_sesiones, n_asistencias)."""
        ...

    def n_sesiones(self) -> int: ...

    def resumen_por_estudiante(self) -> list[ResumenEstudiante]:
        """Conteos A/NP/D por estudiante, ordenado por nombre (matriz del comité)."""
        ...
