-- ============================================================
-- Esquema alineado al ESTÁNDAR CANÓNICO del integrador de asistencia
-- (repo samyrami/Asistencia-prisma). Su salida es estandar.json con
-- personas / sesiones / asistencias. Aquí lo aterrizamos a SQLite para
-- generar los consolidados con SQL.
--
-- Diferencias vs el modelo v1 del tablero (y por qué):
--   - persona lleva programa y cohorte  (los trae el estándar)
--   - sesion lleva modulo, etiqueta, duracion_min
--   - asistencia usa ESTADO canónico (5 valores) + MINUTOS,
--     NO asistio(0/1)/num_horas. El AUSENTE se guarda como fila
--     explícita (minutos=0), no se deduce por ausencia.
-- ============================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS asistencia;
DROP TABLE IF EXISTS sesion;
DROP TABLE IF EXISTS persona;

CREATE TABLE persona (
    id       TEXT PRIMARY KEY,          -- correo normalizado o slug (lo fija el integrador)
    nombre   TEXT NOT NULL,
    correo   TEXT,
    programa TEXT,
    cohorte  TEXT
);

CREATE TABLE sesion (
    id           TEXT PRIMARY KEY,       -- p.ej. "erc:ERC10:1V"
    programa     TEXT,
    cohorte      TEXT,
    modulo       TEXT,                   -- materia / módulo (ERC10)
    etiqueta     TEXT,                   -- 1V, 1S, 2V, ... (columna del consolidado)
    fecha        TEXT,                   -- ISO o ""
    duracion_min REAL
);

CREATE TABLE asistencia (
    persona_id    TEXT NOT NULL REFERENCES persona (id),
    sesion_id     TEXT NOT NULL REFERENCES sesion (id),
    estado        TEXT NOT NULL CHECK (estado IN
                    ('PRESENTE','PARCIAL','AUSENTE','EXCUSA','DESCONOCIDO')),
    minutos       REAL,
    origen        TEXT,
    nombre_origen TEXT,
    PRIMARY KEY (persona_id, sesion_id)
);

CREATE INDEX ix_asis_sesion ON asistencia (sesion_id);
CREATE INDEX ix_asis_estado ON asistencia (estado);
