-- ============================================================
-- Reporte Materias - Modelo de datos (Proceso 1: solo modelado)
-- Fuente: tablero "Reporte Materias" (Contexto/Reporte Materias.pdf)
-- Motor: SQLite (local). Sin carga de datos reales todavía.
--
-- Reglas de existencia acordadas en la reunión de planeación:
--   - Una materia puede existir sin estudiantes.
--   - Un docente puede existir sin materia.
--   - Una clase NO puede existir sin materia creada ni sin docente (1 docente).
--   - Una asistencia NO puede existir sin clase creada ni sin estudiante creado.
-- ============================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS estudiante (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    correo        TEXT NOT NULL UNIQUE COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS materia (
    id_materia     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS docente (
    id_docente     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_docente TEXT NOT NULL UNIQUE
);

-- Una clase pertenece a una (1) materia y tiene un (1) docente.
-- numero_clase: posición de la sesión dentro de la materia (1 a 6 hoy).
CREATE TABLE IF NOT EXISTS clase (
    id_clase     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_materia   INTEGER NOT NULL REFERENCES materia (id_materia),
    id_docente   INTEGER NOT NULL REFERENCES docente (id_docente),
    numero_clase INTEGER NOT NULL CHECK (numero_clase BETWEEN 1 AND 6),
    fecha        TEXT    NOT NULL CHECK (fecha IS date(fecha)),
    UNIQUE (id_materia, numero_clase)
);

-- Registro YA PROCESADO por el algoritmo de asistencia (lo hace otra persona).
-- id_asistente referencia al estudiante, como en el tablero.
CREATE TABLE IF NOT EXISTS asistencia (
    id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_clase      INTEGER NOT NULL REFERENCES clase (id_clase),
    id_asistente  INTEGER NOT NULL REFERENCES estudiante (id_estudiante),
    asistio       INTEGER NOT NULL CHECK (asistio IN (0, 1)),
    num_horas     REAL    NOT NULL CHECK (num_horas >= 0),
    UNIQUE (id_clase, id_asistente)
);
