# Paquete de reproducibilidad AirSimNH–PX4 para evaluación de aterrizaje UAV asistido por visión

[English version](README.md)

Este repositorio contiene el paquete público de reproducibilidad de un estudio de aterrizaje UAV basado en simulación. El estudio evalúa si una capa externa de asistencia visual en modo Offboard modifica el desempeño del aterrizaje autónomo sobre una plataforma señalizada dentro de un flujo AirSimNH–PX4 SITL.

El repositorio está orientado a reproducir analíticamente los resultados reportados a partir de archivos CSV curados, configuraciones congeladas, scripts de análisis, tablas derivadas y utilidades de verificación. No debe interpretarse como un paquete de validación en vuelo real.

## Descripción general del estudio

El experimento compara dos tratamientos pareados de aterrizaje:

| Tratamiento | Descripción | Corrección lateral visual activa |
|---|---|---|
| `T0` | Descenso autónomo base sobre la plataforma señalizada. La percepción ArUco puede registrarse, pero el error visual no se usa para control lateral. | No |
| `T1` | Descenso asistido por visión mediante plataforma ArUco, error visual en espacio de imagen y correcciones laterales Offboard acotadas enviadas por MAVLink/PX4. | Sí |

El diseño formal usa ocho escenarios simulados definidos por altura inicial, desplazamiento lateral y yaw. Cada escenario contiene diez repeticiones pareadas `T0/T1`, lo que produce 160 corridas formales aceptadas y 80 comparaciones pareadas.

## Hallazgos principales

| Resultado | `T0` | `T1` | Interpretación |
|---|---:|---:|---|
| Error terminal medio de aterrizaje | `0.5831 m` | `0.0206 m` | `T1` redujo sustancialmente el error terminal. |
| Tiempo medio del bucle de aterrizaje | `20.6399 s` | `28.8897 s` | `T1` requirió un bucle controlado de aterrizaje más largo. |
| Tasa de detección aceptada | `0.6889` | `0.9978` | `T1` mostró mayor disponibilidad de detección simulada. |
| Éxito simulado a nivel de protocolo | `80/80` | `80/80` | El éxito binario no discriminó entre tratamientos. |

El resultado debe interpretarse como una relación de compromiso precisión–tiempo–corrección: el tratamiento asistido por visión redujo el error terminal, pero incrementó el tiempo del bucle de aterrizaje y la actividad correctiva. No demuestra superioridad global de `T1`, validez en vuelo real, preparación operacional ni transferencia sim-to-real.

## Qué soporta este repositorio

| Nivel de reproducibilidad | Estado | Alcance |
|---|---|---|
| Reproducción analítica | Soportada | Reconstruir tablas curadas, salidas estadísticas de Fase 06 y artefactos de análisis desde CSV versionados. |
| Reejecución experimental | Documentada | Requiere una instalación local de AirSimNH–PX4 SITL, configuración del simulador, entorno PX4 y ajustes de ejecución dependientes de la máquina. |
| Auditoría de logs crudos | Limitada | Los logs completos de simulador/control/percepción, videos, capturas, artefactos temporales y entornos virtuales locales no se almacenan en Git. Su disponibilidad se documenta en el manifiesto. |

## Estructura del repositorio

```text
uav-landing-ai-reproducibility/
├─ .github/workflows/                 # Verificaciones públicas del repositorio, si están habilitadas
├─ configs/                            # Plantillas de experimento, percepción, control y entorno
├─ data/                               # Datos curados y referencias al manifiesto de logs crudos
├─ docs/                               # Metodología, notas de entorno, trazabilidad y soporte para artículo
├─ outputs/                            # Salidas derivadas versionadas y tablas de análisis
├─ reproducibility_manifest/           # Inventario de reproducibilidad y notas de disponibilidad
├─ scripts/                            # Scripts de reproducción y utilidades
├─ src/                                # Código fuente para análisis y verificación
│  └─ analysis/                        # Auditoría, descriptivos, hipótesis, escenarios e incidencias de Fase 06
├─ tests/                              # Utilidades de verificación y pruebas ligeras
├─ CITATION.cff                        # Metadatos de citación
├─ DATA_AVAILABILITY.md                # Declaración de disponibilidad de datos
├─ LICENSE                             # Licencia MIT
├─ README.md                           # README principal en inglés
├─ README.es.md                        # README en español
├─ REPRODUCIBILITY.md                  # Guía de reproducibilidad
├─ SOFTWARE_ENVIRONMENT.md             # Entorno de software y ejecución
└─ requirements.txt                    # Dependencias Python
```

## Artefactos incluidos

La rama pública incluye los materiales ligeros necesarios para inspeccionar y reproducir los resultados analíticos reportados:

- archivos CSV curados por corrida;
- tablas de corridas aceptadas y diferencias pareadas;
- resúmenes por escenario y tratamiento;
- configuraciones congeladas y plantillas públicas;
- salidas estadísticas de Fase 06;
- scripts de análisis;
- utilidades de verificación;
- documentación metodológica y de disponibilidad de datos.

## Artefactos no almacenados en Git

Los siguientes materiales se excluyen intencionalmente de Git porque son pesados, dependientes de la máquina, temporales o no necesarios para la reproducción analítica:

- logs completos de simulador/control/percepción;
- videos, capturas de pantalla y capturas diagnósticas;
- entornos virtuales locales;
- archivos `.env` locales;
- rutas específicas de máquina y estado local del simulador;
- artefactos temporales de diagnóstico.

Su inventario esperado y sus notas de disponibilidad se documentan en el manifiesto del repositorio. Si en el futuro se deposita un archivo crudo en Zenodo, Figshare, OSF u otro repositorio, el DOI y el checksum deben agregarse al manifiesto y a los archivos de disponibilidad de datos.

## Requisitos de software

### Reproducción analítica

Entorno analítico recomendado:

- Windows con PowerShell;
- Python 3.10;
- entorno virtual `.venv`;
- paquetes Python listados en `requirements.txt`:
  - `airsim==1.8.1`
  - `numpy`
  - `opencv-contrib-python`
  - `mavsdk`
  - `pymavlink`
  - `python-dotenv`
  - `scipy`
  - `pandas`
  - `matplotlib`

### Reejecución experimental completa

Una reejecución completa requiere infraestructura local adicional:

- AirSimNH;
- PX4 SITL mediante WSL2;
- canal MAVLink directo UDP en el puerto `14601`;
- nombre del vehículo simulado: `Drone1`;
- cámara inferior: `bottom_center`;
- diccionario ArUco: `DICT_4X4_50`;
- ID del marcador: `23`;
- configuración local del simulador/autopiloto derivada de las plantillas públicas en `configs/`.

No se deben versionar archivos `.env` locales, rutas dependientes de máquina, logs grandes generados ni entornos virtuales.

## Instalación

Desde una terminal de Windows PowerShell:

```powershell
cd "<REPO_ROOT>"
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para reutilizar un entorno virtual existente:

```powershell
cd "<REPO_ROOT>"
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Reproducir los resultados analíticos

La reproducción analítica recomendada en un solo comando es:

```powershell
.\scripts\reproduce_analysis.ps1
```

Una verificación exitosa debería reportar:

```text
Checks: 37 | OK: 37 | REVIEW: 0
```

El mismo flujo puede ejecutarse paso a paso:

```powershell
cd "<REPO_ROOT>"
.\.venv\Scripts\python.exe src\analysis\phase06_dataset_audit.py
.\.venv\Scripts\python.exe src\analysis\phase06_descriptive_statistics.py
.\.venv\Scripts\python.exe src\analysis\phase06_hypothesis_tests.py
.\.venv\Scripts\python.exe src\analysis\phase06_scenario_analysis.py
.\.venv\Scripts\python.exe src\analysis\phase06_incident_analysis.py
```

Las salidas analíticas esperadas incluyen:

- resúmenes de auditoría del dataset;
- estadística descriptiva por tratamiento;
- contrastes pareados de hipótesis y tamaños de efecto;
- resúmenes por escenario;
- análisis de incidencias y casos límite;
- tablas derivadas orientadas a publicación.

## Insumos analíticos centrales

El flujo de reproducción analítica depende de los archivos CSV curados y derivados versionados en la rama pública, incluyendo:

```text
data/curated/phase05/phase05_run_summary.csv
data/logs/phase05_experiments/summary/phase05_run_summary.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
outputs/tables/phase06_analysis/
```

## Límites de interpretación

Use los resultados con las siguientes restricciones de alcance:

1. La evidencia aplica a los escenarios controlados AirSimNH–PX4 SITL `S01`–`S08`.
2. La comparación aplica a los tratamientos `T0/T1` implementados y a las corridas formales aceptadas.
3. La condición terminal es una transición terminal simulada a nivel de protocolo, no una validación de contacto físico.
4. El flujo no valida vuelo real, dinámica de contacto físico, despliegue exterior, robustez ante viento, robustez ante iluminación, otros drones, otras cámaras, zonas de aterrizaje no preparadas ni una ley de control universal.
5. El éxito binario quedó saturado en ambos tratamientos; por tanto, precisión terminal, tiempo, disponibilidad de detección y actividad correctiva deben interpretarse de forma conjunta.

## Contribución metodológica

El repositorio soporta la contribución metodológica central del estudio: un flujo pareado, trazable y reproducible para evaluar cómo una capa de asistencia visual Offboard modifica el desempeño simulado de aterrizaje UAV bajo condiciones de escenario equivalentes.

La contribución no es:

- un nuevo marcador fiducial;
- un nuevo controlador PX4;
- una ley universal de aterrizaje;
- un paquete de validación en vuelo real;
- un benchmark completo de transferencia sim-to-real.

## Citación

Si utiliza este repositorio, cite el paquete de reproducibilidad y el manuscrito asociado cuando esté disponible.

```text
Molleapasa Gutierrez, V. UAV Landing AI Reproducibility Package. Paquete público de reproducibilidad para un experimento AirSimNH–PX4 SITL que compara descenso autónomo base y asistencia visual Offboard basada en ArUco para evaluación simulada de aterrizaje UAV.
```

Para metadatos de citación legibles por máquina, consulte `CITATION.cff`.

## Licencia

Este repositorio se publica bajo licencia MIT. Consulte `LICENSE`.

## Contacto

Autor: Vladimir Molleapasa Gutierrez  
Tema de investigación: flujo reproducible AirSimNH–PX4 para evaluación de aterrizaje autónomo UAV asistido por visión  
Repositorio: `https://github.com/elVladdi/uav-landing-ai-reproducibility`
