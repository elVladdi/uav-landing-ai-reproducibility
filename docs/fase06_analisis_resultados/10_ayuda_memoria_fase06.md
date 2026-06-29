# Fase 06 - Ayuda Memoria

## Proposito

Este documento resume la informacion operativa necesaria para reproducir,
revisar y defender la Fase 06. Incluye documentos generados, scripts usados,
comandos de ejecucion, archivos de salida, decisiones metodologicas y resultados
clave.

La ayuda memoria no reemplaza los entregables analiticos. Su funcion es
preservar trazabilidad y facilitar que la Fase 06 pueda reconstruirse sin
depender de memoria personal o de pasos no documentados.

## Ruta base del proyecto

```text
<REPO_ROOT>
```

Todos los comandos deben ejecutarse desde esa ruta.

## Documentos de Fase 06

Los entregables redactados son:

```text
docs/fase06_analisis_resultados/01_objetivo_y_alcance_fase06.md
docs/fase06_analisis_resultados/02_consolidacion_dataset_experimental.md
docs/fase06_analisis_resultados/03_estadistica_descriptiva_t0_t1.md
docs/fase06_analisis_resultados/04_contraste_hipotesis.md
docs/fase06_analisis_resultados/05_analisis_por_escenario.md
docs/fase06_analisis_resultados/06_analisis_incidencias_fuentes_error.md
docs/fase06_analisis_resultados/07_discusion_resultados.md
docs/fase06_analisis_resultados/08_limitaciones_alcance_framework.md
docs/fase06_analisis_resultados/09_conclusiones_fase06.md
docs/fase06_analisis_resultados/10_ayuda_memoria_fase06.md
```

## Insumos principales de Fase 05

La Fase 06 usa como base los archivos curados de Fase 05:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

El criterio formal de entrada al analisis fue:

```text
curation_status == accepted
```

Las corridas `excluded` y `superseded` se conservan como trazabilidad, pero no
se usan para promedios, contrastes de hipotesis ni comparaciones pareadas.

## Scripts de Fase 06

Los scripts creados para la fase son:

```text
src/analysis/phase06_dataset_audit.py
src/analysis/phase06_descriptive_statistics.py
src/analysis/phase06_hypothesis_tests.py
src/analysis/phase06_scenario_analysis.py
src/analysis/phase06_incident_analysis.py
```

## Comandos de reproduccion

Ejecutar desde la raiz del proyecto:

```powershell
cd "<REPO_ROOT>"
```

Auditoria del dataset:

```powershell
& ".\.venv\Scripts\python.exe" src\analysis\phase06_dataset_audit.py
```

Estadistica descriptiva:

```powershell
& ".\.venv\Scripts\python.exe" src\analysis\phase06_descriptive_statistics.py
```

Contraste de hipotesis:

```powershell
& ".\.venv\Scripts\python.exe" src\analysis\phase06_hypothesis_tests.py
```

Analisis por escenario:

```powershell
& ".\.venv\Scripts\python.exe" src\analysis\phase06_scenario_analysis.py
```

Analisis de incidencias:

```powershell
& ".\.venv\Scripts\python.exe" src\analysis\phase06_incident_analysis.py
```

## Dependencia estadistica

Para el contraste de hipotesis se instalo `scipy` en el entorno virtual del
proyecto. Esto permite usar:

- Shapiro-Wilk;
- t de Student pareada;
- Wilcoxon signed-rank;
- pruebas estadisticas implementadas por `scipy.stats`.

Instalacion usada:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install scipy
```

Version instalada:

```text
scipy 1.15.3
```

## Salidas generadas

Las salidas de Fase 06 se encuentran en:

```text
outputs/tables/phase06_analysis/
```

Archivos generados:

```text
phase06_categorical_tests.csv
phase06_dataset_audit.csv
phase06_dataset_audit.md
phase06_descriptive_by_scenario_treatment.csv
phase06_descriptive_by_treatment.csv
phase06_descriptive_statistics.md
phase06_effect_sizes.csv
phase06_hypothesis_tests.csv
phase06_hypothesis_tests.md
phase06_incident_analysis.md
phase06_incident_extreme_runs.csv
phase06_incident_summary.csv
phase06_pairwise_difference_summary.csv
phase06_scenario_analysis.csv
phase06_scenario_analysis.md
phase06_scenario_factor_summary.csv
phase06_scenario_rankings.csv
phase06_success_abort_summary.csv
phase06_terminal_state_counts.csv
```

## Verificacion de consolidacion

La auditoria inicial del dataset debe reportar:

```text
Checks: 37 | OK: 37 | REVIEW: 0
```

Resultado consolidado:

- `160/160` corridas aceptadas.
- `80/80` pares T0/T1.
- `8/8` escenarios presentes.
- `10` pares por escenario.
- `10` corridas T0 y `10` corridas T1 por escenario.
- Identificadores de corrida y par sin duplicados.

## Decisiones metodologicas clave

Las decisiones principales fueron:

- usar solo corridas `accepted` para el bloque formal;
- preservar `excluded` y `superseded` como trazabilidad, no como datos del
  contraste;
- analizar T0/T1 bajo diseno pareado;
- evaluar normalidad de diferencias con Shapiro-Wilk;
- aplicar t pareada cuando la diferencia cumple normalidad;
- aplicar Wilcoxon signed-rank cuando la diferencia no cumple normalidad;
- usar McNemar exacto para exito/fallo pareado;
- interpretar p-valores junto con magnitud practica;
- no extrapolar resultados de simulacion a vuelo fisico real;
- no presentar ArUco como detector nuevo;
- no presentar T1 como ley universal de control;
- distinguir precision final, dinamica lateral de aproximacion y exito terminal.

## Alineacion con el perfil del proyecto

El perfil define como objetivo general desarrollar y evaluar un
framework reproducible AirSim-PX4 para aterrizaje autonomo asistido por vision
Offboard sobre una plataforma senalizada, en simulacion controlada.

Tambien define como metricas principales:

- error final de posicionamiento;
- tiempo de aterrizaje;
- dinamica lateral de aproximacion y actividad correctiva;
- tasa de exito.

HE3 se evalua como modificacion significativa de la dinamica lateral de
aproximacion. La deteccion aceptada queda como metrica de apoyo para interpretar
el comportamiento tecnico del framework.

## Resultados clave

### Dataset

La base experimental formal queda cerrada:

- `160` corridas aceptadas;
- `80` pares T0/T1;
- `8` escenarios;
- `0` abortos en el conjunto aceptado.

### Error final

T1 reduce significativamente el error final frente a T0:

| Tratamiento | Error final medio |
|---|---:|
| T0 | 0.5831 m |
| T1 | 0.0206 m |

Resultado HE1:

```text
Wilcoxon signed-rank, p = 3.92476e-15
Decision: rechazar H0
```

### Tiempo de aterrizaje

T1 modifica significativamente el tiempo de aterrizaje y tarda mas que T0:

| Tratamiento | Tiempo medio |
|---|---:|
| T0 | 20.6399 s |
| T1 | 28.8897 s |

Resultado HE2:

```text
t pareada, p = 2.01596e-42
Decision: rechazar H0
```

### Dinamica lateral de aproximacion

HE3 queda respaldada como modificacion significativa de la dinamica lateral de
aproximacion. El primer indicador es la dispersion visual/lateral combinada:

| Tratamiento | Dispersion visual combinada media |
|---|---:|
| T0 | 0.0642 |
| T1 | 0.0869 |

Resultado HE3:

```text
Wilcoxon signed-rank bilateral, p = 0.0271772
Decision: rechazar H0
```

Indicadores complementarios de actividad correctiva:

| Indicador | Diferencia media | Prueba | p-valor |
|---|---:|---|---:|
| Conteo de comandos `T1 - T0` | 46.6625 | t pareada | 7.4351e-42 |
| Maximo comando horizontal `T1 - T0` | 0.0674 m/s | Wilcoxon signed-rank | 7.39174e-15 |

Interpretacion:

```text
T1 modifica significativamente la dinamica lateral de aproximacion. Su
correccion activa genera mayor dispersion visual/lateral, mas comandos y mayor
intensidad de comando horizontal, lo que es coherente con la reduccion del
error final.
```

### Exito/fallo

Ambos tratamientos alcanzan exito completo:

| Resultado | Conteo |
|---|---:|
| T0 exitos | 80 |
| T1 exitos | 80 |
| Abortos T0 | 0 |
| Abortos T1 | 0 |

Resultado HE4:

```text
McNemar exacto, p = 1
Decision: no rechazar H0
```

### Deteccion aceptada

La deteccion aceptada mejora en T1, pero se interpreta como metrica de apoyo:

| Tratamiento | Tasa media de deteccion aceptada |
|---|---:|
| T0 | 0.6889 |
| T1 | 0.9978 |

Perdidas de deteccion:

| Tratamiento | Perdidas medias |
|---|---:|
| T0 | 21.8750 |
| T1 | 0.2500 |

## Resultados por escenario

T1 reduce el error final en los ocho escenarios.

Mayores reducciones de error:

| Escenario | Reduccion media |
|---|---:|
| S03 | 0.7652 m |
| S07 | 0.7436 m |
| S04 | 0.7377 m |

Menores reducciones de error:

| Escenario | Reduccion media |
|---|---:|
| S05 | 0.3220 m |
| S02 | 0.3629 m |
| S01 | 0.3792 m |

El desplazamiento lateral inicial de `0.8 m` fue la condicion donde T1 mostro
mayor utilidad practica.

## Incidencias principales

T0 presento:

- mas perdidas de deteccion;
- mayor latencia media;
- latencias extremas superiores a `500 ms`;
- errores finales maximos cercanos a `0.8895 m`.

T1 presento:

- deteccion aceptada casi completa;
- menor error final maximo (`0.0473 m`);
- mayor tiempo de aterrizaje;
- comandos horizontales activos hasta `0.1000 m/s`;
- mayor dispersion visual en escenarios exigentes.

## Formulacion final defendible

La formulacion recomendada para cierre de tesis es:

```text
En simulacion AirSim-PX4 controlada, el tratamiento T1 con asistencia visual
Offboard reduce significativamente el error final de aterrizaje frente al
descenso base T0 y mejora la disponibilidad de deteccion, manteniendo exito
terminal completo. Sin embargo, T1 incrementa el tiempo de maniobra y modifica
la dinamica lateral mediante mayor actividad correctiva. Por tanto, T1 es mas
preciso, pero no universalmente superior en todos los criterios.
```

## Alcance final

Los resultados son validos para:

- simulacion AirSim-PX4;
- plataforma senalizada;
- escenarios `S01` a `S08`;
- tratamientos T0/T1 definidos;
- corridas aceptadas del bloque formal;
- metricas registradas en el proyecto.

Los resultados no validan:

- vuelo fisico real;
- otros drones;
- otras camaras;
- terrenos naturales no preparados;
- condiciones visuales no evaluadas;
- un detector nuevo;
- una ley universal de control.

## Cierre operativo

La Fase 06 queda cerrada cuando:

- el auditor reporta `37 OK / 0 REVIEW`;
- los scripts de analisis se ejecutan sin error;
- los outputs estan generados en `outputs/tables/phase06_analysis/`;
- los entregables `01` a `10` estan redactados;
- las conclusiones responden al perfil del proyecto;
- las limitaciones estan declaradas sin sobreafirmar el alcance.

Con este documento, la Fase 06 queda documentada tanto en su dimension
analitica como en su dimension operativa.
