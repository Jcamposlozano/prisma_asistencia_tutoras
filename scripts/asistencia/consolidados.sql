-- ============================================================
-- CONSOLIDADOS (Proceso 2): las queries que el equipo necesita,
-- generadas desde la base poblada con el estandar.json del integrador.
-- Leyenda de estado:  P=PRESENTE  D=PARCIAL  o=AUSENTE  E=EXCUSA  ?=DESCONOCIDO
-- %Asist = PRESENTE / #sesiones * 100  (misma fórmula que su consolidado.xlsx)
-- ============================================================

-- ------------------------------------------------------------
-- Q1 · CONSOLIDADO MATRIZ  (Persona x sesión) + conteos + %Asist
--      Reproduce exactamente el consolidado.xlsx del integrador.
--      Una columna por etiqueta de sesión (1V,1S,2V,2S,3V,3S).
-- ------------------------------------------------------------
WITH cod AS (
    SELECT a.persona_id, s.etiqueta, a.estado,
           CASE a.estado
             WHEN 'PRESENTE' THEN 'P' WHEN 'PARCIAL' THEN 'D'
             WHEN 'AUSENTE'  THEN 'o' WHEN 'EXCUSA'  THEN 'E' ELSE '?'
           END AS c
    FROM asistencia a JOIN sesion s ON s.id = a.sesion_id
)
SELECT p.nombre AS Persona,
       MAX(CASE WHEN c.etiqueta='1V' THEN c.c END) AS "1V",
       MAX(CASE WHEN c.etiqueta='1S' THEN c.c END) AS "1S",
       MAX(CASE WHEN c.etiqueta='2V' THEN c.c END) AS "2V",
       MAX(CASE WHEN c.etiqueta='2S' THEN c.c END) AS "2S",
       MAX(CASE WHEN c.etiqueta='3V' THEN c.c END) AS "3V",
       MAX(CASE WHEN c.etiqueta='3S' THEN c.c END) AS "3S",
       SUM(c.estado='PRESENTE') AS "#Pres",
       SUM(c.estado='PARCIAL')  AS "#Parc",
       SUM(c.estado='AUSENTE')  AS "#Aus",
       SUM(c.estado='EXCUSA')   AS "#Exc",
       ROUND(100.0 * SUM(c.estado='PRESENTE') /
             (SELECT COUNT(*) FROM sesion), 1) AS "%Asist"
FROM persona p JOIN cod c ON c.persona_id = p.id
GROUP BY p.id, p.nombre
ORDER BY p.nombre;

-- ------------------------------------------------------------
-- Q2 · CONSOLIDADO POR ESTUDIANTE (resumen del módulo, sin matriz)
--      Lo que se muestra "bonito" en el informe de comité.
-- ------------------------------------------------------------
SELECT p.nombre AS estudiante,
       SUM(a.estado='PRESENTE') AS presentes,
       SUM(a.estado='PARCIAL')  AS parciales,
       SUM(a.estado='AUSENTE')  AS ausentes,
       ROUND(100.0 * SUM(a.estado='PRESENTE') /
             (SELECT COUNT(*) FROM sesion), 1) AS pct_asistencia
FROM persona p JOIN asistencia a ON a.persona_id = p.id
GROUP BY p.id, p.nombre
ORDER BY pct_asistencia ASC, p.nombre;   -- los de menor asistencia primero

-- ------------------------------------------------------------
-- Q3 · LISTADO DE NO ASISTENTES por sesión
--      "Filtrar quiénes no asistieron" (paso manual de Juliet).
-- ------------------------------------------------------------
SELECT s.etiqueta AS sesion, p.nombre AS estudiante, a.minutos
FROM asistencia a
JOIN persona p ON p.id = a.persona_id
JOIN sesion  s ON s.id = a.sesion_id
WHERE a.estado = 'AUSENTE'
ORDER BY s.etiqueta, p.nombre;

-- ------------------------------------------------------------
-- Q4 · RESUMEN POR SESIÓN (% de asistencia de cada clase)
-- ------------------------------------------------------------
SELECT s.etiqueta AS sesion,
       SUM(a.estado='PRESENTE') AS presentes,
       SUM(a.estado='PARCIAL')  AS parciales,
       SUM(a.estado='AUSENTE')  AS ausentes,
       COUNT(*)                 AS total,
       ROUND(100.0 * SUM(a.estado='PRESENTE') / COUNT(*), 1) AS pct_asistencia
FROM sesion s JOIN asistencia a ON a.sesion_id = s.id
GROUP BY s.id, s.etiqueta
ORDER BY s.etiqueta;

-- ------------------------------------------------------------
-- Q5 · CONSOLIDADO DE TODA LA MAESTRÍA (por estudiante, TODOS los módulos)
--      Hoy hay un módulo (ERC10); al cargar más módulos, esta misma
--      query los suma sin cambios: es el consolidado global de la maestría.
-- ------------------------------------------------------------
SELECT p.nombre AS estudiante,
       COUNT(DISTINCT s.modulo)                    AS modulos,
       SUM(a.estado='PRESENTE')                    AS presentes,
       SUM(a.estado='PARCIAL')                     AS parciales,
       SUM(a.estado='AUSENTE')                     AS ausentes,
       COUNT(*)                                    AS sesiones_totales,
       ROUND(100.0 * SUM(a.estado='PRESENTE') / COUNT(*), 1) AS pct_maestria
FROM persona p JOIN asistencia a ON a.persona_id = p.id
JOIN sesion s ON s.id = a.sesion_id
GROUP BY p.id, p.nombre
ORDER BY pct_maestria ASC, p.nombre;
