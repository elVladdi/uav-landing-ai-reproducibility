# Fase 06 - Consolidacion del Dataset Experimental

## Proposito

Este documento formaliza la consolidacion inicial del dataset experimental que
sirve como base para la Fase 06. Su finalidad es dejar constancia de que las
salidas curadas de Fase 05 fueron verificadas antes de realizar estadistica
descriptiva, contraste de hipotesis, analisis por escenario y discusion de
resultados.

La consolidacion del dataset es un requisito metodologico previo al analisis:
si las corridas, pares, escenarios o tablas no fueran consistentes, cualquier
resultado estadistico posterior podria quedar comprometido. Por ello, la Fase
06 inicia con una auditoria reproducible de los archivos experimentales
cerrados.

## Fuentes consolidadas

La consolidacion usa como fuentes principales las tablas producidas al cierre
de Fase 05:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

Estas tablas derivan de los logs y resumenes curados de Fase 05, y representan
el conjunto formal aceptado para comparacion entre:

- `T0`: descenso base sin correccion visual inteligente.
- `T1`: aterrizaje asistido por agente visual ArUco y MAVLink directo.

## Herramienta de verificacion

La verificacion se realizo mediante el script:

```text
src/analysis/phase06_dataset_audit.py
```

El script revisa la presencia de archivos de entrada, conteos esperados,
identificadores, cobertura de escenarios, cobertura por tratamiento y estructura
basica de la tabla de diferencias pareadas.

Las salidas generadas por la auditoria son:

```text
outputs/tables/phase06_analysis/phase06_dataset_audit.csv
outputs/tables/phase06_analysis/phase06_dataset_audit.md
```

## Resultado general de auditoria

El resultado final de la auditoria fue:

```text
Checks: 37 | OK: 37 | REVIEW: 0
```

Esto indica que no se detectaron inconsistencias bloqueantes en los archivos
curados utilizados como entrada para Fase 06.

## Verificacion de archivos

La auditoria confirmo la existencia de los cuatro insumos principales:

| Archivo | Estado |
|---|---:|
| `phase05_accepted_runs.csv` | OK |
| `phase05_pairwise_differences.csv` | OK |
| `phase05_scenario_treatment_summary.csv` | OK |
| `phase05_formal_report.md` | OK |

Con esto se verifica que la Fase 06 cuenta con las tablas necesarias para
analisis global, analisis pareado, analisis por escenario y trazabilidad del
cierre formal.

## Verificacion de corridas aceptadas

La tabla `phase05_accepted_runs.csv` fue revisada como fuente de corridas
individuales aceptadas. La auditoria confirmo:

| Criterio | Resultado observado | Resultado esperado | Estado |
|---|---:|---:|---:|
| Corridas aceptadas | 160 | 160 | OK |
| Identificadores `run_id` no vacios y unicos | 160 | 160 | OK |
| Filas sin escenario o tratamiento | 0 | 0 | OK |
| Estado de curacion | `accepted: 160` | Corridas aceptadas | OK |

Este resultado confirma que la base formal utilizada para el analisis contiene
unicamente las 160 corridas aceptadas del experimento T0/T1.

## Verificacion por escenario y tratamiento

La cobertura por escenario y tratamiento tambien fue validada. La estructura
esperada del experimento formal es:

- `8` escenarios (`S01` a `S08`).
- `2` tratamientos por escenario (`T0` y `T1`).
- `10` repeticiones por escenario y tratamiento.

La auditoria confirmo que cada celda escenario/tratamiento contiene exactamente
10 corridas aceptadas:

| Escenario | T0 | T1 | Estado |
|---|---:|---:|---:|
| S01 | 10 | 10 | OK |
| S02 | 10 | 10 | OK |
| S03 | 10 | 10 | OK |
| S04 | 10 | 10 | OK |
| S05 | 10 | 10 | OK |
| S06 | 10 | 10 | OK |
| S07 | 10 | 10 | OK |
| S08 | 10 | 10 | OK |

Por tanto, no existen celdas incompletas en la matriz formal de comparacion.

## Verificacion de pares T0/T1

La tabla `phase05_pairwise_differences.csv` fue revisada como fuente de
comparaciones pareadas. La auditoria confirmo:

| Criterio | Resultado observado | Resultado esperado | Estado |
|---|---:|---:|---:|
| Pares T0/T1 | 80 | 80 | OK |
| Identificadores de par no vacios y unicos | 80 | 80 | OK |
| Filas sin escenario | 0 | 0 | OK |
| Columnas T0/T1 presentes | Si | Si | OK |

La cobertura por escenario en la tabla pareada tambien fue completa:

| Escenario | Pares observados | Pares esperados | Estado |
|---|---:|---:|---:|
| S01 | 10 | 10 | OK |
| S02 | 10 | 10 | OK |
| S03 | 10 | 10 | OK |
| S04 | 10 | 10 | OK |
| S05 | 10 | 10 | OK |
| S06 | 10 | 10 | OK |
| S07 | 10 | 10 | OK |
| S08 | 10 | 10 | OK |

Esto habilita el uso de pruebas para muestras relacionadas en las metricas
continuas, siempre que el supuesto correspondiente sea evaluado para las
diferencias pareadas.

## Verificacion de resumen por escenario

La tabla `phase05_scenario_treatment_summary.csv` fue revisada para confirmar
la presencia de los escenarios experimentales definidos. La auditoria confirmo
la presencia de:

```text
S01, S02, S03, S04, S05, S06, S07, S08
```

Esta cobertura permite realizar analisis agregado y analisis desagregado por
condicion experimental, incluyendo altura inicial, desplazamiento lateral y yaw
inicial.

## Tratamiento de corridas excluidas y reemplazadas

Para el analisis formal de Fase 06 se mantiene el criterio definido en el
cierre de Fase 05:

```text
curation_status == accepted
```

Las corridas con estado `excluded` o `superseded` no se usan para promedios,
contrastes de hipotesis ni diferencias pareadas. Su funcion metodologica es
documentar trazabilidad, incidencias, reemplazos y control de calidad del
proceso experimental.

Este criterio evita mezclar datos diagnosticos, reemplazados o no comparables
con el bloque formal T0/T1.

## Decision de consolidacion

Con base en la auditoria reproducible, se declara que el dataset formal de
Fase 05 queda consolidado para Fase 06.

La decision se justifica porque:

- todos los archivos requeridos existen;
- las 160 corridas formales aceptadas estan presentes;
- los 80 pares T0/T1 estan completos;
- los 8 escenarios experimentales estan cubiertos;
- cada escenario contiene 10 repeticiones por tratamiento;
- cada escenario contiene 10 pares T0/T1;
- no hay identificadores duplicados en corridas ni pares;
- las columnas necesarias para comparacion T0/T1 estan disponibles.

Por tanto, la base queda habilitada para los siguientes entregables:

- estadistica descriptiva T0/T1;
- contraste de hipotesis;
- calculo de tamanos de efecto;
- analisis por escenario;
- revision de incidencias y fuentes de error;
- discusion del alcance del framework AirSim-PX4.

## Criterio de reproducibilidad

La consolidacion puede reproducirse ejecutando:

```powershell
& ".\.venv\Scripts\python.exe" src\analysis\phase06_dataset_audit.py
```

El comando debe ejecutarse desde la raiz del proyecto:

```text
<REPO_ROOT>
```

Un resultado valido para esta etapa debe reportar:

```text
Checks: 37 | OK: 37 | REVIEW: 0
```

Si una ejecucion posterior produce algun valor `REVIEW`, el analisis
estadistico debe pausarse hasta revisar la causa y documentar la correccion o
justificacion correspondiente.
