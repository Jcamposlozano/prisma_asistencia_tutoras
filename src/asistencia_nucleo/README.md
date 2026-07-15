# asistencia-nucleo

Extrae la asistencia desde **cualquier fuente** a un **estándar propio** (un diccionario →
**JSON**) y desde ese pivote la **renderiza a cualquier formato**. El JSON desacopla la
extracción de la presentación: agregar una fuente = un extractor; agregar un formato = un
renderer. **Arquitectura hexagonal**, sin base de datos (el estándar vive en memoria y se
serializa a JSON).

```
 fuentes (Zoom, matriz, Máster, ERC)  ──►  ESTÁNDAR (dict → JSON)  ──►  detalle / consolidado / …
        [ extractores ]                    [ domain: Persona/Sesion/         [ renderers ]
                                             Asistencia + EstadoCanonico ]
```

## Modelo canónico (`domain/`)

- `EstadoCanonico`: `PRESENTE | PARCIAL | AUSENTE | EXCUSA | DESCONOCIDO`.
- `Persona{id, nombre, correo, programa, cohorte}` · `Sesion{id, fecha, etiqueta, modulo, …}` ·
  `Asistencia{persona_id, sesion_id, estado, minutos, origen, nombre_origen}`.
- `Estandar{meta, personas, sesiones, asistencias}` con `to_json()` / `from_json()`.

Cada fuente mapea sus estados al canónico (Zoom/ERC por minutos; matriz x/o; Máster
X/EXCUSA/vacío); cada renderer traduce de vuelta al vocabulario de su formato.

## Arquitectura (hexagonal)

```
src/asistencia_nucleo/
  domain/       # PURO: modelos (estándar), normalizar, duracion, estados, matcher, dedup, estandar(merge)
  ports/        # ExtractorPort · EstandarExporterPort · RendererPort
  application/  # Extraer · ConstruirEstandar · ExportarJson · Renderizar
  adapters/
    extractores/  zoom_csv · matriz_dir · master_xlsx · erc_xlsm
    salida/       json_exporter · detalle_xlsx · consolidado_xlsx
  entrypoints/  cli.py     shared/  config.py · logger.py
```
`domain`/`application`/`ports` no tocan I/O (nada de openpyxl/csv); leer/escribir sólo en
`adapters/`. Verificado por `tests/test_arquitectura.py`.

## Instalación

```bash
pip install poetry
poetry install
```

## Uso

```bash
# Extraer una fuente al estándar JSON:
poetry run nucleo extraer --fuente erc="data/erc/FORMATO ASISTENCIA ERC10.xlsm" --modulo ERC10 --salida estandar.json
poetry run nucleo extraer --fuente zoom="data/zoom/participants.csv" --salida estandar.json
poetry run nucleo extraer --fuente matriz="data/matriz/DIGITAL BUSINESS" --salida estandar.json   # usa Listado*.xlsx vecino
poetry run nucleo extraer --fuente master="data/master/Asistencia Máster.xlsx" --hoja "2025-2 D.Business" --salida estandar.json

# Varias fuentes a la vez (merge por correo/nombre):
poetry run nucleo extraer --fuente erc=... --fuente master=... --salida estandar.json

# Renderizar el estándar a un formato:
poetry run nucleo render --estandar estandar.json --formato detalle     --salida detalle.xlsx
poetry run nucleo render --estandar estandar.json --formato consolidado --salida consolidado.xlsx
```

Tipos de fuente: `zoom` (participants_*.csv), `erc` (FORMATO .xlsm), `matriz` (carpeta de
cohorte + Listado), `master` (Asistencia Máster .xlsx). Umbrales de estado en `configs/base.yaml`.

## Tests

```bash
poetry run pytest        # domain, application (fakes), extractores (integración), arquitectura
poetry run ruff check .
```

Incluye un **cross-check**: el extractor ERC reproduce los conteos ya validados del proyecto
`asistencia-erc` (PRESENTE = A por sesión).

## Datos / PII

`data/` y las salidas (`*.json`, `*.xlsx`) están fuera del control de versiones.
