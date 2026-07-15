"""Adapter: repositorio de asistencia sobre SQLite.

Aterriza el estandar.json del integrador (asistencia_nucleo) al esquema
relacional persona · sesion · asistencia y responde las consultas del informe.
Mismo esquema que scripts/asistencia/schema_asistencia.sql (la copia para DBeaver).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ..domain.asistencia import ResumenEstudiante

_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS persona (
    id       TEXT PRIMARY KEY,
    nombre   TEXT NOT NULL,
    correo   TEXT,
    programa TEXT,
    cohorte  TEXT
);

CREATE TABLE IF NOT EXISTS sesion (
    id           TEXT PRIMARY KEY,
    programa     TEXT,
    cohorte      TEXT,
    modulo       TEXT,
    etiqueta     TEXT,
    fecha        TEXT,
    duracion_min REAL
);

CREATE TABLE IF NOT EXISTS asistencia (
    persona_id    TEXT NOT NULL REFERENCES persona (id),
    sesion_id     TEXT NOT NULL REFERENCES sesion (id),
    estado        TEXT NOT NULL CHECK (estado IN
                    ('PRESENTE','PARCIAL','AUSENTE','EXCUSA','DESCONOCIDO')),
    minutos       REAL,
    origen        TEXT,
    nombre_origen TEXT,
    PRIMARY KEY (persona_id, sesion_id)
);

CREATE INDEX IF NOT EXISTS ix_asis_sesion ON asistencia (sesion_id);
CREATE INDEX IF NOT EXISTS ix_asis_estado ON asistencia (estado);
"""


class SqliteRepositorioAsistencia:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _con(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def cargar_estandar(self, estandar_json: str) -> tuple[int, int, int]:
        doc = json.loads(Path(estandar_json).read_text(encoding="utf-8"))
        con = self._con()
        try:
            con.executescript(_SCHEMA)
            con.executemany(
                "INSERT OR REPLACE INTO persona (id,nombre,correo,programa,cohorte) "
                "VALUES (?,?,?,?,?)",
                [
                    (p["id"], p["nombre"], p.get("correo"), p.get("programa"), p.get("cohorte"))
                    for p in doc.get("personas", [])
                ],
            )
            con.executemany(
                "INSERT OR REPLACE INTO sesion "
                "(id,programa,cohorte,modulo,etiqueta,fecha,duracion_min) VALUES (?,?,?,?,?,?,?)",
                [
                    (
                        s["id"],
                        s.get("programa"),
                        s.get("cohorte"),
                        s.get("modulo"),
                        s.get("etiqueta"),
                        s.get("fecha"),
                        s.get("duracion_min"),
                    )
                    for s in doc.get("sesiones", [])
                ],
            )
            con.executemany(
                "INSERT OR REPLACE INTO asistencia "
                "(persona_id,sesion_id,estado,minutos,origen,nombre_origen) VALUES (?,?,?,?,?,?)",
                [
                    (
                        a["persona_id"],
                        a["sesion_id"],
                        a["estado"],
                        a.get("minutos"),
                        a.get("origen"),
                        a.get("nombre_origen"),
                    )
                    for a in doc.get("asistencias", [])
                ],
            )
            con.commit()
            counts = tuple(
                con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]  # noqa: S608
                for t in ("persona", "sesion", "asistencia")
            )
            return counts  # type: ignore[return-value]
        finally:
            con.close()

    def densificar_ausencias(self) -> int:
        """AUSENTE explícito (minutos 0) para cada (persona, sesión) sin registro.

        Necesario cuando la fuente no trae roster (p.ej. zoom): sólo emite filas
        de quien asistió.
        """
        con = self._con()
        try:
            cur = con.execute(
                """
                INSERT INTO asistencia (persona_id, sesion_id, estado, minutos,
                                        origen, nombre_origen)
                SELECT p.id, s.id, 'AUSENTE', 0, 'densificado', p.nombre
                FROM persona p CROSS JOIN sesion s
                WHERE NOT EXISTS (SELECT 1 FROM asistencia a
                                  WHERE a.persona_id = p.id AND a.sesion_id = s.id)
                """
            )
            con.commit()
            return cur.rowcount
        finally:
            con.close()

    def n_sesiones(self) -> int:
        con = self._con()
        try:
            return con.execute("SELECT COUNT(*) FROM sesion").fetchone()[0]
        finally:
            con.close()

    def resumen_por_estudiante(self) -> list[ResumenEstudiante]:
        con = self._con()
        try:
            rows = con.execute(
                """
                SELECT p.nombre,
                       SUM(a.estado='PRESENTE') AS presentes,
                       SUM(a.estado='AUSENTE')  AS ausentes,
                       SUM(a.estado='PARCIAL')  AS parciales
                FROM persona p JOIN asistencia a ON a.persona_id = p.id
                GROUP BY p.id, p.nombre
                ORDER BY p.nombre COLLATE NOCASE
                """
            ).fetchall()
            return [ResumenEstudiante(n, pr or 0, au or 0, pa or 0) for n, pr, au, pa in rows]
        finally:
            con.close()
