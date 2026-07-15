from asistencia_nucleo.domain.estandar import indice_asistencias, merge
from asistencia_nucleo.domain.modelos import (
    Asistencia,
    DatasetCanonico,
    EstadoCanonico,
    Estandar,
    Sesion,
)
from .conftest import persona


def test_persona_id_correo_o_slug():
    assert persona("Juan Pérez", "j@x.com").id == "j@x.com"
    assert persona("Juan Pérez").id == "juan-perez"


def test_estandar_round_trip_json():
    p = persona("Ada Lovelace", "ada@x.com", programa="X", cohorte="C1")
    s = Sesion(id="s1", etiqueta="1V", fecha="2026-06-09")
    a = Asistencia(p.id, s.id, EstadoCanonico.PRESENTE, minutos=95.0, origen="zoom-csv", nombre_origen="Ada")
    est = Estandar(meta={"generado": "2026-07-09"}, personas=[p], sesiones=[s], asistencias=[a])
    est2 = Estandar.from_json(est.to_json())
    assert est2.personas[0].id == "ada@x.com"
    assert est2.asistencias[0].estado is EstadoCanonico.PRESENTE
    assert est2.sesiones[0].fecha == "2026-06-09"
    assert est2.to_dict() == est.to_dict()


def test_merge_dedup_personas_por_id_y_completa_campos():
    p1 = persona("Ada", "ada@x.com")                       # sin programa
    p2 = persona("Ada", "ada@x.com", programa="X")         # mismo id, con programa
    ds1 = DatasetCanonico(fuente="a", personas=[p1])
    ds2 = DatasetCanonico(fuente="b", personas=[p2])
    est = merge([ds1, ds2], generado="hoy")
    assert len(est.personas) == 1
    assert est.personas[0].programa == "X"                 # se completó el campo vacío
    assert est.meta["fuentes"] == ["a", "b"]


def test_indice_asistencias():
    p = persona("Ada", "ada@x.com")
    a = Asistencia(p.id, "s1", EstadoCanonico.AUSENTE)
    est = Estandar(personas=[p], sesiones=[Sesion(id="s1")], asistencias=[a])
    idx = indice_asistencias(est)
    assert idx[("ada@x.com", "s1")].estado is EstadoCanonico.AUSENTE
