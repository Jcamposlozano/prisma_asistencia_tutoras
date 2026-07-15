"""Adapter de salida: Informe final (HTML -> PDF vía Chrome headless).

Replica el formato del documento original de la coordinación: encabezado con
logos UIDE/eig, "INFORME FINAL" en azul, tabla de medias por pregunta,
calificación docente, incidencias y comentarios de estudiantes.
"""

from __future__ import annotations

import base64
import datetime as dt
import html
import shutil
import subprocess
from pathlib import Path
from typing import Any

CHROME_CANDS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
]
ASSETS = Path(__file__).resolve().parent / "assets"
VINO = "#8a1538"
AZUL = "#1f3b73"
NARANJA = "#c0562a"


def _uri(fname: str) -> str:
    f = ASSETS / fname
    if not f.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()


def _fmt(v: Any) -> str:
    return f"{float(v):.2f}".replace(".", ",")


def _build(datos: dict[str, Any]) -> str:
    esc = lambda s: html.escape(str(s))  # noqa: E731
    logo_uide, logo_eig = _uri("logo_uide.png"), _uri("logo_eig.png")
    hoy = dt.date.today().isoformat()

    filas = "\n".join(
        f'<tr><td class="q">{esc(p["texto"])}</td><td class="v">{_fmt(p["media"])}</td></tr>'
        for p in datos.get("preguntas", [])
    )
    doc = datos.get("docente", {})
    com = datos.get("comentarios", {})

    def bullets(items):
        return "\n".join(f"<li>{esc(t)}</li>" for t in items) or "<li>—</li>"

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Informe final — {esc(datos.get('materia', ''))}</title>
<style>
  @page {{ size: A4; margin: 16mm 18mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
         color:#20262e; font-size:11.5px; line-height:1.5; margin:0; }}
  .brand {{ display:flex; align-items:center; justify-content:space-between;
            height:16mm; margin:0 0 14px; }}
  .brand img.uide {{ height: 13mm; }}
  .brand img.eig  {{ height: 11mm; }}
  h1 {{ color:{AZUL}; font-size:30px; letter-spacing:.5px; margin:0 0 10px; }}
  .meta {{ font-size:12px; margin:0 0 22px; }}
  .meta b {{ font-weight:600; }}
  h2 {{ color:{VINO}; font-size:15px; margin:24px 0 10px; }}
  h3 {{ color:{NARANJA}; font-size:13.5px; margin:18px 0 8px; font-weight:600; }}
  table {{ border-collapse:collapse; width:100%; margin:4px 0 8px; }}
  td {{ border:1px solid #b9c0c8; padding:6px 9px; vertical-align:middle; }}
  td.q {{ font-size:11.5px; }}
  td.v {{ width:52px; text-align:center; font-weight:600;
          font-variant-numeric:tabular-nums; }}
  .doc p {{ margin:2px 0; }}
  .doc .tot {{ color:{VINO}; font-weight:700; margin-top:8px; }}
  .none {{ color:#4a5560; margin:2px 0 0; }}
  ul {{ margin:4px 0 6px; padding-left:20px; }}
  li {{ margin:3px 0; }}
  .foot {{ margin-top:26px; color:#9aa4ae; font-size:9px;
           border-top:1px solid #e2e8f0; padding-top:8px; }}
</style></head><body>

<div class="brand">
  {f'<img class="uide" src="{logo_uide}" alt="UIDE">' if logo_uide else '<span></span>'}
  {f'<img class="eig" src="{logo_eig}" alt="eig">' if logo_eig else ''}
</div>

<h1>INFORME FINAL</h1>
<p class="meta">
  <b>Programa:</b> {esc(datos.get('programa', ''))}<br>
  <b>Materia:</b> {esc(datos.get('materia', ''))}<br>
  <b>Cohorte:</b> {esc(datos.get('cohorte', ''))}<br>
  <b>Profesor:</b> {esc(datos.get('profesor', ''))}
</p>

<h2>Calificación media por pregunta</h2>
<table>{filas}</table>

<h2>Calificación docente</h2>
<div class="doc">
  <p>Puntaje docente clase 1: {esc(doc.get('clase1', '—'))}%</p>
  <p>Puntaje docente clase 2: {esc(doc.get('clase2', '—'))}%</p>
  <p>Puntaje docente clase 3: {esc(doc.get('clase3', '—'))}%</p>
  <p class="tot">Calificación docente: {_fmt(doc.get('calificacion_docente', 0))}</p>
  <p class="tot">Calificación media encuesta: {_fmt(doc.get('media_encuesta', 0))}</p>
</div>

<h2>Incidencias sesiones síncronas</h2>
<p class="none">{esc(datos.get('incidencias_sincronas', 'Ninguna'))}</p>

<h2>Recopilación comentarios estudiantes</h2>
<h3>¿Qué es lo que más te ha gustado del curso?</h3>
<ul>{bullets(com.get('gusto', []))}</ul>
<h3>¿Qué cambiarías?</h3>
<ul>{bullets(com.get('cambiarias', []))}</ul>

<p class="foot">Informe final generado el {esc(hoy)} desde los CSV de encuesta y
evaluación docente.</p>
</body></html>"""


class HtmlInformeFinal:
    def render(self, datos: dict[str, Any], salida: str) -> str:
        html_out = Path(salida).with_suffix(".html")
        pdf_out = Path(salida).with_suffix(".pdf")
        html_out.write_text(_build(datos), encoding="utf-8")
        chrome = next(
            (c for c in CHROME_CANDS if Path(c).exists() or shutil.which(c)), None
        )
        if chrome:
            subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                 f"--print-to-pdf={pdf_out.resolve()}", html_out.resolve().as_uri()],
                check=True, capture_output=True,
            )
            return str(pdf_out)
        return str(html_out)
