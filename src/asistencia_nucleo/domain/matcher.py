"""Matching de una fila de sesion contra el roster (dominio puro).

EMAIL-FIRST: el correo (presente en roster y en cada fila) resuelve casi todo. El
nombre difuso con guardarrailes anti-falso-positivo es el respaldo. Conservador:
ante la duda, REVISAR o SIN_MATCH antes que marcar al estudiante equivocado.
"""

from __future__ import annotations

from dataclasses import dataclass

from .modelos import Match, Nivel, Persona
from .normalizar import normalizar

# Backend difuso: rapidfuzz si esta, si no difflib (stdlib).
try:
    from rapidfuzz import fuzz as _fuzz

    BACKEND = "rapidfuzz"

    def _ratio(a: str, b: str) -> float:
        return float(_fuzz.ratio(a, b))

    def _token_set(a: str, b: str) -> float:
        return float(_fuzz.token_set_ratio(a, b))

    def _token_sort(a: str, b: str) -> float:
        return float(_fuzz.token_sort_ratio(a, b))

except Exception:  # pragma: no cover
    from difflib import SequenceMatcher

    BACKEND = "difflib"

    def _ratio(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio() * 100

    def _token_set(a: str, b: str) -> float:
        sa, sb = set(a.split()), set(b.split())
        inter = " ".join(sorted(sa & sb))
        ra, rb = " ".join(sorted(sa)), " ".join(sorted(sb))
        cand = [SequenceMatcher(None, ra, rb).ratio()]
        if inter:
            cand.append(SequenceMatcher(None, inter, ra).ratio())
            cand.append(SequenceMatcher(None, inter, rb).ratio())
        return max(cand) * 100

    def _token_sort(a: str, b: str) -> float:
        return SequenceMatcher(None, " ".join(sorted(a.split())),
                               " ".join(sorted(b.split()))).ratio() * 100


UMBRAL_TOKEN = 82
UMBRAL_PILA = 82
UMBRAL_COMPARTIDO = 88
PREFIJO_MIN = 4
TOKEN_FUERTE = 95


def token_match(a: str, b: str) -> float:
    if a == b:
        return 100.0
    r = _ratio(a, b)
    corto, largo = (a, b) if len(a) <= len(b) else (b, a)
    if len(corto) >= PREFIJO_MIN and largo.startswith(corto):
        return max(r, 92.0)
    return r


def _mejor(pt: str, c_tokens: list[str]) -> float:
    return max((token_match(pt, ct) for ct in c_tokens), default=0.0)


def _subconjunto(p_tokens: list[str], c_tokens: list[str], thr: float = UMBRAL_TOKEN) -> bool:
    corto, largo = (p_tokens, c_tokens) if len(p_tokens) <= len(c_tokens) else (c_tokens, p_tokens)
    return bool(corto) and all(_mejor(t, largo) >= thr for t in corto)


def _compartidos(p_tokens: list[str], c_tokens: list[str], thr: float = UMBRAL_COMPARTIDO) -> int:
    return sum(1 for t in p_tokens if _mejor(t, c_tokens) >= thr)


@dataclass
class _Cand:
    est: Persona
    score: float
    subset: bool
    pila_ok: bool
    apellido_ok: bool
    compartidos: int

    @property
    def orden(self):
        return (self.subset, self.compartidos, self.score)


def _evaluar(p_tokens: list[str], est: Persona) -> _Cand:
    c = est.tokens
    p_norm = " ".join(p_tokens)
    score = max(_token_set(p_norm, est.nombre_norm), _token_sort(p_norm, est.nombre_norm))
    subset = _subconjunto(p_tokens, c)
    pila_ok = bool(p_tokens and c and token_match(p_tokens[0], c[0]) >= UMBRAL_PILA)
    if p_tokens and len(c) >= 2 and not pila_ok:
        pila_ok = token_match(p_tokens[0], c[1]) >= UMBRAL_PILA
    ap_p, ap_c = p_tokens[1:], c[1:]
    apellido_ok = any(token_match(x, y) >= UMBRAL_TOKEN for x in ap_p for y in ap_c) if ap_p and ap_c else False
    return _Cand(est, score, subset, pila_ok, apellido_ok, _compartidos(p_tokens, c))


def _guardarrail_ok(cand: _Cand) -> bool:
    if cand.subset and cand.compartidos >= 2:
        return True
    return bool(cand.pila_ok and cand.apellido_ok)


def _m(est, nivel, score, motivo) -> Match:
    return Match(est, nivel, round(float(score), 1), motivo)


def _una_palabra(w: str, roster: list[Persona], umbral_revisar: float) -> Match:
    fuertes = [e for e in roster if _mejor(w, e.tokens) >= TOKEN_FUERTE]
    if len(fuertes) == 1:
        return _m(fuertes[0], Nivel.AUTO, 100, "una palabra, candidato unico")
    if len(fuertes) > 1:
        best = max(fuertes, key=lambda e: _mejor(w, e.tokens))
        return _m(best, Nivel.REVISAR, 90, f"una palabra ambigua ({len(fuertes)})")
    if roster:
        best = max(roster, key=lambda e: _mejor(w, e.tokens))
        s = _mejor(w, best.tokens)
        if s >= umbral_revisar:
            return _m(best, Nivel.REVISAR, s, "una palabra, coincidencia debil")
    return Match(None, Nivel.SIN_MATCH, 0.0, "una palabra sin candidatos")


def _multi(p_tokens, roster, umbral_auto, umbral_revisar) -> Match:
    cands = [_evaluar(p_tokens, e) for e in roster]
    if not cands:
        return Match(None, Nivel.SIN_MATCH, 0.0, "roster vacio")
    aceptables = [c for c in cands if _guardarrail_ok(c)]
    if not aceptables:
        best = max(cands, key=lambda c: c.orden)
        if best.score >= umbral_revisar and best.compartidos >= 1:
            return _m(best.est, Nivel.REVISAR, best.score, "sin match confiable; revisar")
        return Match(None, Nivel.SIN_MATCH, round(best.score, 1), "sin match")
    aceptables.sort(key=lambda c: c.orden, reverse=True)
    best = aceptables[0]
    otros = [c for c in aceptables[1:] if c.est.clave != best.est.clave]
    ambiguo = bool(otros) and (best.score - otros[0].score) < 5 \
        and otros[0].subset == best.subset and otros[0].compartidos == best.compartidos
    if ambiguo:
        return _m(best.est, Nivel.REVISAR, best.score, "varios candidatos plausibles")
    if best.subset or best.score >= umbral_auto:
        return _m(best.est, Nivel.AUTO, best.score, "match confiable")
    if best.score >= umbral_revisar:
        return _m(best.est, Nivel.REVISAR, best.score, "confianza media")
    return Match(best.est, Nivel.SIN_MATCH, round(best.score, 1), "score bajo")


def matchear(nombre: str, correo: str, roster: list[Persona],
             umbral_auto: float = 90, umbral_revisar: float = 70) -> Match:
    # 1. Correo exacto (email-first) — la via dominante en este formato.
    c = (correo or "").strip().lower()
    if c:
        hits = [e for e in roster if e.correo_norm == c]
        if len(hits) == 1:
            return _m(hits[0], Nivel.AUTO, 100, "correo exacto")
        if len(hits) > 1:
            return _m(hits[0], Nivel.REVISAR, 100, "correo duplicado en roster")

    # 2. Nombre.
    p_norm = normalizar(nombre)
    p_tokens = p_norm.split()
    if not p_tokens:
        return Match(None, Nivel.SIN_MATCH, 0.0, "nombre vacio")
    exactos = [e for e in roster if e.nombre_norm == p_norm]
    if len(exactos) == 1:
        return _m(exactos[0], Nivel.AUTO, 100, "nombre exacto")
    if len(exactos) > 1:
        return _m(exactos[0], Nivel.REVISAR, 100, "nombre exacto duplicado")
    if len(p_tokens) == 1:
        return _una_palabra(p_tokens[0], roster, umbral_revisar)
    return _multi(p_tokens, roster, umbral_auto, umbral_revisar)
