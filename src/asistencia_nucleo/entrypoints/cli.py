"""Entrypoint CLI: `nucleo extraer ...` y `nucleo render ...`."""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import logging
import os
import sys

from ..adapters.extractores.erc_xlsm import ErcXlsmExtractor
from ..adapters.extractores.master_xlsx import MasterXlsxExtractor
from ..adapters.extractores.matriz_dir import MatrizDirExtractor
from ..adapters.extractores.zoom_csv import ZoomCsvExtractor
from ..adapters.salida.consolidado_xlsx import ConsolidadoXlsxRenderer
from ..adapters.salida.detalle_xlsx import DetalleXlsxRenderer
from ..adapters.salida.json_exporter import JsonExporter
from ..application.construir_estandar import ConstruirEstandar
from ..application.exportar_json import ExportarJson
from ..application.extraer import Extraer
from ..application.renderizar import Renderizar
from ..domain.modelos import Estandar
from ..shared.config import load_config


def _buscar_listado(carpeta: str) -> str | None:
    for parent in (carpeta, os.path.dirname(os.path.normpath(carpeta))):
        hits = glob.glob(os.path.join(parent, "Listado*.xlsx"))
        if hits:
            return hits[0]
    return None


def _crear_extractor(tipo: str, ruta: str, args, cfg):
    pm, pc = cfg["umbrales"]["presente_min"], cfg["umbrales"]["parcial_min"]
    ua, ur = cfg["matching"]["umbral_auto"], cfg["matching"]["umbral_revisar"]
    tipo = tipo.lower()
    if tipo == "zoom":
        return ZoomCsvExtractor(ruta, programa=args.programa or "", cohorte=args.cohorte or "",
                                presente_min=pm, parcial_min=pc)
    if tipo == "erc":
        return ErcXlsmExtractor(ruta, modulo=args.modulo or "", presente_min=pm, parcial_min=pc,
                                umbral_auto=ua, umbral_revisar=ur)
    if tipo == "matriz":
        listado = args.listado or _buscar_listado(ruta)
        if not listado:
            raise ValueError("La fuente 'matriz' requiere --listado (o un 'Listado*.xlsx' junto a la carpeta).")
        return MatrizDirExtractor(ruta, listado=listado, hoja=args.hoja, programa=args.programa or "",
                                  presente_min=pm, parcial_min=pc, umbral_auto=ua, umbral_revisar=ur)
    if tipo == "master":
        return MasterXlsxExtractor(ruta, hoja=args.hoja)
    raise ValueError(f"Tipo de fuente desconocido: {tipo!r} (usa zoom|erc|matriz|master).")


def cmd_extraer(args) -> int:
    cfg = load_config()
    extractores = []
    for spec in args.fuente:
        if "=" not in spec:
            print(f"ERROR: --fuente debe ser tipo=ruta (recibí {spec!r})", file=sys.stderr)
            return 2
        tipo, ruta = spec.split("=", 1)
        extractores.append(_crear_extractor(tipo.strip(), ruta.strip(), args, cfg))

    datasets = Extraer(extractores).ejecutar()
    est = ConstruirEstandar().ejecutar(datasets, generado=_dt.date.today().isoformat())
    m = est.meta
    print(f"Estándar: {m['n_personas']} personas · {m['n_sesiones']} sesiones · {m['n_asistencias']} asistencias")
    print(f"  fuentes={m['fuentes']}  sin_match={m['sin_match']}  filtrados={m['filtrados']}")
    ExportarJson(JsonExporter()).ejecutar(est, args.salida)
    print(f"JSON escrito en: {args.salida}")
    return 0


def cmd_render(args) -> int:
    with open(args.estandar, encoding="utf-8") as f:
        est = Estandar.from_json(f.read())
    renderers = {"detalle": DetalleXlsxRenderer, "consolidado": ConsolidadoXlsxRenderer}
    Renderizar(renderers[args.formato]()).ejecutar(est, args.salida)
    print(f"{args.formato} escrito en: {args.salida}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nucleo",
                                description="Extrae asistencia de cualquier fuente a un estándar JSON y lo renderiza.")
    p.add_argument("-v", "--verbose", action="count", default=0)
    sub = p.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("extraer", help="Extrae una o varias fuentes a un estándar JSON.")
    ex.add_argument("--fuente", action="append", required=True,
                    help="tipo=ruta (repetible). tipo ∈ {zoom, erc, matriz, master}.")
    ex.add_argument("--salida", required=True, help="Ruta del JSON estándar de salida.")
    ex.add_argument("--listado", help="Listado .xlsx (para fuente 'matriz').")
    ex.add_argument("--hoja", help="Hoja objetivo (matriz/master).")
    ex.add_argument("--modulo", help="Nombre de módulo (fuente 'erc').")
    ex.add_argument("--programa", help="Programa a etiquetar en las personas.")
    ex.add_argument("--cohorte", help="Cohorte a etiquetar (fuente 'zoom').")
    ex.set_defaults(func=cmd_extraer)

    rd = sub.add_parser("render", help="Renderiza un estándar JSON a un formato.")
    rd.add_argument("--estandar", required=True, help="Ruta del JSON estándar.")
    rd.add_argument("--formato", required=True, choices=["detalle", "consolidado"])
    rd.add_argument("--salida", required=True, help="Ruta del archivo de salida (.xlsx).")
    rd.set_defaults(func=cmd_render)
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    nivel = logging.WARNING - min(args.verbose, 2) * 10
    logging.basicConfig(level=nivel, format="[%(levelname)s] %(name)s: %(message)s")
    try:
        return args.func(args)
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
