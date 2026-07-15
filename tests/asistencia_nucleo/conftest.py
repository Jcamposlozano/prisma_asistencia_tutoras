"""Fixtures y rutas de muestras."""

from __future__ import annotations

import os

import pytest

from asistencia_nucleo.domain.modelos import Persona

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(RAIZ, "data")

ZOOM = os.path.join(DATA, "zoom", "participants_97772938012_2026_04_29 (2).csv")
ERC = os.path.join(DATA, "erc", "FORMATO ASISTENCIA ERC10.xlsm")
MASTER = os.path.join(DATA, "master", "Asistencia Máster.xlsx")
MATRIZ_DIR = os.path.join(DATA, "matriz", "DIGITAL BUSINESS")
LISTADO = os.path.join(DATA, "matriz", "Listado de estudiantes 2025-2.xlsx")


def _skip(path):
    return pytest.mark.skipif(not os.path.exists(path), reason=f"muestra no disponible: {path}")


requiere_erc = _skip(ERC)
requiere_zoom = _skip(ZOOM)
requiere_master = _skip(MASTER)
requiere_matriz = pytest.mark.skipif(
    not (os.path.isdir(MATRIZ_DIR) and os.path.exists(LISTADO)), reason="muestra matriz no disponible"
)


def persona(nombre, correo="", programa="", cohorte=""):
    return Persona(nombre=nombre, correo=correo, programa=programa, cohorte=cohorte)
