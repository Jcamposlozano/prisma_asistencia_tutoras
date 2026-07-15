"""Casos de uso del servicio de reportes (orquestan domain + ports, sin I/O directo)."""

from __future__ import annotations

from typing import Any

from ..domain.calificaciones import (
    UMBRAL_APROBACION,
    calificacion_docente,
    media_encuesta,
    reprobados,
)
from ..ports.lectores import (
    LectorCalificacionesPort,
    LectorEncuestaPort,
    LectorEvaluacionDocentePort,
)
from ..ports.render import RenderInformeComitePort, RenderInformeFinalPort
from ..ports.repositorio import RepositorioAsistenciaPort


class CargarAsistencia:
    """estandar.json (integrador) -> repositorio relacional."""

    def __init__(self, repo: RepositorioAsistenciaPort) -> None:
        self.repo = repo

    def ejecutar(self, estandar_json: str, densificar: bool = False) -> tuple[int, int, int]:
        counts = self.repo.cargar_estandar(estandar_json)
        if densificar and hasattr(self.repo, "densificar_ausencias"):
            self.repo.densificar_ausencias()
        return counts


class GenerarInformeComite:
    """Repositorio de asistencia (+ incidencias opcionales) -> PPTX/PDF de comité."""

    def __init__(self, repo: RepositorioAsistenciaPort, render: RenderInformeComitePort) -> None:
        self.repo = repo
        self.render = render

    def ejecutar(self, salida: str, incidencias: dict[str, Any] | None = None) -> str:
        return self.render.render(
            self.repo.resumen_por_estudiante(),
            self.repo.n_sesiones(),
            salida,
            incidencias=incidencias,
        )


class ConstruirDatosFinal:
    """CSV crudos (encuesta + docente + calificaciones) -> contrato de datos del final."""

    def __init__(
        self,
        encuesta: LectorEncuestaPort,
        docente: LectorEvaluacionDocentePort,
        calificaciones: LectorCalificacionesPort,
    ) -> None:
        self.encuesta = encuesta
        self.docente = docente
        self.calificaciones = calificaciones

    def ejecutar(
        self,
        *,
        encuesta_csv: str,
        docente_csv: str,
        calificaciones_csv: str,
        profesor: str,
        programa: str = "",
        materia: str = "",
        cohorte: str = "",
        umbral: float = UMBRAL_APROBACION,
    ) -> dict[str, Any]:
        enc = self.encuesta.leer(encuesta_csv)
        doc = self.docente.leer(docente_csv, profesor)
        notas = self.calificaciones.leer(calificaciones_csv)
        medias = [p["media"] for p in enc["preguntas"]]
        no_superan = [
            {"nombre": n.nombre, "score": n.score} for n in reprobados(notas, umbral)
        ]
        return {
            "programa": programa,
            "materia": materia,
            "cohorte": cohorte,
            "profesor": profesor,
            "preguntas": enc["preguntas"],
            "docente": {
                **doc,
                "calificacion_docente": calificacion_docente(
                    [doc["clase1"], doc["clase2"], doc["clase3"]]
                ),
                "media_encuesta": media_encuesta(medias),
            },
            "incidencias_sincronas": "Ninguna",
            "comentarios": enc["comentarios"],
            "no_superan": no_superan,
            "_meta": {
                "n_respondientes": enc["n_respondientes"],
                "umbral_aprobacion": umbral,
                "nota": (
                    "medias por pregunta verificadas contra el informe original; "
                    "calificacion_docente y media_encuesta son promedios calculados "
                    "(el original usa un cálculo manual de la coordinación)."
                ),
            },
        }


class GenerarInformeFinal:
    """Contrato de datos -> documento del informe final."""

    def __init__(self, render: RenderInformeFinalPort) -> None:
        self.render = render

    def ejecutar(self, datos: dict[str, Any], salida: str) -> str:
        return self.render.render(datos, salida)
