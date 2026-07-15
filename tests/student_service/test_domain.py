"""Tests del dominio puro del servicio de reportes."""

from student_service.domain.asistencia import (
    ResumenEstudiante,
    distribucion_por_presentes,
    no_asistentes,
    porcentaje,
)
from student_service.domain.calificaciones import NotaFinal, calificacion_docente, reprobados
from student_service.domain.encuesta import limpiar_comentario, media_pregunta, valor_respuesta


def test_valor_respuesta_mapeo_calibrado():
    # calibrado contra el informe original ERC10
    assert valor_respuesta("5 - Excelente") == 5
    assert valor_respuesta("4 - De acuerdo") == 4
    assert valor_respuesta("3 - Aceptable") == 3
    assert valor_respuesta("Verdadero") == 5
    assert valor_respuesta("Falso") == 0
    assert valor_respuesta("") == 0  # blank cuenta 0 en el denominador


def test_media_pregunta_blank_cuenta_en_denominador():
    # 36 Verdadero + 1 blank sobre 37 -> 4.86 (la media exacta del original, Q2)
    respuestas = ["Verdadero"] * 36 + [""]
    assert media_pregunta(respuestas, 37) == 4.86


def test_limpiar_comentario_recorta_suspensivos():
    assert limpiar_comentario("La metodología…  ") == "La metodología"


def test_reprobados_umbral_70():
    notas = [NotaFinal("A", 0.0), NotaFinal("B", 32.79), NotaFinal("C", 82.0)]
    assert [n.nombre for n in reprobados(notas)] == ["A", "B"]


def test_calificacion_docente_escala_sobre_5():
    assert calificacion_docente([100.0, 100.0, 100.0]) == 5.0


def _resumenes():
    return [
        ResumenEstudiante("ANA", presentes=6, ausentes=0, parciales=0),
        ResumenEstudiante("BETO", presentes=0, ausentes=6, parciales=0),
        ResumenEstudiante("CARLA", presentes=0, ausentes=5, parciales=1),
    ]


def test_distribucion_y_no_asistentes():
    dist = distribucion_por_presentes(_resumenes(), 6)
    assert dist[6] == 1 and dist[0] == 2
    # criterio del original: 0 presentes = no asiste (aunque tenga un parcial)
    assert no_asistentes(_resumenes()) == ["BETO", "CARLA"]


def test_no_asiste_o_incompleto_es_np_mas_d():
    r = ResumenEstudiante("X", presentes=1, ausentes=3, parciales=2)
    assert r.no_asiste_o_incompleto == 5


def test_porcentaje():
    assert porcentaje(5, 38) == 13.16
