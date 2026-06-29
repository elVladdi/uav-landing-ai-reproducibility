# Plan de Analisis Estadistico

## Preparacion de datos

Primero se genera una tabla por corrida:

```powershell
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```

La tabla esperada es:

```text
data/logs/phase05_experiments/summary/phase05_run_summary.csv
```

Y las tablas derivadas son:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_completion_check.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

Antes de calcular metricas comparativas, filtrar:

```text
curation_status == accepted
```

Las corridas `excluded` y `superseded` permanecen en el resumen para trazabilidad
metodologica, pero no alimentan medias, graficos comparativos ni pruebas
estadisticas.

## Estadistica descriptiva

Para cada tratamiento y escenario:

- media;
- mediana;
- desviacion estandar;
- minimo;
- maximo;
- rango intercuartil;
- tasa de exito.

## Comparacion T0/T1

La comparacion debe ser pareada por `scenario_id`, `treatment_pair_id` y
`repetition` cuando sea posible.

Para variables continuas:

- verificar normalidad de diferencias con Shapiro-Wilk;
- usar t de Student para muestras relacionadas si la normalidad es razonable;
- usar Wilcoxon si no se cumple normalidad.

Para exito/fallo:

- usar McNemar si hay emparejamiento suficiente;
- usar Fisher o comparacion de proporciones si el emparejamiento final no es
  suficiente.

## Reporte

Reportar valor p, magnitud del efecto y diferencia practica. Para la tesis, la
interpretacion practica es tan importante como la significancia estadistica.
