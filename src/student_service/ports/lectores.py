"""Ports: lectores de los CSV crudos que exporta la plataforma (encuesta,
evaluación docente, calificaciones)."""

from __future__ import annotations

from typing import Any, Protocol

from ..domain.calificaciones import NotaFinal


class LectorEncuestaPort(Protocol):
    def leer(self, path: str) -> dict[str, Any]:
        """-> {n_respondientes, preguntas:[{texto,media}], comentarios:{gusto,cambiarias}}"""
        ...


class LectorEvaluacionDocentePort(Protocol):
    def leer(self, path: str, profesor: str) -> dict[str, float]:
        """-> {clase1, clase2, clase3} (puntajes 0-100 del docente)."""
        ...


class LectorCalificacionesPort(Protocol):
    def leer(self, path: str) -> list[NotaFinal]:
        """-> nota final (Final Score) por estudiante."""
        ...
