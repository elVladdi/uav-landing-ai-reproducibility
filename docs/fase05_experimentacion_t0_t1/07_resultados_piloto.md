# Resultados Piloto - Fase 05

## Estado

Piloto minimo ejecutado y aceptado el 2026-05-05 por el investigador en `.venv`
con AirSimNH y PX4 SITL.

## Tabla de resultados

| Fecha | Escenario | Tratamiento | Run ID | Resultado | Evidencia | Observaciones |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-05 | `P05_PILOT_CENTER_H2_YAW0` | T0 | `phase05_20260505_132244_43a2b196` | Validado | `data/logs/phase05_experiments/raw/phase05_20260505_132244_43a2b196_baseline_descent.csv` | Descenso base centrado. 76 muestras, 75 detecciones aceptadas, `landing_threshold_reached=True`, `landing_success=True`, error final aprox. `0.043 m`. |
| 2026-05-05 | `P05_PILOT_CENTER_H2_YAW0` | T1 | `phase05_20260505_132414_3529bb30` | Validado | `data/logs/phase05_experiments/raw/phase05_20260505_132414_3529bb30_mavlink_visual_servo.csv` | Descenso visual centrado. 85 muestras, 84 detecciones aceptadas, `landing_threshold_reached=True`, `landing_success=True`, error final aprox. `0.017 m`. |
| 2026-05-05 | `P05_PILOT_OFFSET_Y_POS_H2_YAW0` | T0 | `phase05_20260505_132929_eef8d7ba` | Validado como baseline | `data/logs/phase05_experiments/raw/phase05_20260505_132929_eef8d7ba_baseline_descent.csv` | Descenso base con offset lateral. 61 muestras, 39 detecciones aceptadas, `landing_threshold_reached=True`, `landing_success=True`, error final aprox. `0.726 m`. El error alto es coherente con T0 porque no corrige lateralmente. |
| 2026-05-05 | `P05_PILOT_OFFSET_Y_POS_H2_YAW0` | T1 | `phase05_20260505_133149_3b8adca2` | Piloto parcial, supersedido | `data/logs/phase05_experiments/raw/phase05_20260505_133149_3b8adca2_mavlink_visual_servo.csv` | Correccion visual activa positiva: 125/125 detecciones aceptadas, error lateral normalizado bajo de aprox. `0.3750` a `0.0079`, error final aprox. `0.011 m`, sin abortos. No se acepta como aterrizaje formal porque `landing_threshold_reached=False`; el lazo visual termino a aprox. `0.971 m`, por encima del umbral `0.80 m`. Se conserva como incidencia tecnica y no debe usarse como corrida comparativa aceptada. |
| 2026-05-05 | `P05_PILOT_OFFSET_Y_POS_H2_YAW0` | T1 | `phase05_20260505_154421_71272606` | Validado | `data/logs/phase05_experiments/raw/phase05_20260505_154421_71272606_mavlink_visual_servo.csv` | Repeticion con `--duration 40`. 139 muestras visuales, 138 detecciones aceptadas, error lateral normalizado bajo de aprox. `0.4402` a `0.0286`, `landing_threshold_reached=True`, `landing_success=True`, sin abortos, error final aprox. `0.014 m` y cierre en `LOITER`, `armed=False`. |

## Resumen cuantitativo

| Escenario | Tratamiento | Exito formal | Error final aprox. | Tasa deteccion aceptada | Tiempo/ventana visual |
| --- | --- | --- | --- | --- | --- |
| Centrado | T0 | Si | `0.043 m` | `98.7 %` | `18.137 s` |
| Centrado | T1 | Si | `0.017 m` | `98.8 %` | `19.967 s` |
| Offset lateral +0.8 m | T0 | Si, como baseline | `0.726 m` | `63.9 %` | `18.675 s` |
| Offset lateral +0.8 m | T1 | Si, repeticion aceptada | `0.014 m` | `99.3 %` | `30.749 s`, alcanzo `0.7909 m` |

## Lectura metodologica

El piloto confirma que la estructura de Fase 05 funciona: se generan logs
separados para T0/T1, se registran metadatos de escenario, se calculan metricas
por corrida y los cierres terminan con PX4 en `LOITER`, `armed=False`.

La comparacion centrada queda validada. En el escenario con offset lateral, T0
sirve como baseline porque conserva error final alto al no corregir. La
repeticion T1 con mayor duracion demuestra correccion lateral fuerte y estable,
alcanza el umbral formal de aterrizaje y reduce el error final respecto a T0.

## Corrida supersedida

La corrida `phase05_20260505_133149_3b8adca2` se conserva como evidencia
tecnica de correccion visual, pero queda supersedida por
`phase05_20260505_154421_71272606` para el piloto aceptado. En cualquier
analisis comparativo, debe excluirse la corrida parcial para no duplicar el par
`P05_PAIR_PILOT_YPOS_R01`.

## Curacion aplicada

Al regenerar `phase05_run_summary.csv` con `src/analysis/phase05_metrics.py`,
el piloto queda con cuatro corridas `accepted` y una corrida `superseded`:

- `accepted`: T0 centrado, T1 centrado, T0 offset +0.8 m y T1 offset +0.8 m
  repetida con `--duration 40`;
- `superseded`: `phase05_20260505_133149_3b8adca2`, reemplazada por
  `phase05_20260505_154421_71272606`.

## Accion recomendada antes del experimento completo

Antes de habilitar las 160 corridas, revisar si el diseno formal mantendra
`--duration 40` para escenarios con desplazamiento lateral y preparar el orden
operativo de ejecucion por bloques.

## Criterio de aceptacion del piloto

El piloto minimo se acepta si:

- las cuatro corridas generan CSV en `data/logs/phase05_experiments/raw/`;
- el resumen se genera con `src/analysis/phase05_metrics.py`;
- T0 no registra correcciones laterales;
- T1 usa correcciones visuales y mantiene los parametros congelados;
- existe `final_error_m` o queda documentada la causa de no disponibilidad;
- no queda PX4 en modo residual inseguro al finalizar.

Estado actual frente al criterio: aceptado, usando la repeticion
`phase05_20260505_154421_71272606` como T1 valido para el escenario con offset
lateral positivo.
