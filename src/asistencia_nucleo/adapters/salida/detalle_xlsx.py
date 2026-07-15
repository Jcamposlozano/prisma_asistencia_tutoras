"""Renderer 'detalle': una fila por asistencia (formato largo)."""

from __future__ import annotations

import logging

from openpyxl import Workbook
from openpyxl.styles import Font

from ...domain.modelos import Estandar

log = logging.getLogger(__name__)


class DetalleXlsxRenderer:
    def render(self, estandar: Estandar, salida: str) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = "detalle"
        personas = {p.id: p for p in estandar.personas}
        sesiones = {s.id: s for s in estandar.sesiones}

        heads = ["Persona", "Correo", "Programa", "Cohorte", "Sesión", "Fecha",
                 "Módulo", "Estado", "Minutos", "Origen"]
        ws.append(heads)
        for c in ws[1]:
            c.font = Font(bold=True)

        for a in estandar.asistencias:
            p = personas.get(a.persona_id)
            s = sesiones.get(a.sesion_id)
            ws.append([
                p.nombre if p else a.persona_id,
                p.correo if p else "",
                p.programa if p else "",
                p.cohorte if p else "",
                s.etiqueta if s else a.sesion_id,
                s.fecha if s else "",
                s.modulo if s else "",
                a.estado.value,
                a.minutos,
                a.origen,
            ])
        ws.column_dimensions["A"].width = 34
        wb.save(salida)
        log.info("Detalle escrito en %s (%d filas)", salida, len(estandar.asistencias))
