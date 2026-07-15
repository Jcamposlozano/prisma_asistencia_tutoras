"""Utilidades compartidas para leer CSV de Zoom y filtrar no-personas (adapter)."""

from __future__ import annotations

import csv
import datetime as _dt
import re

C_NOMBRE = "Nombre (nombre original)"
C_CORREO = "Correo electrónico"
C_ENTRADA = "Hora de entrada"
C_DUR = "Duración (minutos)"
C_INV = "Invitado"

_FMT = ("%d/%m/%Y %I:%M:%S %p", "%m/%d/%Y %I:%M:%S %p", "%d/%m/%Y %H:%M:%S")


def _fecha(txt: str) -> _dt.date | None:
    txt = (txt or "").strip()
    for f in _FMT:
        try:
            return _dt.datetime.strptime(txt, f).date()
        except ValueError:
            continue
    return None


def _num(txt) -> float:
    try:
        return float(str(txt).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def leer_csv_zoom(path: str) -> list[dict]:
    """Lee un participants_*.csv (UTF-8 con BOM) -> filas {nombre,correo,minutos,entrada,invitado}."""
    filas: list[dict] = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            nombre = (row.get(C_NOMBRE) or "").strip()
            if not nombre:
                continue
            filas.append({
                "nombre": nombre,
                "correo": (row.get(C_CORREO) or "").strip(),
                "minutos": _num(row.get(C_DUR)),
                "entrada": _fecha(row.get(C_ENTRADA, "")),
                "invitado": (row.get(C_INV) or "").strip(),
            })
    return filas


_RE_BOT = re.compile(
    r"notetaker|fathom|otter|read\.?\s*ai|fireflies|grabaci[oó]n|recording|\bbot\b|\bai\b|\bia\b", re.I
)
_DISP = ("iphone", "ipad", "ipod", "galaxy", "poco", "redmi", "samsung", "motorola", "xiaomi",
         "huawei", "honor", "oppo", "vivo", "realme", "tablet", "android", "macbook", "laptop", "pc", "nokia")
_RE_DISP = re.compile(r"^\s*(?:" + "|".join(_DISP) + r")\b", re.I)
_RE_RESC = re.compile(r"\bde\s+(.+)$", re.I)
_RE_CORREO_HOST = re.compile(r"\.zoom@|@.*zoom", re.I)
_RE_HOST = re.compile(r"gmp\+?\s*m[aá]ster|gmp\s+d[bm]|db-dm|master\s*d[bm]", re.I)


def clasificar(nombre: str, invitado: str = "", correo: str = "") -> tuple[str, str]:
    """Devuelve (categoria, nombre_para_match). categoria: PERSONA|HOST|BOT|DISPOSITIVO."""
    inv = (invitado or "").strip().lower()
    correo = (correo or "").strip()
    if inv in ("no", "n"):
        return "HOST", ""
    if correo and _RE_CORREO_HOST.search(correo):
        return "HOST", ""
    if _RE_HOST.search(nombre):
        return "HOST", ""
    if _RE_BOT.search(nombre):
        return "BOT", ""
    if _RE_DISP.search(nombre):
        m = _RE_RESC.search(nombre)
        rescatado = m.group(1).strip() if m else ""
        return "DISPOSITIVO", (rescatado if len(rescatado.replace(" ", "")) >= 2 else "")
    return "PERSONA", nombre
