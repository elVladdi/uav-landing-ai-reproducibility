# UAV Landing AI

Repositorio del proyecto de investigación **UAV Landing AI**, orientado al diseño, integración y evaluación de un agente visual para apoyar el aterrizaje autónomo de un vehículo aéreo no tripulado (UAV) sobre una plataforma señalizada en un entorno controlado de simulación.

El proyecto compara dos tratamientos:

- `T0`: aterrizaje base sin corrección lateral visual inteligente.
- `T1`: aterrizaje asistido por un agente visual basado en detección ArUco y control lateral mediante MAVLink directo.

La evidencia experimental se generó en simulación con AirSimNH, PX4 SITL, cámara inferior simulada, Python 3.10 y scripts reproducibles. El alcance corresponde a validación en entorno simulado; no representa todavía una validación en vuelo real.

## Estado actual

El repositorio se encuentra en **cierre analítico de Fase 06**. Las fases técnicas y experimentales previas quedaron cerradas y la comparación formal `T0/T1` ya fue analizada estadísticamente.

| Fase | Propósito | Estado |
| --- | --- | --- |
| Fase 01 | Definición del sistema, alcance, tratamientos y métricas preliminares. | Cerrada |
| Fase 02 | Configuración y validación del entorno AirSimNH/PX4/Python. | Cerrada |
| Fase 03 | Validación inicial de percepción visual y evidencia anotada. | Cerrada |
| Fase 04 | Integración percepción-control con ArUco, MAVLink directo y descenso asistido. | Cerrada |
| Fase 05 | Ejecución formal de escenarios `T0/T1`, curación de corridas y dataset experimental. | Cerrada |
| Fase 06 | Auditoría, estadística descriptiva, contraste de hipótesis, análisis por escenario, incidencias, discusión, limitaciones y conclusiones. | Cerrada |

## Resultado principal

La Fase 06 analizó **160 corridas aceptadas**, organizadas como **80 pares completos `T0/T1`** en ocho escenarios (`S01`-`S08`), con diez pares por escenario.

Los resultados principales son:

- `T1` redujo de forma marcada el error final de aterrizaje: media `T0 = 0.5831 m`, media `T1 = 0.0206 m`, con contraste pareado significativo.
- `T1` incrementó el tiempo de aterrizaje: media `T0 = 20.6399 s`, media `T1 = 28.8897 s`, lo que refleja una estrategia más correctiva y deliberada.
- La detección visual aceptada fue muy superior en `T1` (`0.9978`) frente a `T0` (`0.6889`), y las pérdidas de detección fueron sustancialmente menores.
- No se observó diferencia en éxito/fracaso porque ambos tratamientos completaron `80/80` corridas aceptadas.
- `T1` modificó significativamente la dinámica lateral de aproximación: presentó mayor dispersión visual/lateral, más actividad correctiva y mayor intensidad de comando horizontal que `T0`.

En términos interpretativos, el agente visual mejora de manera clara la precisión final del aterrizaje a cambio de mayor tiempo de ejecución y mayor actividad correctiva durante la aproximación. La mejora se sostiene dentro del marco simulado y bajo los escenarios controlados del experimento.

## Estructura del repositorio

```text
uav-landing-ai/
├─ configs/                         # Configuraciones del entorno y del experimento
├─ data/                            # Datos ligeros y resúmenes curados
├─ docs/                            # Documentación metodológica y entregables por fase
│  ├─ fase01_definicion_del_sistema_delimitacion_del_alcance/
│  ├─ fase02_entorno_experimental/
│  ├─ fase03_percepcion_visual/
│  ├─ fase04_integracion_autopiloto/
│  ├─ fase05_experimentacion_t0_t1/
│  └─ fase06_analisis_resultados/
├─ experiments/                     # Material de ejecución experimental
├─ outputs/                         # Salidas ligeras versionables
│  └─ tables/phase06_analysis/      # Tablas finales de análisis de Fase 06
├─ scripts/                         # Utilidades del proyecto
├─ src/                             # Código fuente
│  └─ analysis/                     # Scripts de auditoría y análisis estadístico
├─ requirements.txt                 # Dependencias Python
└─ README.md                        # Este documento
```

Los logs crudos, entornos virtuales y salidas pesadas no forman parte del versionado principal. El repositorio conserva los documentos, scripts, tablas ligeras y resúmenes necesarios para auditoría académica y reproducción del análisis.

## Documentación clave

- Índice documental general: [`docs/README.md`](docs/README.md)
- Trazabilidad de fases y objetivos: [`docs/trazabilidad_fases_objetivos.md`](docs/trazabilidad_fases_objetivos.md)
- Justificación metodológica de fases: [`docs/justificacion_metodologica_fases.md`](docs/justificacion_metodologica_fases.md)
- Diseño experimental `T0/T1`: [`docs/fase05_experimentacion_t0_t1/02_diseno_experimental_t0_t1.md`](docs/fase05_experimentacion_t0_t1/02_diseno_experimental_t0_t1.md)
- Cierre de ejecución formal: [`docs/fase05_experimentacion_t0_t1/13_avance_ejecucion_formal.md`](docs/fase05_experimentacion_t0_t1/13_avance_ejecucion_formal.md)
- Conclusiones de Fase 06: [`docs/fase06_analisis_resultados/09_conclusiones_fase06.md`](docs/fase06_analisis_resultados/09_conclusiones_fase06.md)
- Ayuda memoria de Fase 06: [`docs/fase06_analisis_resultados/10_ayuda_memoria_fase06.md`](docs/fase06_analisis_resultados/10_ayuda_memoria_fase06.md)

## Entorno de trabajo

Requisitos principales:

- Windows con PowerShell.
- Python 3.10.
- Entorno virtual `.venv`.
- Dependencias de `requirements.txt`, incluida `scipy` para contrastes estadísticos.
- AirSimNH y PX4 SITL para reproducir ejecución experimental completa.

Instalación recomendada:

```powershell
cd "<REPO_ROOT>"
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si el entorno virtual ya existe:

```powershell
cd "<REPO_ROOT>"
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Reproducción del análisis de Fase 06

Los scripts de Fase 06 generan las tablas ligeras ubicadas en `outputs/tables/phase06_analysis/`.

```powershell
cd "<REPO_ROOT>"
.\.venv\Scripts\python.exe src\analysis\phase06_dataset_audit.py
.\.venv\Scripts\python.exe src\analysis\phase06_descriptive_statistics.py
.\.venv\Scripts\python.exe src\analysis\phase06_hypothesis_tests.py
.\.venv\Scripts\python.exe src\analysis\phase06_scenario_analysis.py
.\.venv\Scripts\python.exe src\analysis\phase06_incident_analysis.py
```

Salidas esperadas:

- Auditoría del dataset experimental.
- Estadística descriptiva por tratamiento.
- Contrastes de hipótesis y tamaños de efecto.
- Análisis por escenario.
- Análisis de incidencias y fuentes de error.

## Criterios de interpretación

El análisis debe leerse con cuatro precauciones:

- La comparación es válida dentro de los escenarios simulados definidos.
- La precisión final y la dinámica lateral de aproximación no son métricas equivalentes.
- La ausencia de diferencia en éxito/fracaso se explica porque el conjunto aceptado contiene corridas exitosas en ambos tratamientos.
- Los resultados no sustituyen una campaña de validación física; constituyen una base experimental reproducible para la tesis y para trabajo futuro.

## Próximo uso académico

Con Fase 06 cerrada, el repositorio queda preparado para alimentar:

- capítulo de metodología;
- capítulo de resultados;
- discusión de hipótesis;
- limitaciones y trabajo futuro;
- artículo o informe final del proyecto.

La siguiente etapa natural ya no es ejecutar más corridas, sino convertir la evidencia consolidada en redacción académica final, tablas publicables y figuras para tesis o artículo.
