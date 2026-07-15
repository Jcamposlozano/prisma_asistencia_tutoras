"""Reglas puras de asistencia para los informes (sin I/O).

Vocabulario del informe de comité (heredado del formato de las coordinadoras):
  A  = PRESENTE      NP = AUSENTE      D = PARCIAL
  "No asiste o tiempo incompleto" = NP + D
"""

from __future__ import annotations

from dataclasses import dataclass

# estado canónico -> (letra de la matriz P/D/o, clase visual)
CODIGO_ESTADO: dict[str, tuple[str, str]] = {
    "PRESENTE": ("P", "p"),
    "PARCIAL": ("D", "d"),
    "AUSENTE": ("o", "o"),
    "EXCUSA": ("E", "e"),
    "DESCONOCIDO": ("?", "x"),
}


@dataclass(frozen=True)
class ResumenEstudiante:
    """Conteos de un estudiante en el módulo (fila de la matriz del comité)."""

    nombre: str
    presentes: int  # A
    ausentes: int  # NP
    parciales: int  # D

    @property
    def no_asiste_o_incompleto(self) -> int:
        return self.ausentes + self.parciales


def distribucion_por_presentes(
    resumenes: list[ResumenEstudiante], n_sesiones: int
) -> dict[int, int]:
    """{k: nº de estudiantes que asistieron a k sesiones}, k = n_sesiones..0."""
    dist = {k: 0 for k in range(n_sesiones + 1)}
    for r in resumenes:
        dist[r.presentes] += 1
    return dist


def porcentaje(cuenta: int, total: int, decimales: int = 2) -> float:
    return round(100.0 * cuenta / total, decimales) if total else 0.0


def no_asistentes(resumenes: list[ResumenEstudiante]) -> list[str]:
    """Nombres con 0 sesiones PRESENTE (criterio del informe original)."""
    return sorted((r.nombre for r in resumenes if r.presentes == 0), key=str.casefold)
