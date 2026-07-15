-- ============================================================
-- LOADER: estandar.json (salida del integrador) -> SQLite
-- "Las llamadas" para poblar la base desde la salida real del
-- repo Asistencia-prisma. Usa readfile() + json_each de SQLite.
--
-- Uso (CLI):
--   sqlite3 reporte_asistencia.db ".read scripts/asistencia/schema_asistencia.sql"
--   sqlite3 reporte_asistencia.db ".read scripts/asistencia/cargar_estandar.sql"
--
-- Requiere la variable :ruta -> se resuelve arriba con un .param o
-- editando la constante de abajo. Por defecto lee /tmp/estandar.json
-- ============================================================

PRAGMA foreign_keys = ON;

-- Cargar el JSON crudo en una tabla temporal (una sola celda)
DROP TABLE IF EXISTS _estandar_raw;
CREATE TEMP TABLE _estandar_raw AS
    SELECT readfile('/tmp/estandar.json') AS j;

-- personas
INSERT OR REPLACE INTO persona (id, nombre, correo, programa, cohorte)
SELECT json_extract(p.value, '$.id'),
       json_extract(p.value, '$.nombre'),
       json_extract(p.value, '$.correo'),
       json_extract(p.value, '$.programa'),
       json_extract(p.value, '$.cohorte')
FROM _estandar_raw r, json_each(r.j, '$.personas') p;

-- sesiones
INSERT OR REPLACE INTO sesion (id, programa, cohorte, modulo, etiqueta, fecha, duracion_min)
SELECT json_extract(s.value, '$.id'),
       json_extract(s.value, '$.programa'),
       json_extract(s.value, '$.cohorte'),
       json_extract(s.value, '$.modulo'),
       json_extract(s.value, '$.etiqueta'),
       json_extract(s.value, '$.fecha'),
       json_extract(s.value, '$.duracion_min')
FROM _estandar_raw r, json_each(r.j, '$.sesiones') s;

-- asistencias
INSERT OR REPLACE INTO asistencia (persona_id, sesion_id, estado, minutos, origen, nombre_origen)
SELECT json_extract(a.value, '$.persona_id'),
       json_extract(a.value, '$.sesion_id'),
       json_extract(a.value, '$.estado'),
       json_extract(a.value, '$.minutos'),
       json_extract(a.value, '$.origen'),
       json_extract(a.value, '$.nombre_origen')
FROM _estandar_raw r, json_each(r.j, '$.asistencias') a;

DROP TABLE _estandar_raw;

-- Verificación rápida
SELECT (SELECT COUNT(*) FROM persona)    AS personas,
       (SELECT COUNT(*) FROM sesion)     AS sesiones,
       (SELECT COUNT(*) FROM asistencia) AS asistencias;
