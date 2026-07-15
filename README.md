# student-service — Reportes de la maestría (EIG · UIDE)

Monolito que automatiza los **dos informes** que la coordinación arma a mano cada
bimestre por materia: el **Informe para comité curricular** (PPTX/PDF) y el
**Informe final** (PDF). De los archivos crudos de la plataforma a los documentos
con la marca institucional, con un comando por paso.

```
participants_*.csv (Zoom)        CSV encuesta · eval. docente · calificaciones
        │                                        │
        │  nucleo extraer (asistencia_nucleo)    │  reporte datos-final
        ▼                                        ▼
  estandar.json ──► reporte cargar ──► SQLite    datos_final.json
                          │                        │
                          ▼                        ▼
                   reporte comite ◄────────────── (incidencias)
                   (PPTX + PDF)              reporte final (HTML + PDF)
```

## Estructura (arquitectura hexagonal, plantilla ESIC)

```
src/
├── asistencia_nucleo/    # Integrador de asistencia (autor: Samuel Ramírez,
│                         #   github.com/samyrami/Asistencia-prisma — vendorizado).
│                         #   Extrae cualquier fuente (zoom/erc/master/matriz) al
│                         #   estándar canónico. domain/application/ports/adapters.
└── student_service/      # Servicio de reportes (este repo).
    ├── domain/           #   Reglas puras: estados A/NP/D, escala de encuesta,
    │                     #   umbral de aprobación (70), distribución de asistencia.
    ├── application/      #   Casos de uso: CargarAsistencia, GenerarInformeComite,
    │                     #   ConstruirDatosFinal, GenerarInformeFinal.
    ├── ports/            #   Contratos: repositorio, lectores CSV, renderers.
    ├── adapters/         #   SQLite, lectores CSV de la plataforma,
    │   └── salida/       #   PPTX (comité) y HTML→PDF (final) con marca UIDE/eig.
    ├── entrypoints/      #   CLI `reporte` (+ api/worker de la plantilla).
    └── shared/           #   config/logger/shutdown (plantilla ESIC).
scripts/asistencia/       # SQL para DBeaver (schema/consolidados) + demo sintética.
configs/  tests/          # Config por entorno · tests de dominio y arquitectura.
```

## Uso

```bash
poetry install

# 1) Asistencia: archivos planos -> estándar canónico
poetry run nucleo extraer --fuente zoom=participants_s1.csv \
    --programa "Energías Renovables" --cohorte C10 --salida estandar.json

# 2) Estándar -> SQLite  (--densificar si la fuente no trae roster, p.ej. zoom)
poetry run reporte cargar --estandar estandar.json --db reporte.db --densificar

# 3) CSV de encuesta/docente/calificaciones -> datos del informe final
poetry run reporte datos-final --encuesta encuesta.csv --docente docente.csv \
    --calificaciones notas.csv --profesor "Nombre Docente" \
    --materia "Energía de la biomasa" --cohorte "10 NOV25" --salida datos.json

# 4) Los dos informes
poetry run reporte comite --db reporte.db --plantilla plantilla_comite.pptx \
    --datos datos.json --salida informe_comite.pptx
poetry run reporte final --datos datos.json --salida informe_final
```

## Datos / PII

Los archivos de la plataforma, las bases generadas, los informes y la plantilla
PPTX de comité contienen **datos personales de estudiantes** y están **fuera del
control de versiones** (ver `.gitignore`). El repo solo lleva código, SQL y
plantillas de configuración.

## Validación

- Las **12 medias de la encuesta** reproducen exactas el informe original (ERC10).
- Matriz A/NP/D, distribución y "No asisten" cuadran contra el consolidado real.
- Reprobados = `Final Score < 70` (reproduce los casos del informe original).
- Pendiente de calibrar: la fórmula manual de "Calificación docente" y "media
  encuesta" de la coordinación (hoy se calculan como promedios transparentes).
