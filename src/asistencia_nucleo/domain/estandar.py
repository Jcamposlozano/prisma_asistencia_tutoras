"""Construcción del estándar a partir de datasets + consultas puras sobre él."""

from __future__ import annotations

from .modelos import Asistencia, DatasetCanonico, Estandar, Persona


def _completar(base: Persona, otra: Persona) -> None:
    """Rellena campos vacíos de `base` con los de `otra` (mismo id)."""
    if not base.correo and otra.correo:
        base.correo = otra.correo
        base.correo_norm = otra.correo_norm
    for attr in ("programa", "cohorte"):
        if not getattr(base, attr) and getattr(otra, attr):
            setattr(base, attr, getattr(otra, attr))


def merge(datasets: list[DatasetCanonico], *, generado: str = "") -> Estandar:
    """Une varios datasets en un Estandar: dedup de personas/sesiones por id."""
    personas: dict[str, Persona] = {}
    for ds in datasets:
        for p in ds.personas:
            if p.id in personas:
                _completar(personas[p.id], p)
            else:
                personas[p.id] = p

    sesiones: dict[str, object] = {}
    for ds in datasets:
        for s in ds.sesiones:
            sesiones.setdefault(s.id, s)

    asistencias: list[Asistencia] = []
    for ds in datasets:
        asistencias.extend(ds.asistencias)

    meta = {
        "generado": generado,
        "fuentes": [ds.fuente for ds in datasets],
        "n_personas": len(personas),
        "n_sesiones": len(sesiones),
        "n_asistencias": len(asistencias),
        "sin_match": sum(len(ds.sin_match) for ds in datasets),
        "filtrados": sum(len(ds.filtrados) for ds in datasets),
    }
    return Estandar(meta=meta, personas=list(personas.values()),
                    sesiones=list(sesiones.values()), asistencias=asistencias)


def indice_asistencias(est: Estandar) -> dict[tuple[str, str], Asistencia]:
    """{(persona_id, sesion_id): Asistencia} para consultas rápidas (renderers)."""
    return {(a.persona_id, a.sesion_id): a for a in est.asistencias}
