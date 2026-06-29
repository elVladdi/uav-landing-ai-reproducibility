# Avance de Ejecucion Formal

## Estado al 2026-05-05

Se completo el escenario formal `P05_S01_H2_Y04_YAW0`.

## Estado al 2026-05-06

`P05_S02_H2_Y04_YAW15` queda en ejecucion parcial con R01-R04 completos
despues de aplicar la enmienda metodologica `P05-A01` y repetir formalmente los
T1 afectados por la incidencia de marcador residual.

## Estado al 2026-05-09

`P05_S01_H2_Y04_YAW0` y `P05_S02_H2_Y04_YAW15` estan cerrados. En
`P05_S03_H2_Y08_YAW0` queda cerrado con R01-R10 pareadas formalmente:
T0 `10/10` y T1 `10/10`. Se inicio `P05_S04_H2_Y08_YAW15`; R01-R04 quedan
pareadas formalmente despues de repetir T1 R04 y declarar `Run 67` original
como `superseded`.

## Estado al 2026-06-07

Se completaron los bloques `Run 69` a `Run 76` y `Run 77` a `Run 80` de
`P05_S04_H2_Y08_YAW15`. S04 queda cerrado con R01-R10 pareadas formalmente:
T0 `10/10` y T1 `10/10`. El acumulado formal queda en `80/160` corridas
aceptadas y `40` pares T0/T1 aceptados.

Tambien se inicio `P05_S05_H3_Y04_YAW0` con el bloque `Run 81` a `Run 88`,
se extendio con el bloque `Run 89` a `Run 96` y se cerro con el bloque
`Run 97` a `Run 100`. R01-R10 quedan pareadas formalmente: T0 `10/10` y
T1 `10/10`. El acumulado formal queda en `100/160` corridas aceptadas y
`50` pares T0/T1 aceptados.

## Estado al 2026-06-08

Se inicio `P05_S06_H3_Y04_YAW15` con el bloque `Run 101` a `Run 108`,
se extendio con el bloque `Run 109` a `Run 116` y se cerro con el bloque
`Run 117` a `Run 120`. R01-R10 quedan pareadas formalmente: T0 `10/10` y
T1 `10/10`. El acumulado formal queda en `120/160` corridas aceptadas y
`60` pares T0/T1 aceptados.

Tambien se inicio `P05_S07_H3_Y08_YAW0` con el bloque `Run 121` a
`Run 128` y se extendio con el bloque `Run 129` a `Run 136`. R01-R08 quedan
pareadas formalmente: T0 `8/10` y T1 `8/10`. Durante `Run 136`, dos intentos
duplicados de T0 R08 quedaron `superseded` por el ultimo intento completo.
Luego se cerro S07 con el bloque `Run 137` a `Run 140`. R01-R10 quedan
pareadas formalmente: T0 `10/10` y T1 `10/10`. El acumulado formal queda en
`140/160` corridas aceptadas y `70` pares T0/T1 aceptados.

Tambien se inicio `P05_S08_H3_Y08_YAW15` con el bloque `Run 141` a
`Run 148`. R01-R04 quedan pareadas formalmente: T0 `4/10` y T1 `4/10`.
El acumulado formal queda en `148/160` corridas aceptadas y `74` pares T0/T1
aceptados.

Se extendio `P05_S08_H3_Y08_YAW15` con el bloque `Run 149` a `Run 156`.
R01-R08 quedan pareadas formalmente: T0 `8/10` y T1 `8/10`. El acumulado
formal queda en `156/160` corridas aceptadas y `78` pares T0/T1 aceptados.

Finalmente, se cerro `P05_S08_H3_Y08_YAW15` con el bloque `Run 157` a
`Run 160`. R01-R10 quedan pareadas formalmente: T0 `10/10` y T1 `10/10`.
La ejecucion formal de Fase 05 queda completa con `160/160` corridas formales
aceptadas, `80` pares T0/T1 aceptados y `16/16` celdas escenario/tratamiento
completas.

## Bloque 1

- Rango ejecutado: `Run 1` a `Run 8`.
- Escenario: `P05_S01_H2_Y04_YAW0`.
- Condicion: altura inicial `2.0 m`, offset lateral `0.4 m`, yaw `0.0 deg`.
- Pares completos: `R01`, `R02`, `R03`, `R04`.
- Corridas aceptadas: 8/8.
- Estado PX4 posterior a las corridas: cierre seguro observado en `HOLD` o
  `LOITER`, `armed=False`.
- Marcadores residuales: eliminados con `clear_landing_markers.py`.

## Bloque 2

- Rango ejecutado: `Run 9` a `Run 16`.
- Escenario: `P05_S01_H2_Y04_YAW0`.
- Condicion: altura inicial `2.0 m`, offset lateral `0.4 m`, yaw `0.0 deg`.
- Pares completos: `R05`, `R06`, `R07`, `R08`.
- Corridas aceptadas: 8/8.

## Bloque 3

- Rango ejecutado: `Run 17` a `Run 20`.
- Escenario: `P05_S01_H2_Y04_YAW0`.
- Condicion: altura inicial `2.0 m`, offset lateral `0.4 m`, yaw `0.0 deg`.
- Pares completos: `R09`, `R10`.
- Corridas aceptadas: 4/4.
- Estado de completitud del escenario: T0 `10/10`, T1 `10/10`.
- Escenario S01 cerrado para analisis formal.

## Corridas aceptadas

| Repeticion | T0 run_id | T1 run_id |
|---:|---|---|
| 1 | `phase05_20260505_164143_5ec5680e` | `phase05_20260505_164539_85f27d44` |
| 2 | `phase05_20260505_165111_feb19818` | `phase05_20260505_164848_2e00f2f9` |
| 3 | `phase05_20260505_165322_bd0f0c54` | `phase05_20260505_165530_d9672e22` |
| 4 | `phase05_20260505_170004_fe1e3d39` | `phase05_20260505_165745_2f6b6a6b` |
| 5 | `phase05_20260505_170604_78ce63e2` | `phase05_20260505_170905_3196fab0` |
| 6 | `phase05_20260505_171508_8d09c7cd` | `phase05_20260505_171329_70a51954` |
| 7 | `phase05_20260505_171646_b0d3f4a0` | `phase05_20260505_171818_30801bff` |
| 8 | `phase05_20260505_172209_d6f7df3f` | `phase05_20260505_172001_9faa9dc1` |
| 9 | `phase05_20260505_204624_a0d2f963` | `phase05_20260505_204943_14fa9d91` |
| 10 | `phase05_20260505_205624_6dc3309e` | `phase05_20260505_205420_2950f2f8` |

## Resumen parcial

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Tasa media de deteccion aceptada |
|---|---:|---:|---:|---:|
| T0 | 10 | `0.400 m` | `19.674 s` | `84.2 %` |
| T1 | 10 | `0.021 m` | `26.815 s` | `98.9 %` |

Los valores anteriores provienen de las salidas curadas versionables:

```text
data/logs/phase05_experiments/summary/phase05_run_summary.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_completion_check.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

Los logs crudos y figuras pesadas siguen excluidos. Estas tablas livianas se
versionan porque permiten revisar y reproducir el avance formal sin subir el
volumen completo de datos experimentales.

## Diferencias pareadas parciales

Sobre 10 pares T0/T1 aceptados:

- reduccion media del error final `T0 - T1`: `0.379 m`;
- diferencia media de tiempo `T0 - T1`: `-7.141 s`;
- mejora media de deteccion aceptada `T1 - T0`: `14.7 puntos porcentuales`.

## Lectura metodologica

El escenario S01 confirma que la estructura formal funciona: los tratamientos
quedan pareados por `treatment_pair_id`, la curacion marca las 20 corridas como
`accepted`, y las tablas derivadas se generan sin duplicados. T1 reduce el error
final frente a T0 en las diez repeticiones del escenario S01, aunque requiere
mas tiempo de descenso hasta el umbral.

## Inicio de S02

Se inicio el escenario `P05_S02_H2_Y04_YAW15` despues de validar yaw con
`offboard-yaw-rate`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 21 | T0 | 1 | `phase05_20260505_212244_60e653af` | `accepted` | descenso base completo, `landing_threshold_reached=True`, cierre `LOITER`, `armed=False` |
| 22 | T1 | 1 | `phase05_20260505_212727_5fc9e757` | `excluded` | aborto por perdida de marcador cerca del umbral visual |
| 22R | T1 | 1 | `phase05_20260505_213632_1aeebbe7` | `excluded` | repeticion con el mismo patron de perdida cerca del umbral visual |
| 22F | T1 | 1 | `phase05_20260506_220836_6d1110a0` | `accepted` | corrida formal aceptada con `P05-A01`, cierre `LOITER`, `armed=False` |

La corrida T0 de S02 quedo aceptada con error final `0.392 m`,
`landing_threshold_reached=True`, `landing_success=True` y cierre seguro en
`LOITER`, `armed=False`.

La corrida T1 de S02 corrigio lateralmente de forma efectiva y cerro segura:
error final `0.0146 m`, tasa de deteccion aceptada `96.6 %`, evento terminal
`land_complete`, modo final `LOITER` y `armed=False`. Sin embargo, no se acepta
para comparacion formal porque el lazo visual aborto por
`marker_missing_or_controller_abort`: acumulo `4` perdidas consecutivas con
limite `3`, a una altitud visual minima aprox. de `0.849 m`, sin alcanzar el
umbral formal de `0.80 m`.

La repeticion `phase05_20260505_213632_1aeebbe7` reprodujo el mismo patron:
error final `0.0086 m`, tasa de deteccion aceptada `96.4 %`, cierre
`LOITER`, `armed=False`, pero `aborted=True` por `4` perdidas consecutivas con
limite `3`. En este segundo intento la altitud visual minima fue aprox.
`0.815 m`, apenas por encima del umbral formal `0.80 m`.

La prueba diagnostica no formal `phase05_20260505_215332_c32234b5` uso
`max_missing_detections=6` y resolvio la incidencia sin cambiar el resto de la
condicion experimental: `landing_success=True`,
`landing_threshold_reached=True`, `aborted=False`, `lost_detection_count=1`,
tasa de deteccion aceptada `99.1 %`, altitud visual final `0.7977 m`, error
final `0.0073 m`, cierre `LOITER`, `armed=False`. La corrida quedo
correctamente `excluded` por curacion al usar `scenario_id` terminado en
`_DIAG`.

La repeticion formal posterior `phase05_20260506_220836_6d1110a0` quedo
`accepted`: `landing_success=True`, `landing_threshold_reached=True`,
`aborted=False`, `lost_detection_count=2`, tasa de deteccion aceptada `98.2 %`,
altitud visual final `0.7891 m`, error final `0.0213 m`, cierre `LOITER`,
`armed=False`. Con ello, `P05_S02_H2_Y04_YAW15_R01` queda pareado formalmente:
T0 `phase05_20260505_212244_60e653af` y T1
`phase05_20260506_220836_6d1110a0`.

Para el primer par de S02, la reduccion pareada del error final `T0 - T1` fue
`0.371 m`; el tiempo hasta umbral aumento en T1 por `6.220 s`; y la tasa de
deteccion aceptada mejoro en `35.2` puntos porcentuales frente a T0.

## Bloque parcial S02 R02-R04

Se ejecuto el bloque `Run 23` a `Run 28`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 23 | T1 | 2 | `phase05_20260506_222127_a5df3786` | `accepted` | T1 aceptado, `landing_threshold_reached=True`, cierre `LOITER`, `armed=False` |
| 24 | T0 | 2 | `phase05_20260506_222339_fad7e0f2` | `accepted` | T0 aceptado, par R02 completo |
| 25 | T0 | 3 | `phase05_20260506_222538_f7bff17b` | `accepted` | T0 aceptado, falta repetir T1 R03 |
| 26 | T1 | 3 | `phase05_20260506_222740_a752e2bd` | `excluded` | aborto por perdida de marcador cerca de `0.9351 m` |
| 27 | T1 | 4 | `phase05_20260506_222948_9cf2352f` | `excluded` | aborto temprano; se observaron dos marcadores fiduciarios en escena |
| 28 | T0 | 4 | `phase05_20260506_223142_f52b8e85` | `accepted` | T0 aceptado, falta repetir T1 R04 |
| 26R | T1 | 3 | `phase05_20260506_223941_15b8da6a` | `accepted` | repeticion aceptada tras limpieza preventiva, `lost_detection_count=0` |
| 27R | T1 | 4 | `phase05_20260506_224144_bda896e4` | `accepted` | repeticion aceptada tras limpieza preventiva, `lost_detection_count=1` |

El par R02 quedo completo para comparacion formal en la primera ejecucion del
bloque. Los pares R03 y R04 quedaron inicialmente incompletos porque los T1
asociados a `Run 26` y `Run 27` fueron excluidos. En `Run 27` se observo una
condicion no controlada: dos marcadores fiduciarios simultaneos, probablemente
por marcador residual de una corrida previa. Por criterio metodologico, esas
corridas no se rescatan.

Las repeticiones `26R` y `27R` resolvieron el bloque: R03 y R04 quedan
formalmente pareados. La repeticion R03 tuvo `accepted_detection_rate=100.0 %`,
`lost_detection_count=0`, altitud visual final `0.7991 m`, error final
`0.0209 m` y cierre `LOITER`, `armed=False`. La repeticion R04 tuvo
`accepted_detection_rate=99.1 %`, `lost_detection_count=1`, altitud visual final
`0.7821 m`, error final `0.0151 m` y cierre `LOITER`, `armed=False`.

Con R01-R04 completos, el resumen parcial de S02 queda:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Tasa media de deteccion aceptada |
|---|---:|---:|---:|---:|
| T0 | 4 | `0.403 m` | `18.236 s` | `66.7 %` |
| T1 | 4 | `0.019 m` | `25.938 s` | `98.9 %` |

## Bloque parcial S02 R05-R07

Se ejecuto el bloque `Run 29` a `Run 34`, correspondiente a las repeticiones
R05, R06 y R07 de `P05_S02_H2_Y04_YAW15`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 29 | T0 | 5 | `phase05_20260506_225204_cd5af6c5` | `accepted` | T0 aceptado, error final `0.424 m`, cierre `LOITER`, `armed=False` |
| 30 | T1 | 5 | `phase05_20260506_225359_b159c30b` | `excluded` | aborto por perdida de marcador: `missing_detections=7`, `max_missing_detections=6`, altitud visual minima `0.8638 m` |
| 31 | T1 | 6 | `phase05_20260506_225630_93cc83e3` | `excluded` | aborto por perdida de marcador: `missing_detections=7`, `max_missing_detections=6`, altitud visual minima `0.9136 m` |
| 32 | T0 | 6 | `phase05_20260506_225833_1e65c812` | `accepted` | T0 aceptado, error final `0.476 m`, cierre `LOITER`, `armed=False` |
| 33 | T0 | 7 | `phase05_20260506_230025_ebc765b5` | `accepted` | T0 aceptado, error final `0.482 m`, cierre `LOITER`, `armed=False` |
| 34 | T1 | 7 | `phase05_20260506_230225_10e6ea83` | `excluded` | aborto por perdida de marcador: `missing_detections=7`, `max_missing_detections=6`, altitud visual minima `0.8429 m` |

Las tres corridas T1 redujeron el error lateral antes del aborto
(`reduced_abs_error_x=True`) y cerraron de forma segura en `LOITER`,
`armed=False`, pero no alcanzaron el criterio formal
`landing_threshold_reached=True`. El patron no corresponde a marcador residual:
ocurre al final del descenso visual, cerca del umbral `0.80 m`, con perdida
transitoria recurrente del ArUco bajo `yaw_deg=15.0`.

Estado acumulado de S02 despues de este bloque:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 7 | 10 | 3 |
| T1 | 4 | 10 | 6 |

Los pares comparativos completos de S02 siguen siendo R01-R04. Los T0 de R05,
R06 y R07 se conservan como aceptados, pero los pares quedan incompletos hasta
resolver o repetir formalmente sus T1.

## Diagnostico terminal S02

Se ejecuto la prueba no formal
`phase05_20260506_231219_1598cbf1`, con
`scenario_id=P05_S02_H2_Y04_YAW15_DIAG`, `landing_complete_altitude=0.90` y
`max_missing_detections=10`.

Resultado:

- `landing_success=True`.
- `landing_threshold_reached=True`.
- `aborted=False`.
- `accepted_detection_rate=100.0 %`.
- `lost_detection_count=0`.
- altitud visual final `0.8988 m`.
- error final `0.0110 m`.
- cierre `LOITER`, `armed=False`.

La corrida quedo correctamente excluida por curacion al usar sufijo `_DIAG`.
El resultado indica que una entrega visual mas alta puede evitar la perdida
terminal del marcador. Sin embargo, al revisar los precheck de S02 se detecto
que el yaw real no era absoluto `15 deg`: variaba entre corridas porque el
helper aplicaba `+15 deg` relativo al yaw residual.

## Enmienda P05-A02

Se actualizo el helper de yaw y el generador formal para usar yaw absoluto:

- `run_phase05_yaw_setup.py` acepta `--absolute-yaw-deg`.
- `phase05_generate_run_plan.py` genera `--absolute-yaw-deg` para todos los
  escenarios, incluidos `YAW0`.
- `configs/phase05_experiment_config.json` registra
  `formal_execution.yaw_setup.mode = "absolute"`.

Esta enmienda controla el factor metodologico "orientacion inicial" antes de
continuar con nuevas corridas formales.

## Siguiente accion

No continuar con `Run 35` todavia. Se valido primero el yaw absoluto:

```powershell
python src\perception\clear_landing_markers.py --object-regex ".*phase05.*"
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_phase05_yaw_setup.py --confirm-send --method offboard-yaw-rate --absolute-yaw-deg 15.0 --yaw-speed-deg-s 10.0 --yaw-kp 0.80 --tolerance-deg 3.0 --wait-timeout 25.0
python src\control\run_px4_land.py --confirm-send --timeout 30
python src\control\run_px4_telemetry_check.py --duration 5
```

Resultado de validacion: `Yaw setup accepted`, yaw final aprox. `12.04 deg`,
objetivo `15.00 deg`, error `2.96 deg`, tolerancia `3.0 deg`. La telemetria
posterior al aterrizaje quedo en `HOLD`, baja altitud y `armed=True`; por tanto
antes del siguiente diagnostico se debe desarmar.

El intento de desarme posterior fue denegado por PX4 (`COMMAND_DENIED`) y
AirSimNH reporto `Disarming denied: not landed`; la sesion se descarto y se
reinicio el entorno. La telemetria posterior al reinicio quedo limpia:
`phase04_20260506_233451_19ee46f6_px4_telemetry.csv`, `mode=HOLD`,
`armed=False`, `alt=0.0`.

Despues del reinicio limpio se ejecuto un T1 diagnostico con yaw absoluto y
umbral terminal `0.90 m`:

```powershell
python src\perception\clear_landing_markers.py --object-regex ".*phase05.*"
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_phase05_yaw_setup.py --confirm-send --method offboard-yaw-rate --absolute-yaw-deg 15.0 --yaw-speed-deg-s 10.0 --yaw-kp 0.80 --tolerance-deg 3.0 --wait-timeout 25.0
python src\perception\spawn_fiducial_marker.py --object-name phase05_diag_s02_abs_yaw_terminal_r01_t1 --under-vehicle --offset-x 0.0 --offset-y 0.4 --z 0.0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_phase05_t1_visual_descent.py --confirm-send --duration 40 --detector aruco --save-annotated --max-horizontal-speed 0.10 --max-missing-detections 10 --enable-descent --descent-rate 0.08 --centered-cycles-required 5 --landing-complete-altitude 0.90 --scenario-id P05_S02_H2_Y04_YAW15_ABSYAW_DIAG --marker-object-name phase05_diag_s02_abs_yaw_terminal_r01_t1 --treatment-pair-id P05_S02_H2_Y04_YAW15_ABSYAW_DIAG_R01 --repetition 1 --planned-initial-height-m 2.0 --planned-offset-x-m 0.0 --planned-offset-y-m 0.4 --planned-yaw-deg 15.0
python src\perception\clear_landing_markers.py --object-regex ".*phase05.*"
python src\control\run_px4_telemetry_check.py --duration 5
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```

Resultado del diagnostico con yaw absoluto:

- `phase05_20260506_233844_cc63ed08`
- `scenario_id=P05_S02_H2_Y04_YAW15_ABSYAW_DIAG`
- `curation_status=excluded` por sufijo `_DIAG`
- `landing_success=False`
- `landing_threshold_reached=False`
- `aborted=True`
- `missing_detections=11`, con `max_missing_detections=10`
- `accepted_detection_rate=89.6 %`
- altitud visual final `0.9453 m`
- error final `0.0226 m`
- cierre `LOITER`, `armed=False`

Interpretacion: el control visual redujo el error lateral, pero con yaw absoluto
`15 deg` el marcador se perdio antes de alcanzar el umbral visual `0.90 m`.
Por tanto, no se adopta todavia una enmienda formal para S02 T1 y no se debe
continuar con `Run 35`.

Siguiente accion: ejecutar una segunda prueba diagnostica no formal con yaw
absoluto y `landing_complete_altitude=1.05`. Si esa prueba alcanza el umbral sin
aborto, se documentara una posible enmienda `P05-A03` sobre la altitud de
entrega visual a `LAND`; si falla, se revisara geometria/visibilidad del
marcador antes de reanudar S02 formal.

## Diagnostico H105 S02

Se ejecuto la segunda prueba diagnostica no formal con yaw absoluto:

- `phase05_20260508_230559_a6773794`
- `scenario_id=P05_S02_H2_Y04_YAW15_ABSYAW_H105_DIAG`
- `curation_status=excluded` por sufijo `_DIAG`
- `landing_complete_altitude=1.05`
- `max_missing_detections=10`
- `landing_success=True`
- `landing_threshold_reached=True`
- `aborted=False`
- `accepted_detection_rate=100.0 %`
- `lost_detection_count=0`
- altitud visual final `1.0408 m`
- error final `0.0218 m`
- latencia media `80.68 ms`, maxima `148.81 ms`
- cierre `LOITER`, `armed=False`

Interpretacion: con yaw absoluto `15 deg`, la entrega visual a `LAND` en
`1.05 m` evita la perdida terminal del marcador y mantiene error lateral bajo.
La corrida queda excluida de las metricas formales por ser diagnostica, pero
sustenta la enmienda `P05-A03`.

## Enmienda P05-A03

Se adopta la enmienda metodologica `P05-A03`:

- campo: `frozen_t1.landing_complete_altitude_m`
- valor anterior: `0.80`
- valor nuevo: `1.05`
- alcance: umbral terminal de comandos formales desde la reanudacion posterior
  al diagnostico H105.

Los T1 formales excluidos en R05-R07 no se convierten en aceptados. Para
comparabilidad estricta, cualquier correccion de R05-R07 bajo `P05-A03` debe
repetir el par completo o declarar explicitamente la mezcla de umbrales. El
siguiente paso operativo es usar comandos formales regenerados con
`landing_complete_altitude=1.05` y no ejecutar bloques antiguos generados con
`0.80`.

## Bloque correctivo S02 R05-R07

Se ejecutaron pares correctivos completos de `P05_S02_H2_Y04_YAW15` para R05,
R06 y R07 bajo la configuracion `P05-A03` (`landing_complete_altitude=1.05`).

| Run original | Tratamiento | Repeticion | Corrida antigua | Curacion antigua | Corrida correctiva | Curacion nueva | Resultado |
|---:|---|---:|---|---|---|---|---|
| 29 | T0 | 5 | `phase05_20260506_225204_cd5af6c5` | `superseded` | `phase05_20260508_232252_383f3956` | `accepted` | error final `0.3193 m`, cierre `LOITER`, `armed=False` |
| 30 | T1 | 5 | `phase05_20260506_225359_b159c30b` | `superseded` | `phase05_20260508_232456_adf8e39a` | `accepted` | error final `0.0220 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 31 | T1 | 6 | `phase05_20260506_225630_93cc83e3` | `superseded` | `phase05_20260508_232703_429b8f5b` | `accepted` | error final `0.0071 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 32 | T0 | 6 | `phase05_20260506_225833_1e65c812` | `superseded` | `phase05_20260508_232901_d1c52dd5` | `accepted` | error final `0.3970 m`, cierre `LOITER`, `armed=False` |
| 33 | T0 | 7 | `phase05_20260506_230025_ebc765b5` | `superseded` | `phase05_20260508_233055_78205df8` | `accepted` | error final `0.4078 m`, cierre `LOITER`, `armed=False` |
| 34 | T1 | 7 | `phase05_20260506_230225_10e6ea83` | `superseded` | `phase05_20260508_233244_dd7fa514` | `accepted` | error final `0.0075 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |

Los seis intentos antiguos R05-R07 se declararon en
`curation.superseded_runs`. Tras regenerar metricas y reporte:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 7 | 10 | 3 |
| T1 | 7 | 10 | 3 |

S02 queda pareado formalmente hasta R07. Para `P05_S02_H2_Y04_YAW15`, el
resumen parcial curado con `n=7` por tratamiento es:

| Tratamiento | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|
| T0 | `0.3910 m` | `16.251 s` | `68.0 %` |
| T1 | `0.0160 m` | `22.694 s` | `99.4 %` |

Los siete pares aceptados de S02 mantienen una reduccion pareada positiva del
error final en T1. El promedio `T0 - T1` para error final es aproximadamente
`0.375 m`.

## Cierre S02 R08-R10

Se ejecutaron las repeticiones restantes R08-R10 de
`P05_S02_H2_Y04_YAW15` bajo `P05-A03`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 35 | T1 | 8 | `phase05_20260508_234338_2a120ef2` | `accepted` | error final `0.0269 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 36 | T0 | 8 | `phase05_20260508_234529_e128c503` | `accepted` | error final `0.4009 m`, cierre `LOITER`, `armed=False` |
| 37 | T0 | 9 | `phase05_20260508_234728_fe8b975a` | `accepted` | error final `0.3484 m`, cierre `LOITER`, `armed=False` |
| 38 | T1 | 9 | `phase05_20260508_235107_065ebbfe` | `accepted` | error final `0.0218 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 39 | T1 | 10 | `phase05_20260508_235301_34c84471` | `accepted` | error final `0.0107 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 40 | T0 | 10 | `phase05_20260508_235528_1fd2fb58` | `accepted` | error final `0.3140 m`, cierre `LOITER`, `armed=False` |

Durante el primer intento de `Run 38`, AirSimNH se cerro. El entorno fue
reiniciado y `Run 38` se repitio; el intento interrumpido no genero una fila
formal en `phase05_run_summary.csv`. La repeticion valida quedo aceptada como
`phase05_20260508_235107_065ebbfe`.

## Cierre S02

El escenario `P05_S02_H2_Y04_YAW15` queda completo:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

Resumen curado del escenario:

| Tratamiento | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media | Exito |
|---|---:|---:|---:|---:|
| T0 | `0.3800 m` | `15.173 s` | `70.9 %` | `100 %` |
| T1 | `0.0172 m` | `22.180 s` | `99.6 %` | `100 %` |

Los diez pares aceptados de S02 muestran reduccion positiva del error final en
T1. El promedio pareado `T0 - T1` para error final es `0.3629 m`; la diferencia
media de tiempo `T0 - T1` es `-7.007 s`; y la mejora media de deteccion aceptada
`T1 - T0` es `28.7` puntos porcentuales.

Estado acumulado del experimento:

- corridas formales aceptadas: `40`;
- pares T0/T1 aceptados: `20`;
- escenarios completos: `P05_S01_H2_Y04_YAW0` y `P05_S02_H2_Y04_YAW15`;
- celdas escenario/tratamiento completas: `4/16`.

## Bloque parcial S03 R01-R04

Se inicio `P05_S03_H2_Y08_YAW0`, primer escenario con desplazamiento lateral
`offset_y=0.8 m` y yaw absoluto `0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 41 | T0 | 1 | `phase05_20260509_000310_08ba7fc5` | `accepted` | error final `0.8579 m`, cierre `LOITER`, `armed=False` |
| 42 | T1 | 1 | `phase05_20260509_000451_0b969adf` | `accepted` | error final `0.0377 m`, deteccion `100.0 %`, cierre `LOITER`, `armed=False` |
| 43 | T1 | 2 | `phase05_20260509_000701_eb58d52f` | `accepted` | error final `0.0119 m`, deteccion `100.0 %`, cierre `LOITER`, `armed=False` |
| 44 | T0 | 2 | `phase05_20260509_000902_46f50524` | `accepted` | error final `0.7584 m`, cierre `LOITER`, `armed=False` |
| 45 | T0 | 3 | `phase05_20260509_001055_cdf6de44` | `accepted` | error final `0.7441 m`, cierre `LOITER`, `armed=False` |
| 46 | T1 | 3 | `phase05_20260509_001242_70bda245` | `superseded` | aborto temprano por perdida de marcador; reemplazado por repeticion correctiva |
| 46R | T1 | 3 | `phase05_20260509_003307_468906cb` | `accepted` | repeticion aceptada, error final `0.0091 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 47 | T1 | 4 | `phase05_20260509_001502_30366ed5` | `superseded` | primer intento interrumpido por cierre de AirSimNH, sin `land_complete` |
| 47R | T1 | 4 | `phase05_20260509_001816_20a45b99` | `accepted` | repeticion aceptada, error final `0.0221 m`, deteccion `100.0 %`, cierre `LOITER`, `armed=False` |
| 48 | T0 | 4 | `phase05_20260509_002035_66a0dbb4` | `accepted` | error final `0.7656 m`, cierre `LOITER`, `armed=False` |

Estado posterior del bloque:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 4 | 10 | 6 |
| T1 | 4 | 10 | 6 |

Pares completos actuales de S03: R01, R02, R03 y R04. El primer intento T1 de
R03 queda conservado como incidencia `superseded`, pero no alimenta las metricas
comparativas.

En los pares completos, T1 mantiene reduccion fuerte del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.8201 m` | `-9.167 s` |
| R02 | `0.7465 m` | `-10.248 s` |
| R03 | `0.7350 m` | `-14.064 s` |
| R04 | `0.7435 m` | `-9.746 s` |

Resumen parcial curado de S03 con R01-R04:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 4 | `0.7815 m` | `13.451 s` | `35.4 %` |
| T1 | 4 | `0.0202 m` | `24.257 s` | `100.0 %` |

## Avance adicional S03 R05-R06

Despues de corregir R03, se ejecutaron `Run 49` a `Run 52`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 49 | T0 | 5 | `phase05_20260509_004101_41d9cbae` | `accepted` | error final `0.8051 m`, cierre `LOITER`, `armed=False` |
| 50 | T1 | 5 | `phase05_20260509_004244_9f022853` | `accepted` | error final `0.0364 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 51 | T1 | 6 | `phase05_20260509_004447_9d806e29` | `accepted` | error final `0.0231 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 52 | T0 | 6 | `phase05_20260509_004647_e3423cd3` | `accepted` | error final `0.7602 m`, cierre `LOITER`, `armed=False` |

Estado acumulado de S03:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 6 | 10 | 4 |
| T1 | 6 | 10 | 4 |

R01-R06 quedan pareados formalmente.

Los pares R05 y R06 mantienen reduccion positiva del error final:

- R05: `T0 - T1 = 0.7688 m`, diferencia de tiempo `T0 - T1 = -8.908 s`;
- R06: `T0 - T1 = 0.7372 m`, diferencia de tiempo `T0 - T1 = -11.075 s`.

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `52`;
- pares T0/T1 aceptados: `26`;
- escenarios completos: `P05_S01_H2_Y04_YAW0` y `P05_S02_H2_Y04_YAW15`;
- celdas escenario/tratamiento completas: `4/16`.

## Avance adicional S03 R07-R08

Se ejecutaron `Run 53` a `Run 56`, correspondientes a R07-R08 de
`P05_S03_H2_Y08_YAW0`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 53 | T0 | 7 | `phase05_20260509_005615_8743cfbe` | `accepted` | error final `0.8274 m`, cierre `LOITER`, `armed=False` |
| 54 | T1 | 7 | `phase05_20260509_005801_2841af18` | `accepted` | error final `0.0018 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 55 | T1 | 8 | `phase05_20260509_010004_a268301d` | `accepted` | error final `0.0126 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 56 | T0 | 8 | `phase05_20260509_010204_ea0ffbac` | `accepted` | error final `0.7735 m`, cierre `LOITER`, `armed=False` |

Estado acumulado de S03:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 8 | 10 | 2 |
| T1 | 8 | 10 | 2 |

R01-R08 quedan pareados formalmente. En este bloque, T1 mantiene reduccion
positiva del error final:

- R07: `T0 - T1 = 0.8256 m`, diferencia de tiempo `T0 - T1 = -9.063 s`;
- R08: `T0 - T1 = 0.7609 m`, diferencia de tiempo `T0 - T1 = -9.500 s`.

Resumen parcial curado de S03 con R01-R08:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 8 | `0.7865 m` | `13.470 s` | `37.0 %` |
| T1 | 8 | `0.0193 m` | `23.692 s` | `100.0 %` |

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `56`;
- pares T0/T1 aceptados: `28`;
- escenarios completos: `P05_S01_H2_Y04_YAW0` y `P05_S02_H2_Y04_YAW15`;
- celdas escenario/tratamiento completas: `4/16`.

## Cierre S03 R09-R10

Se ejecutaron `Run 57` a `Run 60`, correspondientes a R09-R10 de
`P05_S03_H2_Y08_YAW0`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 57 | T0 | 9 | `phase05_20260509_011118_927e3e09` | `accepted` | error final `0.7471 m`, cierre `LOITER`, `armed=False` |
| 58 | T1 | 9 | `phase05_20260509_011302_debefdda` | `accepted` | error final `0.0283 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 59 | T1 | 10 | `phase05_20260509_011530_f3221898` | `accepted` | error final `0.0198 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 60 | T0 | 10 | `phase05_20260509_011732_05fe4345` | `accepted` | error final `0.8159 m`, cierre `LOITER`, `armed=False` |

Estado de cierre de S03:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

R01-R10 quedan pareados formalmente. En el cierre, T1 mantiene reduccion
positiva del error final:

- R09: `T0 - T1 = 0.7188 m`, diferencia de tiempo `T0 - T1 = -11.280 s`;
- R10: `T0 - T1 = 0.7961 m`, diferencia de tiempo `T0 - T1 = -11.459 s`.

Resumen curado de S03:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 10 | `0.7850 m` | `13.401 s` | `38.4 %` |
| T1 | 10 | `0.0198 m` | `23.852 s` | `100.0 %` |

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `60`;
- pares T0/T1 aceptados: `30`;
- escenarios completos: `P05_S01_H2_Y04_YAW0`,
  `P05_S02_H2_Y04_YAW15` y `P05_S03_H2_Y08_YAW0`;
- celdas escenario/tratamiento completas: `6/16`.

## Inicio S04 R01-R04

Se inicio `P05_S04_H2_Y08_YAW15`, con altura inicial `2.0 m`, offset lateral
`0.8 m` y yaw absoluto `15.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 61 | T0 | 1 | `phase05_20260509_211541_7721a9cb` | `accepted` | error final `0.7945 m`, cierre `LOITER`, `armed=False` |
| 62 | T1 | 1 | `phase05_20260509_211844_6ec091cb` | `accepted` | error final `0.0236 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 63 | T1 | 2 | `phase05_20260509_212043_98eea009` | `accepted` | error final `0.0248 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 64 | T0 | 2 | `phase05_20260509_212246_507d9664` | `accepted` | error final `0.7275 m`, cierre `LOITER`, `armed=False` |
| 65 | T0 | 3 | `phase05_20260509_212437_424a9706` | `accepted` | error final `0.7473 m`, cierre `LOITER`, `armed=False` |
| 66 | T1 | 3 | `phase05_20260509_212628_e65318a0` | `accepted` | error final `0.0382 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 67 | T1 | 4 | `phase05_20260509_212824_d3037b9b` | `superseded` | aborto temprano por perdida de marcador; reemplazado por repeticion correctiva |
| 67R | T1 | 4 | `phase05_20260509_214330_4ae8d025` | `accepted` | repeticion aceptada, error final `0.0349 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 68 | T0 | 4 | `phase05_20260509_213059_1d49740f` | `accepted` | error final `0.8102 m`, cierre `LOITER`, `armed=False` |

Durante la repeticion correctiva de `Run 67`, AirSimNH se cerro dos veces de
forma intempestiva. Esos intentos no generaron filas formales adicionales en
`phase05_run_summary.csv`; tras reiniciar el entorno, la repeticion valida fue
la corrida `phase05_20260509_214330_4ae8d025`.

Estado acumulado de S04:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 4 | 10 | 6 |
| T1 | 4 | 10 | 6 |

Pares completos actuales de S04: R01, R02, R03 y R04.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7709 m` | `-9.091 s` |
| R02 | `0.7027 m` | `-11.112 s` |
| R03 | `0.7091 m` | `-7.926 s` |
| R04 | `0.7753 m` | `-9.745 s` |

Resumen parcial curado de S04:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 4 | `0.7699 m` | `13.779 s` | `48.3 %` |
| T1 | 4 | `0.0304 m` | `23.247 s` | `100.0 %` |

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `68`;
- pares T0/T1 aceptados: `34`;
- escenarios completos: `P05_S01_H2_Y04_YAW0`,
  `P05_S02_H2_Y04_YAW15` y `P05_S03_H2_Y08_YAW0`;
- celdas escenario/tratamiento completas: `6/16`.

## Avance S04 R05-R08

Se ejecuto el bloque `Run 69` a `Run 76`, correspondiente a R05-R08 de
`P05_S04_H2_Y08_YAW15`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 69 | T0 | 5 | `phase05_20260607_201947_00bacbf8` | `accepted` | error final `0.8420 m`, cierre `LOITER`, `armed=False` |
| 70 | T1 | 5 | `phase05_20260607_202259_ee7d9535` | `accepted` | error final `0.0310 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 71 | T1 | 6 | `phase05_20260607_202528_4e226b05` | `accepted` | error final `0.0155 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 72 | T0 | 6 | `phase05_20260607_202802_f1ccaa50` | `accepted` | error final `0.7150 m`, cierre `LOITER`, `armed=False` |
| 73 | T0 | 7 | `phase05_20260607_203018_78b4b93d` | `accepted` | error final `0.7537 m`, cierre `LOITER`, `armed=False` |
| 74 | T1 | 7 | `phase05_20260607_203218_26efe62a` | `accepted` | error final `0.0145 m`, deteccion `97.9 %`, perdidas `2`, cierre `LOITER`, `armed=False` |
| 75 | T1 | 8 | `phase05_20260607_203502_6e0b3de1` | `accepted` | error final `0.0410 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 76 | T0 | 8 | `phase05_20260607_204013_33ccace8` | `accepted` | error final `0.7236 m`, cierre `LOITER`, `armed=False` |

Los ocho CSV crudos asociados existen en
`data/logs/phase05_experiments/raw/`, tienen tamano no nulo y fueron incluidos
en `phase05_run_summary.csv` con `curation_status=accepted`.

Estado acumulado de S04:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 8 | 10 | 2 |
| T1 | 8 | 10 | 2 |

Pares completos actuales de S04: R01, R02, R03, R04, R05, R06, R07 y R08.

En el bloque R05-R08, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R05 | `0.8109 m` | `-10.228 s` |
| R06 | `0.6995 m` | `-8.560 s` |
| R07 | `0.7391 m` | `-8.569 s` |
| R08 | `0.6826 m` | `-7.362 s` |

Resumen parcial curado de S04 con R01-R08:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 8 | `0.7642 m` | `13.824 s` | `42.5 %` |
| T1 | 8 | `0.0280 m` | `22.898 s` | `99.7 %` |

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `76`;
- pares T0/T1 aceptados: `38`;
- escenarios completos: `P05_S01_H2_Y04_YAW0`,
  `P05_S02_H2_Y04_YAW15` y `P05_S03_H2_Y08_YAW0`;
- celdas escenario/tratamiento completas: `6/16`.

## Cierre S04 R09-R10

Se ejecuto el bloque `Run 77` a `Run 80`, correspondiente a R09-R10 de
`P05_S04_H2_Y08_YAW15`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 77 | T0 | 9 | `phase05_20260607_210540_4e06679b` | `accepted` | error final `0.8312 m`, cierre `LOITER`, `armed=False` |
| 78 | T1 | 9 | `phase05_20260607_210813_021d52e2` | `accepted` | error final `0.0134 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 79 | T1 | 10 | `phase05_20260607_211217_143c9f08` | `accepted` | error final `0.0282 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 80 | T0 | 10 | `phase05_20260607_211514_29807371` | `accepted` | error final `0.6969 m`, cierre `LOITER`, `armed=False` |

Los cuatro CSV crudos asociados existen en
`data/logs/phase05_experiments/raw/`, tienen tamano no nulo y fueron incluidos
en `phase05_run_summary.csv` con `curation_status=accepted`.

Estado de cierre de S04:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

R01-R10 quedan pareados formalmente. En el cierre, T1 mantiene reduccion
positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R09 | `0.8178 m` | `-9.094 s` |
| R10 | `0.6687 m` | `-10.131 s` |

Resumen curado de S04:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media | Exito |
|---|---:|---:|---:|---:|---:|
| T0 | 10 | `0.7642 m` | `13.881 s` | `39.5 %` | `100 %` |
| T1 | 10 | `0.0265 m` | `23.063 s` | `99.8 %` | `100 %` |

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `80`;
- pares T0/T1 aceptados: `40`;
- escenarios completos: `P05_S01_H2_Y04_YAW0`,
  `P05_S02_H2_Y04_YAW15`, `P05_S03_H2_Y08_YAW0` y
  `P05_S04_H2_Y08_YAW15`;
- celdas escenario/tratamiento completas: `8/16`.

## Inicio S05 R01-R04

Se inicio `P05_S05_H3_Y04_YAW0`, con altura inicial `3.0 m`, offset lateral
`0.4 m` y yaw absoluto `0.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 81 | T0 | 1 | `phase05_20260607_213303_9c51c735` | `accepted` | error final `0.3610 m`, cierre `LOITER`, `armed=False` |
| 82 | T1 | 1 | `phase05_20260607_213623_1b8534dd` | `accepted` | error final `0.0319 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 83 | T1 | 2 | `phase05_20260607_213902_7caf345d` | `accepted` | error final `0.0113 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 84 | T0 | 2 | `phase05_20260607_214148_83b1349c` | `accepted` | error final `0.3332 m`, cierre `LOITER`, `armed=False` |
| 85 | T0 | 3 | `phase05_20260607_214425_58aa6793` | `accepted` | error final `0.3694 m`, cierre `LOITER`, `armed=False` |
| 86 | T1 | 3 | `phase05_20260607_214643_a41bad91` | `accepted` | error final `0.0350 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 87 | T1 | 4 | `phase05_20260607_214908_0cfa1281` | `accepted` | error final `0.0473 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 88 | T0 | 4 | `phase05_20260607_215108_40cc496d` | `accepted` | error final `0.3120 m`, cierre `LOITER`, `armed=False` |

Se audito especificamente `Run 81` por duda operacional sobre si se ejecutaron
todos los comandos. La corrida formal queda aceptada porque el log crudo
`phase05_20260607_213303_9c51c735_baseline_descent.csv` contiene precheck,
entrada a `OFFBOARD`, descenso, entrega a `LAND` y evento `land_complete`. La
telemetria posterior `phase04_20260607_213342_d2beae6c_px4_telemetry.csv`
registra `mode=HOLD`, `armed=False` y health local correcto. Por tanto, no se
requiere repeticion ni enmienda de curacion.

## Avance S05 R05-R08

Se ejecuto el segundo bloque parcial de `P05_S05_H3_Y04_YAW0`, correspondiente
a R05-R08 con altura inicial `3.0 m`, offset lateral `0.4 m` y yaw absoluto
`0.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 89 | T0 | 5 | `phase05_20260607_221808_a9cca7d9` | `accepted` | error final `0.3257 m`, cierre `LOITER`, `armed=False` |
| 90 | T1 | 5 | `phase05_20260607_222051_9a36760b` | `accepted` | error final `0.0072 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 91 | T1 | 6 | `phase05_20260607_222951_4917c63d` | `accepted` | error final `0.0111 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 92 | T0 | 6 | `phase05_20260607_223443_4e22bf09` | `accepted` | error final `0.3294 m`, cierre `LOITER`, `armed=False` |
| 93 | T0 | 7 | `phase05_20260607_223645_2c1bd3fd` | `accepted` | error final `0.3119 m`, cierre `LOITER`, `armed=False` |
| 94 | T1 | 7 | `phase05_20260607_224019_fb919ed7` | `accepted` | error final `0.0047 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 95 | T1 | 8 | `phase05_20260607_224226_6ceb231e` | `accepted` | error final `0.0134 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 96 | T0 | 8 | `phase05_20260607_224448_37f56610` | `accepted` | error final `0.3528 m`, cierre `LOITER`, `armed=False` |

Se verifico que los ocho CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 117 y 161
lineas por archivo.

## Cierre S05 R09-R10

Se ejecuto el bloque final de `P05_S05_H3_Y04_YAW0`, correspondiente a R09-R10
con altura inicial `3.0 m`, offset lateral `0.4 m` y yaw absoluto `0.0 deg`.
Con este bloque, S05 queda cerrado formalmente.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 97 | T0 | 9 | `phase05_20260607_230102_0bf4d95d` | `accepted` | error final `0.3705 m`, cierre `LOITER`, `armed=False` |
| 98 | T1 | 9 | `phase05_20260607_230316_de152728` | `accepted` | error final `0.0348 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 99 | T1 | 10 | `phase05_20260607_230522_8db17bb0` | `accepted` | error final `0.0183 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 100 | T0 | 10 | `phase05_20260607_230808_fc5c095d` | `accepted` | error final `0.3698 m`, cierre `LOITER`, `armed=False` |

Se verifico que los cuatro CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 121 y 148
lineas por archivo.

Estado acumulado de S05:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

Pares completos actuales de S05: R01, R02, R03, R04, R05, R06, R07, R08,
R09 y R10.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.3291 m` | `-7.310 s` |
| R02 | `0.3218 m` | `-6.290 s` |
| R03 | `0.3344 m` | `-3.795 s` |
| R04 | `0.2647 m` | `-4.550 s` |
| R05 | `0.3184 m` | `-2.825 s` |
| R06 | `0.3183 m` | `-4.794 s` |
| R07 | `0.3072 m` | `-7.655 s` |
| R08 | `0.3394 m` | `-6.162 s` |
| R09 | `0.3357 m` | `0.839 s` |
| R10 | `0.3515 m` | `-4.760 s` |

Resumen curado final de S05 con R01-R10:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 10 | `0.3436 m` | `25.657 s` | `88.6 %` |
| T1 | 10 | `0.0215 m` | `30.388 s` | `100.0 %` |

## Inicio S06 R01-R04

Se inicio `P05_S06_H3_Y04_YAW15`, con altura inicial `3.0 m`, offset lateral
`0.4 m` y yaw absoluto `15.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 101 | T0 | 1 | `phase05_20260607_233910_4a8cd7ec` | `accepted` | error final `0.8463 m`, cierre `LOITER`, `armed=False` |
| 102 | T1 | 1 | `phase05_20260607_234238_327228c7` | `accepted` | error final `0.0157 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 103 | T1 | 2 | `phase05_20260607_234624_88a84c56` | `accepted` | error final `0.0217 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 104 | T0 | 2 | `phase05_20260607_234943_48e4e226` | `accepted` | error final `0.5858 m`, cierre `LOITER`, `armed=False` |
| 105 | T0 | 3 | `phase05_20260607_235325_8c8bb524` | `accepted` | error final `0.5070 m`, cierre `LOITER`, `armed=False` |
| 106 | T1 | 3 | `phase05_20260607_235731_308afe85` | `accepted` | error final `0.0269 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 107 | T1 | 4 | `phase05_20260608_000028_039492bd` | `accepted` | error final `0.0110 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 108 | T0 | 4 | `phase05_20260608_000247_7a6e3332` | `accepted` | error final `0.4163 m`, cierre `LOITER`, `armed=False` |

Se verifico que los ocho CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 121 y 181
lineas por archivo.

## Avance S06 R05-R08

Se ejecuto el segundo bloque parcial de `P05_S06_H3_Y04_YAW15`,
correspondiente a R05-R08 con altura inicial `3.0 m`, offset lateral `0.4 m`
y yaw absoluto `15.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 109 | T0 | 5 | `phase05_20260608_001718_3e8d2fb1` | `accepted` | error final `0.3355 m`, cierre `LOITER`, `armed=False` |
| 110 | T1 | 5 | `phase05_20260608_003026_6c0a185e` | `accepted` | error final `0.0165 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 111 | T1 | 6 | `phase05_20260608_003245_b76351c8` | `accepted` | error final `0.0323 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 112 | T0 | 6 | `phase05_20260608_003506_3a955a59` | `accepted` | error final `0.3932 m`, cierre `LOITER`, `armed=False` |
| 113 | T0 | 7 | `phase05_20260608_003721_0a408242` | `accepted` | error final `0.4179 m`, cierre `LOITER`, `armed=False` |
| 114 | T1 | 7 | `phase05_20260608_003953_87d08eed` | `accepted` | error final `0.0097 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 115 | T1 | 8 | `phase05_20260608_004215_1ebfe23d` | `accepted` | error final `0.0174 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 116 | T0 | 8 | `phase05_20260608_004430_67507501` | `accepted` | error final `0.3654 m`, cierre `LOITER`, `armed=False` |

Se verifico que los ocho CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 118 y 181
lineas por archivo.

## Cierre S06 R09-R10

Se ejecuto el bloque final de `P05_S06_H3_Y04_YAW15`, correspondiente a
R09-R10 con altura inicial `3.0 m`, offset lateral `0.4 m` y yaw absoluto
`15.0 deg`. Con este bloque, S06 queda cerrado formalmente.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 117 | T0 | 9 | `phase05_20260608_005400_ece937e5` | `accepted` | error final `0.4735 m`, cierre `LOITER`, `armed=False` |
| 118 | T1 | 9 | `phase05_20260608_005635_b3de11f3` | `accepted` | error final `0.0033 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 119 | T1 | 10 | `phase05_20260608_005858_727a0c85` | `accepted` | error final `0.0108 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 120 | T0 | 10 | `phase05_20260608_010121_9015143d` | `accepted` | error final `0.4156 m`, cierre `LOITER`, `armed=False` |

Se verifico que los cuatro CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 118 y 156
lineas por archivo.

Estado acumulado de S06:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

Pares completos actuales de S06: R01, R02, R03, R04, R05, R06, R07, R08,
R09 y R10.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.8306 m` | `-7.165 s` |
| R02 | `0.5641 m` | `-9.314 s` |
| R03 | `0.4801 m` | `-8.026 s` |
| R04 | `0.4053 m` | `-8.887 s` |
| R05 | `0.3190 m` | `-6.852 s` |
| R06 | `0.3610 m` | `-7.509 s` |
| R07 | `0.4081 m` | `-7.030 s` |
| R08 | `0.3481 m` | `-7.929 s` |
| R09 | `0.4702 m` | `-2.189 s` |
| R10 | `0.4048 m` | `-7.457 s` |

Resumen curado final de S06 con R01-R10:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 10 | `0.4756 m` | `25.639 s` | `88.4 %` |
| T1 | 10 | `0.0165 m` | `32.875 s` | `100.0 %` |

## Inicio S07 R01-R04

Se inicio `P05_S07_H3_Y08_YAW0`, con altura inicial `3.0 m`, offset lateral
`0.8 m` y yaw absoluto `0.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 121 | T0 | 1 | `phase05_20260608_104943_84c26529` | `accepted` | error final `0.8074 m`, cierre `LOITER`, `armed=False` |
| 122 | T1 | 1 | `phase05_20260608_105157_18017f67` | `accepted` | error final `0.0129 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 123 | T1 | 2 | `phase05_20260608_105539_0b6fcf44` | `accepted` | error final `0.0224 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 124 | T0 | 2 | `phase05_20260608_105821_fd28825e` | `accepted` | error final `0.7555 m`, cierre `LOITER`, `armed=False` |
| 125 | T0 | 3 | `phase05_20260608_110142_915fc1ee` | `accepted` | error final `0.7279 m`, cierre `LOITER`, `armed=False` |
| 126 | T1 | 3 | `phase05_20260608_110423_5cc26639` | `accepted` | error final `0.0389 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 127 | T1 | 4 | `phase05_20260608_112944_5eb17392` | `accepted` | error final `0.0193 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 128 | T0 | 4 | `phase05_20260608_113207_9cd80600` | `accepted` | error final `0.7789 m`, cierre `LOITER`, `armed=False` |

Se verifico que los ocho CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 115 y 191
lineas por archivo.

Estado acumulado de S07:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 4 | 10 | 6 |
| T1 | 4 | 10 | 6 |

Pares completos actuales de S07: R01, R02, R03 y R04.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7945 m` | `-9.515 s` |
| R02 | `0.7331 m` | `-12.984 s` |
| R03 | `0.6891 m` | `-9.537 s` |
| R04 | `0.7596 m` | `-11.536 s` |

Resumen parcial curado de S07 con R01-R04:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 4 | `0.7674 m` | `26.888 s` | `73.4 %` |
| T1 | 4 | `0.0234 m` | `37.781 s` | `100.0 %` |

## Avance S07 R05-R08

Se ejecuto el segundo bloque parcial de `P05_S07_H3_Y08_YAW0`,
correspondiente a R05-R08 con altura inicial `3.0 m`, offset lateral `0.8 m`
y yaw absoluto `0.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 129 | T0 | 5 | `phase05_20260608_115833_ac615232` | `accepted` | error final `0.6753 m`, cierre `LOITER`, `armed=False` |
| 130 | T1 | 5 | `phase05_20260608_120108_01bf9b72` | `accepted` | error final `0.0185 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 131 | T1 | 6 | `phase05_20260608_120325_a9584a19` | `accepted` | error final `0.0255 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 132 | T0 | 6 | `phase05_20260608_120603_2c9dc18c` | `accepted` | error final `0.6918 m`, cierre `LOITER`, `armed=False` |
| 133 | T0 | 7 | `phase05_20260608_120821_9e5b2b7c` | `accepted` | error final `0.7616 m`, cierre `LOITER`, `armed=False` |
| 134 | T1 | 7 | `phase05_20260608_121033_33399d34` | `accepted` | error final `0.0122 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 135 | T1 | 8 | `phase05_20260608_121322_9d00fb97` | `accepted` | error final `0.0315 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 136 | T0 | 8 | `phase05_20260608_122434_ac873b0b` | `accepted` | error final `0.7926 m`, cierre `LOITER`, `armed=False` |

Durante `Run 136` se generaron tres CSV completos para la misma clave formal
T0 R08. Para evitar duplicacion artificial en el analisis, se conserva como
aceptado el ultimo intento completo y los dos intentos previos quedan
declarados como `superseded` en `curation.superseded_runs`.

| Run logico | Tratamiento | Repeticion | run_id | Curacion | superseded_by |
|---:|---|---:|---|---|---|
| 136 | T0 | 8 | `phase05_20260608_121619_f18597c3` | `superseded` | `phase05_20260608_122434_ac873b0b` |
| 136 | T0 | 8 | `phase05_20260608_121826_222fe0bc` | `superseded` | `phase05_20260608_122434_ac873b0b` |

Se verifico que los diez CSV crudos generados durante el bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 117 y 178
lineas por archivo. No se eliminaron logs crudos.

Estado acumulado de S07:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 8 | 10 | 2 |
| T1 | 8 | 10 | 2 |

Pares completos actuales de S07: R01, R02, R03, R04, R05, R06, R07 y R08.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7945 m` | `-9.515 s` |
| R02 | `0.7331 m` | `-12.984 s` |
| R03 | `0.6891 m` | `-9.537 s` |
| R04 | `0.7596 m` | `-11.536 s` |
| R05 | `0.6569 m` | `-5.971 s` |
| R06 | `0.6663 m` | `-10.433 s` |
| R07 | `0.7494 m` | `-9.591 s` |
| R08 | `0.7611 m` | `-5.316 s` |

Resumen parcial curado de S07 con R01-R08:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 8 | `0.7489 m` | `26.456 s` | `72.8 %` |
| T1 | 8 | `0.0227 m` | `35.817 s` | `100.0 %` |

## Cierre S07 R09-R10

Se ejecuto el bloque de cierre de `P05_S07_H3_Y08_YAW0`, correspondiente a
R09-R10 con altura inicial `3.0 m`, offset lateral `0.8 m` y yaw absoluto
`0.0 deg`. Con este bloque, S07 queda cerrado formalmente.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 137 | T0 | 9 | `phase05_20260608_130247_e28ac4f0` | `accepted` | error final `0.8895 m`, cierre `LOITER`, `armed=False` |
| 138 | T1 | 9 | `phase05_20260608_131411_c3801822` | `accepted` | error final `0.0327 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 139 | T1 | 10 | `phase05_20260608_131743_02ff76bb` | `accepted` | error final `0.0101 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 140 | T0 | 10 | `phase05_20260608_132016_13101669` | `accepted` | error final `0.7797 m`, cierre `LOITER`, `armed=False` |

Se verifico que los cuatro CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 117 y 214
lineas por archivo.

Estado acumulado de S07:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

Pares completos finales de S07: R01, R02, R03, R04, R05, R06, R07, R08,
R09 y R10.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7945 m` | `-9.515 s` |
| R02 | `0.7331 m` | `-12.984 s` |
| R03 | `0.6891 m` | `-9.537 s` |
| R04 | `0.7596 m` | `-11.536 s` |
| R05 | `0.6569 m` | `-5.971 s` |
| R06 | `0.6663 m` | `-10.433 s` |
| R07 | `0.7494 m` | `-9.591 s` |
| R08 | `0.7611 m` | `-5.316 s` |
| R09 | `0.8568 m` | `-14.880 s` |
| R10 | `0.7696 m` | `-12.342 s` |

Resumen curado final de S07 con R01-R10:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 10 | `0.7660 m` | `26.601 s` | `73.1 %` |
| T1 | 10 | `0.0224 m` | `36.812 s` | `100.0 %` |

## Inicio S08 R01-R04

Se inicio `P05_S08_H3_Y08_YAW15`, con altura inicial `3.0 m`, offset lateral
`0.8 m` y yaw absoluto `15.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 141 | T0 | 1 | `phase05_20260608_145204_e031cbc5` | `accepted` | error final `0.7989 m`, cierre `LOITER`, `armed=False` |
| 142 | T1 | 1 | `phase05_20260608_145623_5cf1f00c` | `accepted` | error final `0.0131 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 143 | T1 | 2 | `phase05_20260608_145858_66086f4f` | `accepted` | error final `0.0330 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 144 | T0 | 2 | `phase05_20260608_150148_ca339b4f` | `accepted` | error final `0.7940 m`, cierre `LOITER`, `armed=False` |
| 145 | T0 | 3 | `phase05_20260608_150412_e0539f18` | `accepted` | error final `0.7093 m`, cierre `LOITER`, `armed=False` |
| 146 | T1 | 3 | `phase05_20260608_150643_cddaa57d` | `accepted` | error final `0.0317 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 147 | T1 | 4 | `phase05_20260608_150901_e29040c2` | `accepted` | error final `0.0067 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 148 | T0 | 4 | `phase05_20260608_151114_e6e1f464` | `accepted` | error final `0.7088 m`, cierre `LOITER`, `armed=False` |

Se verifico que los ocho CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 105 y 186
lineas por archivo.

Estado acumulado de S08:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 4 | 10 | 6 |
| T1 | 4 | 10 | 6 |

Pares completos actuales de S08: R01, R02, R03 y R04.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7858 m` | `-10.855 s` |
| R02 | `0.7610 m` | `-10.834 s` |
| R03 | `0.6776 m` | `-10.033 s` |
| R04 | `0.7021 m` | `-10.139 s` |

Resumen parcial curado de S08 con R01-R04:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 4 | `0.7528 m` | `24.340 s` | `65.4 %` |
| T1 | 4 | `0.0211 m` | `34.805 s` | `100.0 %` |

## Avance S08 R05-R08

Se ejecuto el segundo bloque parcial de `P05_S08_H3_Y08_YAW15`,
correspondiente a R05-R08 con altura inicial `3.0 m`, offset lateral `0.8 m`
y yaw absoluto `15.0 deg`.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 149 | T0 | 5 | `phase05_20260608_153204_75c1cf12` | `accepted` | error final `0.7574 m`, cierre `LOITER`, `armed=False` |
| 150 | T1 | 5 | `phase05_20260608_153518_1f649825` | `accepted` | error final `0.0331 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 151 | T1 | 6 | `phase05_20260608_153752_cbd723c3` | `accepted` | error final `0.0128 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 152 | T0 | 6 | `phase05_20260608_154116_86105482` | `accepted` | error final `0.7647 m`, cierre `LOITER`, `armed=False` |
| 153 | T0 | 7 | `phase05_20260608_154347_ecf70a40` | `accepted` | error final `0.7836 m`, cierre `LOITER`, `armed=False` |
| 154 | T1 | 7 | `phase05_20260608_154624_690038b4` | `accepted` | error final `0.0028 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 155 | T1 | 8 | `phase05_20260608_154849_a312c4d5` | `accepted` | error final `0.0218 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 156 | T0 | 8 | `phase05_20260608_155107_6001aa64` | `accepted` | error final `0.7530 m`, cierre `LOITER`, `armed=False` |

Se verifico que los ocho CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 106 y 188
lineas por archivo.

Estado acumulado de S08:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 8 | 10 | 2 |
| T1 | 8 | 10 | 2 |

Pares completos actuales de S08: R01, R02, R03, R04, R05, R06, R07 y R08.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7858 m` | `-10.855 s` |
| R02 | `0.7610 m` | `-10.834 s` |
| R03 | `0.6776 m` | `-10.033 s` |
| R04 | `0.7021 m` | `-10.139 s` |
| R05 | `0.7243 m` | `-8.877 s` |
| R06 | `0.7518 m` | `-8.576 s` |
| R07 | `0.7807 m` | `-12.058 s` |
| R08 | `0.7312 m` | `-11.164 s` |

Resumen parcial curado de S08 con R01-R08:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 8 | `0.7587 m` | `24.793 s` | `66.5 %` |
| T1 | 8 | `0.0194 m` | `35.110 s` | `100.0 %` |

## Cierre S08 R09-R10

Se ejecuto el bloque final de `P05_S08_H3_Y08_YAW15`, correspondiente a
R09-R10 con altura inicial `3.0 m`, offset lateral `0.8 m` y yaw absoluto
`15.0 deg`. Con este bloque, S08 y la ejecucion formal de Fase 05 quedan
cerrados.

| Run | Tratamiento | Repeticion | run_id | Curacion | Resultado |
|---:|---|---:|---|---|---|
| 157 | T0 | 9 | `phase05_20260608_160251_dafcb6ba` | `accepted` | error final `0.7458 m`, cierre `LOITER`, `armed=False` |
| 158 | T1 | 9 | `phase05_20260608_160541_dcf510ce` | `accepted` | error final `0.0222 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 159 | T1 | 10 | `phase05_20260608_160802_e1f96ad8` | `accepted` | error final `0.0280 m`, deteccion `100.0 %`, perdidas `0`, cierre `LOITER`, `armed=False` |
| 160 | T0 | 10 | `phase05_20260608_161033_b151d6ea` | `accepted` | error final `0.6916 m`, cierre `LOITER`, `armed=False` |

Se verifico que los cuatro CSV crudos del bloque existen bajo
`data/logs/phase05_experiments/raw/`, con tamano no nulo y entre 119 y 186
lineas por archivo.

Estado final de S08:

| Tratamiento | Aceptadas | Esperadas | Faltantes |
|---|---:|---:|---:|
| T0 | 10 | 10 | 0 |
| T1 | 10 | 10 | 0 |

Pares completos finales de S08: R01, R02, R03, R04, R05, R06, R07, R08,
R09 y R10.

En los pares completos, T1 mantiene reduccion positiva del error final:

| Repeticion | Delta error final `T0 - T1` | Delta tiempo `T0 - T1` |
|---:|---:|---:|
| R01 | `0.7858 m` | `-10.855 s` |
| R02 | `0.7610 m` | `-10.834 s` |
| R03 | `0.6776 m` | `-10.033 s` |
| R04 | `0.7021 m` | `-10.139 s` |
| R05 | `0.7243 m` | `-8.877 s` |
| R06 | `0.7518 m` | `-8.576 s` |
| R07 | `0.7807 m` | `-12.058 s` |
| R08 | `0.7312 m` | `-11.164 s` |
| R09 | `0.7237 m` | `-8.021 s` |
| R10 | `0.6636 m` | `-9.851 s` |

Resumen curado final de S08 con R01-R10:

| Tratamiento | n | Error final medio | Tiempo medio hasta umbral | Deteccion aceptada media |
|---|---:|---:|---:|---:|
| T0 | 10 | `0.7507 m` | `25.093 s` | `67.9 %` |
| T1 | 10 | `0.0205 m` | `35.134 s` | `100.0 %` |

Estado acumulado del experimento tras regenerar tablas:

- corridas formales aceptadas: `160`;
- pares T0/T1 aceptados: `80`;
- escenarios completos: `P05_S01_H2_Y04_YAW0`,
  `P05_S02_H2_Y04_YAW15`, `P05_S03_H2_Y08_YAW0` y
  `P05_S04_H2_Y08_YAW15`, `P05_S05_H3_Y04_YAW0` y
  `P05_S06_H3_Y04_YAW15`, `P05_S07_H3_Y08_YAW0` y
  `P05_S08_H3_Y08_YAW15`;
- celdas escenario/tratamiento completas: `16/16`;
- celdas faltantes: ninguna.

## Siguiente accion

La ejecucion formal de Fase 05 queda cerrada. Continuar con el analisis final
de resultados, generacion de figuras comparativas y redaccion de la discusion
T0/T1 usando exclusivamente corridas con `curation_status=accepted`.

### Justificacion metodologica de la enmienda P05-A01

La enmienda `P05-A01` se adopta a partir del escenario `P05_S02_H2_Y04_YAW15`
debido a perdidas transitorias del marcador cerca del umbral visual bajo
`yaw_deg=15.0`. Las corridas de `P05_S01_H2_Y04_YAW0` se conservan porque no
presentaron abortos por perdida de marcador y porque el parametro modificado
solo afecta la tolerancia ante perdidas consecutivas, no la ley de correccion
lateral, la velocidad maxima horizontal, la tasa de descenso ni el umbral de
aterrizaje visual. No obstante, el analisis final debera reportar esta enmienda
como una modificacion controlada del protocolo experimental.

Mantener actualizadas las tablas:

```powershell
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```
