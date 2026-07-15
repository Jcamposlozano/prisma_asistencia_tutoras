"""Reglas puras de calificaciones (sin I/O).

Los estudiantes superan la asignatura con nota >= UMBRAL_APROBACION (70,
según el proceso de las coordinadoras: "superan la asignatura con 70").
"""

from __future__ import annotations

from dataclasses import dataclass

UMBRAL_APROBACION = 70.0


@dataclass(frozen=True)
class NotaFinal:
    nombre: str
    score: float


def reprobados(notas: list[NotaFinal], umbral: float = UMBRAL_APROBACION) -> list[NotaFinal]:
    """Estudiantes que no superan la materia (score < umbral), en orden de entrada."""
    return [n for n in notas if n.score < umbral]


def calificacion_docente(clases: list[float]) -> float:
    """Promedio de los puntajes de clase (0-100) expresado en escala /5.

    NOTA: el informe original trae una cifra calculada a mano por la coordinación
    (p.ej. 4,56) cuya fórmula no está en los archivos; esta es la versión
    transparente y reproducible. Calibrar cuando la coordinación comparta su fórmula.
    """
    if not clases:
        return 0.0
    return round(sum(clases) / len(clases) / 20.0, 2)


def media_encuesta(medias_preguntas: list[float]) -> float:
    """Promedio simple de las medias por pregunta (misma nota de calibración)."""
    if not medias_preguntas:
        return 0.0
    return round(sum(medias_preguntas) / len(medias_preguntas), 2)
