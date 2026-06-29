# Cierre de Fase 05

## Criterio de cierre

La Fase 05 se considera cerrada cuando existe evidencia reproducible de:

- plan formal generado para 160 corridas;
- logs crudos por corrida;
- resumen curado `phase05_run_summary.csv`;
- tabla de corridas aceptadas;
- tabla por escenario y tratamiento;
- tabla de diferencias pareadas T0/T1;
- registro de corridas `excluded` y `superseded`;
- reporte final generado desde los datos.

## Archivos de cierre

Los archivos operativos de cierre son:

```text
data/logs/phase05_experiments/summary/phase05_run_summary.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_completion_check.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

## Versionado reproducible

Los logs crudos, capturas, figuras anotadas y salidas pesadas permanecen
excluidos del repositorio por `.gitignore`. Para revision academica y
trazabilidad, si se versionan los resumenes curados y tablas livianas de Fase
05.

El archivo `data/logs/phase05_experiments/summary/phase05_run_summary.csv` es
la tabla curada base. Las tablas de
`outputs/tables/phase05_experiments/` son salidas reproducibles generadas desde:

```powershell
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```

## Criterio minimo para informe

Para el informe de tesis, usar solo corridas con:

```text
curation_status == accepted
```

Las corridas `excluded` y `superseded` se reportan como control de calidad,
pero no se usan para promedios ni pruebas comparativas.

## Decision de cierre

Al 2026-06-08, la Fase 05 queda cerrada como experimento formal completo.
La evidencia curada muestra:

- `160/160` corridas formales aceptadas;
- `80` pares T0/T1 aceptados;
- `16/16` celdas escenario/tratamiento completas;
- ninguna celda formal faltante;
- `164` registros con `curation_status=accepted`, de los cuales `160`
  corresponden al plan formal y `4` son aceptados no formales excluidos del
  reporte formal;
- `8` registros con `curation_status=excluded`;
- `12` registros con `curation_status=superseded`.

La decision de cierre es aceptar la Fase 05 como completa para analisis,
figuras y redaccion de resultados. Las corridas `excluded` y `superseded`
permanecen documentadas como control de calidad y trazabilidad metodologica,
pero no forman parte de los promedios ni de las comparaciones pareadas.

No quedan corridas formales pendientes. Cualquier ejecucion adicional debe
registrarse como corrida no formal o como nueva enmienda metodologica, sin
sobrescribir logs crudos ni modificar la secuencia formal cerrada.

## Proximo uso de resultados

Los resultados de Fase 05 alimentan:

- tablas comparativas T0/T1;
- graficos de error final, tiempo y estabilidad;
- discusion de tasa de exito;
- analisis de limitaciones;
- conclusiones de la tesis.

La fuente primaria para esta etapa es el conjunto de tablas curadas versionadas
en `outputs/tables/phase05_experiments/`, regeneradas desde
`phase05_run_summary.csv` con los scripts indicados arriba.
