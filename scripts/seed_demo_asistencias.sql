-- ============================================================
-- DEMO: asistencias YA PROCESADAS (simula el output del algoritmo
-- de asistencia, que desarrolla otra persona).
--
-- Datos tomados de la materia real de referencia:
--   ENERGIA DE LA BIOMASA - corte MER-A (junio 2026)
--   Docente: Andrea Estefanía Jaramillo
--   6 clases: viernes/sábado 5-6, 12-13, 19-20 de junio de 2026
--
-- Convención del demo (regla "más de la mitad de la clase"):
--   asistio = 1 -> estuvo más de la mitad del tiempo (A)
--   asistio = 0 -> se conectó pero tiempo insuficiente (ID)
--   sin fila    -> no se presentó (NP); se obtiene por reflexión
--                  inversa: estudiante sin asistencia en esa clase.
-- ============================================================

PRAGMA foreign_keys = ON;

INSERT INTO estudiante (id_estudiante, nombre, correo) VALUES
    (1,  'AGUILAR CAMPOS JORDAN',                                     'joraguilarca@uide.edu.ec'),
    (2,  'ANDRADE NARVAEZ RICARDO GERMAN',                            'riandradena@uide.edu.ec'),
    (3,  'CALDERON PINZA MAX',                                        'macalderonpi@uide.edu.ec'),
    (4,  'ESPINOZA DE LOS MONTEROS VELASTEGUI GABRIELA ALEXANDRA',    'gaespinozave@uide.edu.ec'),
    (5,  'JAIME MAURICIO PILAMUNGA UBIDIA',                           'japilamungaub@uide.edu.ec'),
    (6,  'LAVERDE MONGE JAVIER',                                      'jalaverdemo@uide.edu.ec'),
    (7,  'LUDEÑA CHALACAN JUAN',                                      'juludenach@uide.edu.ec'),
    (8,  'MENDOZA GARCIA MALENY',                                     'mamendozaga@uide.edu.ec'),
    (9,  'MOGROVEJO NARVAEZ DAVID',                                   'damogrovejona@uide.edu.ec'),
    (10, 'MOGROVEJO NARVAEZ DIEGO',                                   'dimogrovejona@uide.edu.ec');

INSERT INTO docente (id_docente, nombre_docente) VALUES
    (1, 'Andrea Estefanía Jaramillo');

INSERT INTO materia (id_materia, nombre_materia) VALUES
    (1, 'ENERGIA DE LA BIOMASA');

INSERT INTO clase (id_clase, id_materia, id_docente, numero_clase, fecha) VALUES
    (1, 1, 1, 1, '2026-06-05'),
    (2, 1, 1, 2, '2026-06-06'),
    (3, 1, 1, 3, '2026-06-12'),
    (4, 1, 1, 4, '2026-06-13'),
    (5, 1, 1, 5, '2026-06-19'),
    (6, 1, 1, 6, '2026-06-20');

-- Clase 1 (2026-06-05, duración ~2.5 h)
INSERT INTO asistencia (id_clase, id_asistente, asistio, num_horas) VALUES
    (1, 1,  1, 2.11),
    (1, 2,  1, 2.45),
    (1, 3,  1, 2.26),
    (1, 4,  1, 1.69),
    (1, 5,  1, 1.69),
    (1, 6,  1, 2.60),
    (1, 7,  1, 2.50),
    (1, 8,  1, 1.55),
    (1, 9,  1, 1.54),
    (1, 10, 0, 0.05);   -- ID: solo 3 min

-- Clase 2 (2026-06-06, duración ~4 h)
INSERT INTO asistencia (id_clase, id_asistente, asistio, num_horas) VALUES
    (2, 2,  1, 3.90),
    (2, 3,  1, 3.90),
    (2, 4,  1, 2.58),
    (2, 6,  1, 3.87),
    (2, 7,  1, 3.20),
    (2, 8,  1, 3.05),
    (2, 9,  1, 3.85),
    (2, 10, 0, 1.10);   -- ID: menos de la mitad
    -- estudiantes 1 y 5 sin fila -> NP

-- Clase 3 (2026-06-12, duración ~2.5 h)
INSERT INTO asistencia (id_clase, id_asistente, asistio, num_horas) VALUES
    (3, 1,  1, 2.30),
    (3, 2,  1, 2.41),
    (3, 3,  1, 2.15),
    (3, 5,  1, 2.02),
    (3, 6,  1, 2.55),
    (3, 7,  0, 0.64),   -- ID: 38 min
    (3, 8,  1, 1.80),
    (3, 9,  1, 2.10),
    (3, 10, 1, 2.20);
    -- estudiante 4 sin fila -> NP

-- Clase 4 (2026-06-13, duración ~4 h)
INSERT INTO asistencia (id_clase, id_asistente, asistio, num_horas) VALUES
    (4, 1,  1, 3.75),
    (4, 2,  1, 3.90),
    (4, 3,  1, 3.60),
    (4, 4,  1, 3.10),
    (4, 5,  1, 2.95),
    (4, 6,  1, 3.88),
    (4, 8,  1, 3.40),
    (4, 9,  1, 3.70),
    (4, 10, 1, 3.20);
    -- estudiante 7 sin fila -> NP

-- Clase 5 (2026-06-19, duración ~2.5 h)
INSERT INTO asistencia (id_clase, id_asistente, asistio, num_horas) VALUES
    (5, 1,  1, 2.20),
    (5, 2,  1, 2.35),
    (5, 3,  1, 2.28),
    (5, 4,  1, 1.90),
    (5, 5,  0, 0.97),   -- ID: 58 min
    (5, 6,  1, 2.45),
    (5, 7,  1, 2.30),
    (5, 8,  1, 2.05),
    (5, 9,  1, 2.33),
    (5, 10, 1, 2.15);

-- Clase 6 (2026-06-20, duración ~4 h)
INSERT INTO asistencia (id_clase, id_asistente, asistio, num_horas) VALUES
    (6, 1,  1, 3.80),
    (6, 2,  1, 3.95),
    (6, 3,  1, 3.55),
    (6, 4,  1, 3.25),
    (6, 5,  1, 3.10),
    (6, 6,  1, 3.90),
    (6, 7,  1, 3.45),
    (6, 8,  1, 3.15),
    (6, 9,  1, 3.65),
    (6, 10, 1, 3.30);
