# Consolidados de asistencia — integración con el validador

Conecta la salida del **integrador de asistencia** (repo `samyrami/Asistencia-prisma`)
con nuestra base para generar los **consolidados** por SQL.

## El flujo

```
FORMATO ASISTENCIA ERC10.xlsm          (fuente cruda, la que descargan hoy)
        │  ── integrador (nucleo extraer) ──►
estandar.json   { personas, sesiones, asistencias(estado, minutos) }
        │  ── cargar_estandar.sql (json_each) ──►
reporte_asistencia.db   (persona · sesion · asistencia)
        │  ── consolidados.sql ──►
Consolidados (matriz P/D/o, %Asist, no asistentes, por sesión, maestría)
```

El integrador **no usa base de datos**: entrega un JSON. Nosotros lo aterrizamos a
SQLite y de ahí salen todos los reportes con queries.

## Las llamadas (reproducir de cero)

```bash
# 1) Generar el estándar desde el archivo real (herramienta del compañero)
poetry run nucleo extraer \
  --fuente 'erc=Documentos Referencia/FORMATO ASISTENCIA ERC10.xlsm' \
  --modulo ERC10 --salida scripts/asistencia/estandar.json

# 2) Crear la base y cargar el JSON  (nuestras "llamadas")
sqlite3 reporte_asistencia.db ".read scripts/asistencia/schema_asistencia.sql"
sqlite3 reporte_asistencia.db ".read scripts/asistencia/cargar_estandar.sql"   # usa readfile()/json_each

# 3) Consolidados (o abrir la .db en DBeaver y correr consolidados.sql)
sqlite3 -header -column reporte_asistencia.db ".read scripts/asistencia/consolidados.sql"
```

> El loader lee `/tmp/estandar.json` por defecto (ver la ruta en `cargar_estandar.sql`).
> Para otra ruta, edita esa línea o copia el JSON allí.

## Alineación de modelo (importante)

El modelo v1 del tablero usaba `asistio`(0/1) + `num_horas`. El integrador real usa el
**estándar canónico**, así que alineamos:

| tablero v1            | estándar del integrador (v2)                         |
|-----------------------|------------------------------------------------------|
| `estudiante`          | `persona` (+ `programa`, `cohorte`)                  |
| `clase`               | `sesion` (+ `modulo`, `etiqueta`, `duracion_min`)    |
| `asistio` 0/1         | `estado` = PRESENTE·PARCIAL·AUSENTE·EXCUSA·DESCONOCIDO|
| `num_horas`           | `minutos`                                            |
| NP deducido (sin fila)| AUSENTE guardado como **fila explícita** (minutos 0) |

Umbrales del integrador: PRESENTE ≥ 60 min · PARCIAL ≥ 29 min · si no AUSENTE.

## Los consolidados (`consolidados.sql`)

- **Q1** Matriz Persona × sesión (P/D/o/E) + #Pres/#Parc/#Aus + %Asist → igual a su `consolidado.xlsx`.
- **Q2** Resumen por estudiante (ordenado por %; los de menor asistencia primero).
- **Q3** Listado de no asistentes por sesión.
- **Q4** Resumen por sesión (% de asistencia de cada clase).
- **Q5** Consolidado de toda la maestría (por estudiante, suma de módulos).

## Datos de la corrida (ERC10, junio 2026)

38 personas · 6 sesiones · 228 asistencias · 93 presentes / 7 parciales / 128 ausentes.
5 estudiantes con 100 %. `sin_match = 7` (filas que el integrador no pudo cruzar contra el
roster — a validar con el dueño del algoritmo).
