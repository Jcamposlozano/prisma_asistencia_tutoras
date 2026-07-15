"""Extractor: un participants_*.csv de Zoom -> DatasetCanonico.

Sin roster externo: las personas son los propios participantes (filtrando host/bots
y rescatando dispositivos). El estado se deriva de los minutos (dedup por persona).
"""

from __future__ import annotations

import os

from ...domain.estados import estado_por_minutos
from ...domain.modelos import Asistencia, DatasetCanonico, Persona, Sesion
from ...domain.normalizar import normalizar
from ._zoom_common import clasificar, leer_csv_zoom


class ZoomCsvExtractor:
    def __init__(self, path: str, *, programa: str = "", cohorte: str = "",
                 presente_min: float = 60, parcial_min: float = 29) -> None:
        self.path = path
        self.programa = programa
        self.cohorte = cohorte
        self.presente_min = presente_min
        self.parcial_min = parcial_min

    def extraer(self) -> DatasetCanonico:
        filas = leer_csv_zoom(self.path)
        base = os.path.splitext(os.path.basename(self.path))[0]
        fechas = [f["entrada"] for f in filas if f["entrada"]]
        fecha = min(fechas).isoformat() if fechas else ""
        sesion = Sesion(id=f"zoom:{base}", programa=self.programa, cohorte=self.cohorte,
                        etiqueta=fecha or base, fecha=fecha)

        acc: dict[str, dict] = {}
        filtrados: list[dict] = []
        for f in filas:
            cat, nombre_match = clasificar(f["nombre"], f["invitado"], f["correo"])
            if cat in ("HOST", "BOT") or (cat == "DISPOSITIVO" and not nombre_match):
                filtrados.append({"nombre": f["nombre"], "categoria": cat, "minutos": f["minutos"]})
                continue
            clave = f["correo"].strip().lower() or normalizar(nombre_match)
            reg = acc.setdefault(clave, {"nombre": nombre_match, "correo": f["correo"], "min": 0.0})
            reg["min"] += f["minutos"]

        personas: list[Persona] = []
        asistencias: list[Asistencia] = []
        for reg in acc.values():
            p = Persona(nombre=reg["nombre"], correo=reg["correo"],
                        programa=self.programa, cohorte=self.cohorte)
            personas.append(p)
            asistencias.append(Asistencia(
                persona_id=p.id, sesion_id=sesion.id,
                estado=estado_por_minutos(reg["min"], self.presente_min, self.parcial_min),
                minutos=round(reg["min"], 1), origen="zoom-csv", nombre_origen=reg["nombre"]))

        return DatasetCanonico(fuente="zoom-csv", personas=personas, sesiones=[sesion],
                               asistencias=asistencias, filtrados=filtrados)
