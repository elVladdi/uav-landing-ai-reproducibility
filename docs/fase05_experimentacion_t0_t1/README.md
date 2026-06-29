# Fase 05 - Experimentacion T0/T1

La Fase 05 corresponde al experimento formal de comparacion entre el
tratamiento base `T0` y el tratamiento visual asistido `T1` para aterrizaje
autonomo de UAV en AirSimNH + PX4 SITL.

Estado formal: **cerrada al 2026-06-08**, con `160/160` corridas formales
aceptadas, `80` pares T0/T1 completos y `16/16` celdas escenario/tratamiento
completas.

## Pipeline reproducible

La siguiente figura resume el flujo reproducible usado para cada corrida formal:
planificacion, preparacion, ejecucion T0/T1, registro de logs crudos, curacion
de datos, calculo de metricas y generacion del reporte formal.

![Pipeline reproducible de una corrida formal en Fase 05](<Imagenes/Pipeline reproducible de una corrida formal.png>)

La regla operativa del experimento fue conservar los logs crudos y usar solo
corridas con `curation_status=accepted` para promedios, tablas finales y
comparacion pareada T0/T1. Las corridas `excluded` y `superseded` permanecen
documentadas para trazabilidad metodologica.

## Scripts principales

- `src/experiments/phase05_generate_run_plan.py`: genera los comandos formales
  por bloque.
- `src/perception/clear_landing_markers.py`: elimina marcadores residuales antes
  y despues de cada corrida.
- `src/control/run_phase05_yaw_setup.py`: configura yaw inicial absoluto cuando
  corresponde.
- `src/perception/spawn_fiducial_marker.py`: crea el marcador ArUco del
  escenario.
- `src/control/run_phase05_t0_baseline_descent.py`: ejecuta `T0`, descenso base
  sin correccion visual inteligente.
- `src/control/run_phase05_t1_visual_descent.py`: ejecuta `T1`, descenso visual
  asistido por ArUco y MAVLink directo.
- `src/analysis/phase05_metrics.py`: genera el resumen curado
  `phase05_run_summary.csv`.
- `src/analysis/phase05_formal_report.py`: genera tablas finales y reporte
  formal.

## Evidencia curada

Las salidas versionadas principales son:

- `data/logs/phase05_experiments/summary/phase05_run_summary.csv`
- `outputs/tables/phase05_experiments/phase05_accepted_runs.csv`
- `outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv`
- `outputs/tables/phase05_experiments/phase05_pairwise_differences.csv`
- `outputs/tables/phase05_experiments/phase05_completion_check.csv`
- `outputs/tables/phase05_experiments/phase05_formal_report.md`

## Documentos de la fase

| Documento | Contenido |
|---|---|
| `01_objetivo_y_alcance.md` | Objetivo, alcance y criterio de salida de la fase. |
| `02_diseno_experimental_t0_t1.md` | Tratamientos, unidad de analisis y escenarios formales. |
| `03_configuracion_congelada.md` | Configuracion congelada usada por T0 y T1. |
| `04_protocolo_piloto.md` | Protocolo inicial de piloto minimo. |
| `05_diccionario_datos_metricas.md` | Variables, campos y metricas registradas. |
| `06_criterios_inclusion_exclusion.md` | Criterios de inclusion, exclusion y validez. |
| `07_resultados_piloto.md` | Resultados piloto y verificacion preliminar. |
| `08_plan_analisis_estadistico.md` | Plan de comparacion formal y analisis pareado. |
| `09_known_issues.md` | Incidencias tecnicas y metodologicas. |
| `10_regla_curacion_datos.md` | Regla de curacion `accepted`, `excluded`, `superseded`. |
| `11_protocolo_ejecucion_formal.md` | Procedimiento de ejecucion por bloques. |
| `12_cierre_fase05.md` | Criterios, archivos y decision de cierre formal. |
| `13_avance_ejecucion_formal.md` | Bitacora de ejecucion formal por bloques. |
