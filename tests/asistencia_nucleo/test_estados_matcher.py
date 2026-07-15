from asistencia_nucleo.domain.estados import estado_por_minutos
from asistencia_nucleo.domain.matcher import matchear
from asistencia_nucleo.domain.modelos import EstadoCanonico, Nivel
from .conftest import persona


def test_estado_por_minutos():
    assert estado_por_minutos(90) is EstadoCanonico.PRESENTE
    assert estado_por_minutos(60) is EstadoCanonico.PRESENTE
    assert estado_por_minutos(45) is EstadoCanonico.PARCIAL
    assert estado_por_minutos(29) is EstadoCanonico.PARCIAL
    assert estado_por_minutos(10) is EstadoCanonico.AUSENTE


def _roster():
    return [persona("AGUILAR CAMPOS, JORDAN", "a@uide.edu.ec"),
            persona("ANDRADE NARVAEZ, RICARDO", "r@uide.edu.ec")]


def test_matcher_email_first():
    m = matchear("nombre irreconocible", "a@uide.edu.ec", _roster())
    assert m.nivel is Nivel.AUTO
    assert m.persona.correo == "a@uide.edu.ec"


def test_matcher_por_nombre_subconjunto():
    m = matchear("AGUILAR CAMPOS JORDAN", "", _roster())
    assert m.nivel is Nivel.AUTO
    assert m.persona.correo == "a@uide.edu.ec"


def test_matcher_externo_sin_match():
    m = matchear("Fulano Externo", "x@otro.com", _roster())
    assert m.nivel is Nivel.SIN_MATCH
