"""Reglas puras de la encuesta del curso (sin I/O).

Mapeo de respuestas calibrado contra el informe original ERC10 (las 12 medias
coinciden exactas):
  "N - ..."   -> N (dígito líder)
  "Verdadero" -> 5
  "Falso"     -> 0
  vacío       -> 0  (cuenta en el denominador, como el informe original)
  media = suma / nº de respondientes
"""

from __future__ import annotations

import re

# Textos canónicos de las 12 preguntas de escala, en el orden del CSV de la
# plataforma (columnas 5, 7, ... 27).
PREGUNTAS: list[str] = [
    "¿Cuál es tu valoración global del curso?",
    "Los conceptos desarrollados durante el curso resultan prácticos y aplicables.",
    "La calidad del contenido del curso (tema, lecturas de profundización y caso) es…",
    "Los videos introductorios resultan útiles para entender mejor la teoría.",
    "Las lecturas y encuestas de tendencia te han servido para ver la aplicación real "
    "de los contenidos teóricos.",
    "Las conclusiones de las encuestas de tendencia agregan valor a tu vida profesional.",
    "Las síntesis diarias que realiza el profesor en el debate te guían para continuar "
    "con la discusión del caso.",
    "Cuando el profesor retroalimenta tus intervenciones, lo hace de manera detallada.",
    "Las intervenciones del profesor, aunque no fueran respuestas directas a tus "
    "aportaciones en el debate, ¿te sirvieron de guía para continuar participando en el debate?",
    "Tu valoración del profesor como moderador del debate es...",
    "Las conclusiones del debate te resultan útiles para entender el caso y su resolución.",
    "El acompañamiento que me da la tutora durante el curso es…",
]

_RE_DIGITO = re.compile(r"\s*(\d)\s*-")


def valor_respuesta(texto: str) -> int:
    """Convierte una respuesta textual de la plataforma a la escala 0-5."""
    s = (texto or "").strip()
    m = _RE_DIGITO.match(s)
    if m:
        return int(m.group(1))
    low = s.lower()
    if low.startswith("verdad"):
        return 5
    if low.startswith("fals"):
        return 0
    return 0  # blank cuenta 0 (replica el informe original)


def media_pregunta(respuestas: list[str], n_respondientes: int) -> float:
    """Media de una pregunta sobre TODOS los respondientes (blank = 0)."""
    if not n_respondientes:
        return 0.0
    return round(sum(valor_respuesta(r) for r in respuestas) / n_respondientes, 2)


def limpiar_comentario(texto: str) -> str:
    """Recorta espacios y puntos suspensivos finales que arrastra el export."""
    return re.sub(r"[\s…]+$", "", (texto or "").strip()).strip()
