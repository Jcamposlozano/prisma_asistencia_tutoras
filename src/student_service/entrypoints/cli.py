"""Entrypoint CLI del servicio de reportes: `reporte <comando>`.

Flujo completo (ver README):
  1. reporte cargar      estandar.json -> SQLite            (asistencia)
  2. reporte comite      SQLite (+ datos.json) -> PPTX/PDF  (informe comité)
  3. reporte datos-final CSV crudos -> datos.json           (encuesta/docente/notas)
  4. reporte final       datos.json -> HTML/PDF             (informe final)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..adapters.lectores_csv import (
    LectorCalificacionesCsv,
    LectorEncuestaCsv,
    LectorEvaluacionDocenteCsv,
)
from ..adapters.salida.html_final import HtmlInformeFinal
from ..adapters.salida.pptx_comite import PptxInformeComite
from ..adapters.sqlite_repo import SqliteRepositorioAsistencia
from ..application.casos_uso import (
    CargarAsistencia,
    ConstruirDatosFinal,
    GenerarInformeComite,
    GenerarInformeFinal,
)


def cmd_cargar(a) -> int:
    repo = SqliteRepositorioAsistencia(a.db)
    p, s, asis = CargarAsistencia(repo).ejecutar(a.estandar, densificar=a.densificar)
    print(f"{a.db}: {p} personas · {s} sesiones · {asis} asistencias")
    return 0


def cmd_comite(a) -> int:
    repo = SqliteRepositorioAsistencia(a.db)
    render = PptxInformeComite(a.plantilla, exportar_pdf=not a.solo_pptx)
    inc = json.loads(Path(a.datos).read_text(encoding="utf-8")) if a.datos else None
    out = GenerarInformeComite(repo, render).ejecutar(a.salida, incidencias=inc)
    print(f"comité -> {out}")
    return 0


def cmd_datos_final(a) -> int:
    caso = ConstruirDatosFinal(
        LectorEncuestaCsv(), LectorEvaluacionDocenteCsv(), LectorCalificacionesCsv()
    )
    datos = caso.ejecutar(
        encuesta_csv=a.encuesta,
        docente_csv=a.docente,
        calificaciones_csv=a.calificaciones,
        profesor=a.profesor,
        programa=a.programa,
        materia=a.materia,
        cohorte=a.cohorte,
        umbral=a.umbral,
    )
    Path(a.salida).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    medias = [p["media"] for p in datos["preguntas"]]
    print(f"datos -> {a.salida}")
    print(f"  respondientes={datos['_meta']['n_respondientes']}  medias={medias}")
    print(f"  no_superan: {[r['nombre'] for r in datos['no_superan']]}")
    return 0


def cmd_final(a) -> int:
    datos = json.loads(Path(a.datos).read_text(encoding="utf-8"))
    out = GenerarInformeFinal(HtmlInformeFinal()).ejecutar(datos, a.salida)
    print(f"final -> {out}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="reporte",
        description="Genera los informes de la maestría (comité curricular e informe final).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("cargar", help="Carga un estandar.json del integrador a SQLite.")
    c.add_argument("--estandar", required=True)
    c.add_argument("--db", default="reporte_asistencia.db")
    c.add_argument("--densificar", action="store_true",
                   help="AUSENTE explícito para (persona, sesión) sin registro (fuentes sin roster).")
    c.set_defaults(func=cmd_cargar)

    c = sub.add_parser("comite", help="Genera el informe para comité curricular (PPTX+PDF).")
    c.add_argument("--db", default="reporte_asistencia.db")
    c.add_argument("--plantilla", required=True,
                   help="PPTX original de la coordinación (local, contiene PII: no va al repo).")
    c.add_argument("--datos", help="JSON de datos-final con 'no_superan' (lámina de incidencias).")
    c.add_argument("--salida", default="informe_comite.pptx")
    c.add_argument("--solo-pptx", action="store_true")
    c.set_defaults(func=cmd_comite)

    c = sub.add_parser("datos-final", help="CSV crudos -> JSON de datos del informe final.")
    c.add_argument("--encuesta", required=True)
    c.add_argument("--docente", required=True)
    c.add_argument("--calificaciones", required=True)
    c.add_argument("--profesor", required=True)
    c.add_argument("--programa", default="")
    c.add_argument("--materia", default="")
    c.add_argument("--cohorte", default="")
    c.add_argument("--umbral", type=float, default=70.0)
    c.add_argument("--salida", default="datos_final.json")
    c.set_defaults(func=cmd_datos_final)

    c = sub.add_parser("final", help="Genera el informe final (HTML+PDF) desde el JSON de datos.")
    c.add_argument("--datos", required=True)
    c.add_argument("--salida", default="informe_final")
    c.set_defaults(func=cmd_final)
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
