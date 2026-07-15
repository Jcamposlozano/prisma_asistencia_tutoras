"""Modelo canónico (el 'estándar'): entidades puras + serialización a dict/JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum

from .normalizar import normalizar, tokens


class EstadoCanonico(str, Enum):
    PRESENTE = "PRESENTE"
    PARCIAL = "PARCIAL"       # asistió parcialmente / tiempo incompleto
    AUSENTE = "AUSENTE"
    EXCUSA = "EXCUSA"
    DESCONOCIDO = "DESCONOCIDO"


class Nivel(str, Enum):
    AUTO = "AUTO"
    REVISAR = "REVISAR"
    SIN_MATCH = "SIN_MATCH"


def _slug(texto: str) -> str:
    return normalizar(texto).replace(" ", "-") or "sin-nombre"


@dataclass
class Persona:
    nombre: str
    correo: str = ""
    programa: str = ""
    cohorte: str = ""
    id: str = ""
    # derivados (para matching)
    nombre_norm: str = ""
    correo_norm: str = ""
    tokens: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.correo_norm = (self.correo or "").strip().lower()
        self.nombre_norm = normalizar(self.nombre)
        self.tokens = tokens(self.nombre)
        if not self.id:
            self.id = self.correo_norm or _slug(self.nombre)

    @property
    def clave(self) -> str:
        return self.id

    def to_dict(self) -> dict:
        return {"id": self.id, "nombre": self.nombre, "correo": self.correo,
                "programa": self.programa, "cohorte": self.cohorte}

    @classmethod
    def from_dict(cls, d: dict) -> Persona:
        return cls(nombre=d.get("nombre", ""), correo=d.get("correo", ""),
                   programa=d.get("programa", ""), cohorte=d.get("cohorte", ""),
                   id=d.get("id", ""))


@dataclass
class Sesion:
    id: str
    programa: str = ""
    cohorte: str = ""
    modulo: str = ""
    etiqueta: str = ""
    fecha: str = ""                       # ISO (YYYY-MM-DD) o ""
    duracion_min: float | None = None

    def to_dict(self) -> dict:
        return {"id": self.id, "programa": self.programa, "cohorte": self.cohorte,
                "modulo": self.modulo, "etiqueta": self.etiqueta, "fecha": self.fecha,
                "duracion_min": self.duracion_min}

    @classmethod
    def from_dict(cls, d: dict) -> Sesion:
        return cls(id=d["id"], programa=d.get("programa", ""), cohorte=d.get("cohorte", ""),
                   modulo=d.get("modulo", ""), etiqueta=d.get("etiqueta", ""),
                   fecha=d.get("fecha", ""), duracion_min=d.get("duracion_min"))


@dataclass
class Asistencia:
    persona_id: str
    sesion_id: str
    estado: EstadoCanonico
    minutos: float | None = None
    origen: str = ""
    nombre_origen: str = ""

    def to_dict(self) -> dict:
        return {"persona_id": self.persona_id, "sesion_id": self.sesion_id,
                "estado": self.estado.value, "minutos": self.minutos,
                "origen": self.origen, "nombre_origen": self.nombre_origen}

    @classmethod
    def from_dict(cls, d: dict) -> Asistencia:
        return cls(persona_id=d["persona_id"], sesion_id=d["sesion_id"],
                   estado=EstadoCanonico(d["estado"]), minutos=d.get("minutos"),
                   origen=d.get("origen", ""), nombre_origen=d.get("nombre_origen", ""))


@dataclass
class Match:
    persona: Persona | None
    nivel: Nivel
    score: float
    motivo: str


@dataclass
class DatasetCanonico:
    """Lo que devuelve un extractor: un trozo del estándar desde UNA fuente."""

    fuente: str = ""
    personas: list[Persona] = field(default_factory=list)
    sesiones: list[Sesion] = field(default_factory=list)
    asistencias: list[Asistencia] = field(default_factory=list)
    sin_match: list[dict] = field(default_factory=list)
    filtrados: list[dict] = field(default_factory=list)


@dataclass
class Estandar:
    meta: dict = field(default_factory=dict)
    personas: list[Persona] = field(default_factory=list)
    sesiones: list[Sesion] = field(default_factory=list)
    asistencias: list[Asistencia] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "meta": self.meta,
            "personas": [p.to_dict() for p in self.personas],
            "sesiones": [s.to_dict() for s in self.sesiones],
            "asistencias": [a.to_dict() for a in self.asistencias],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> Estandar:
        return cls(
            meta=d.get("meta", {}),
            personas=[Persona.from_dict(p) for p in d.get("personas", [])],
            sesiones=[Sesion.from_dict(s) for s in d.get("sesiones", [])],
            asistencias=[Asistencia.from_dict(a) for a in d.get("asistencias", [])],
        )

    @classmethod
    def from_json(cls, texto: str) -> Estandar:
        return cls.from_dict(json.loads(texto))
