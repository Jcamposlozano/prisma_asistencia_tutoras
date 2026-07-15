"""Application con un ExtractorPort falso (in-memory): testabilidad hexagonal."""

from __future__ import annotations

from asistencia_nucleo.application.construir_estandar import ConstruirEstandar
from asistencia_nucleo.application.extraer import Extraer
from asistencia_nucleo.domain.modelos import Asistencia, DatasetCanonico, EstadoCanonico, Sesion
from .conftest import persona


class FakeExtractor:
    def __init__(self, ds):
        self._ds = ds

    def extraer(self):
        return self._ds


def test_extraer_y_construir_merge():
    p = persona("Ada", "ada@x.com")
    s = Sesion(id="s1", etiqueta="1V")
    ds1 = DatasetCanonico(fuente="f1", personas=[p], sesiones=[s],
                          asistencias=[Asistencia(p.id, s.id, EstadoCanonico.PRESENTE)])
    ds2 = DatasetCanonico(fuente="f2", personas=[persona("Bob", "bob@x.com")])

    datasets = Extraer([FakeExtractor(ds1), FakeExtractor(ds2)]).ejecutar()
    est = ConstruirEstandar().ejecutar(datasets, generado="hoy")

    assert est.meta["n_personas"] == 2
    assert est.meta["n_sesiones"] == 1
    assert est.meta["n_asistencias"] == 1
    assert est.meta["fuentes"] == ["f1", "f2"]
    assert est.meta["generado"] == "hoy"
