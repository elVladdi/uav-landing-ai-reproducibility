# Protocolo de Ejecucion Formal

## Objetivo

Ejecutar el bloque formal de Fase 05 sin lanzar las 160 corridas de una sola
vez. La ejecucion debe avanzar por bloques pequenos, regenerando metricas y
reporte despues de cada bloque.

## Precondiciones

- AirSimNH abierto y estable.
- PX4 SITL activo en WSL2.
- Conexion MAVLink directa disponible en UDP 14601.
- Entorno `.venv` activo.
- Piloto minimo aceptado.
- Regla de curacion aplicada.

## Generar plan formal

```powershell
python src\experiments\phase05_generate_run_plan.py --start-index 1 --limit 8
```

Esto genera:

```text
outputs/tables/phase05_formal_run_plan.csv
outputs/tables/phase05_formal_run_commands.md
```

El plan completo contiene 160 corridas: 8 escenarios, 2 tratamientos y 10
repeticiones por tratamiento.

## Validacion previa de yaw

Antes de ejecutar escenarios con `YAW15`, validar una vez el comando de yaw
absoluto:

```powershell
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_phase05_yaw_setup.py --confirm-send --method offboard-yaw-rate --absolute-yaw-deg 15.0 --yaw-speed-deg-s 10.0 --yaw-kp 0.80 --tolerance-deg 3.0 --wait-timeout 25.0
python src\control\run_px4_land.py --confirm-send --timeout 30
python src\control\run_px4_telemetry_check.py --duration 5
```

La validacion es aceptable si el helper de yaw informa `Yaw setup accepted` y
la telemetria posterior queda en tierra. Si despues del aterrizaje PX4 conserva
`armed=True`, desarmar antes de continuar:

```powershell
python src\control\run_px4_disarm.py --confirm-send
python src\control\run_px4_telemetry_check.py --duration 5
```

Si la validacion de yaw falla, no ejecutar los escenarios `YAW15` hasta registrar
y corregir la incidencia. Si el desarme no deja `armed=False`, reiniciar PX4 /
AirSimNH antes de iniciar el siguiente escenario.

## Politica de bloques

Ejecutar bloques de 8 corridas como punto de partida. Un bloque de 8 corridas
cubre cuatro pares T0/T1. Tras cada bloque:

```powershell
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```

Revisar `outputs/tables/phase05_experiments/phase05_completion_check.csv` antes
de continuar.

## Enmienda P05-A01

Durante el inicio de `P05_S02_H2_Y04_YAW15`, dos intentos T1 corrigieron el
error lateral y cerraron seguros, pero quedaron excluidos por perdida
consecutiva del marcador justo antes del umbral visual de `0.80 m`. Una prueba
diagnostica no formal con `max_missing_detections=6` alcanzo el umbral sin
aborto.

Desde esta enmienda, el tratamiento T1 formal usa:

```text
max_missing_detections = 6
```

Las corridas diagnosticas mantienen `scenario_id` terminado en `_DIAG` y quedan
excluidas automaticamente por curacion.

## Orientacion inicial

Los escenarios con `yaw_deg=15.0` usan:

```powershell
python src\control\run_phase05_yaw_setup.py --confirm-send --method offboard-yaw-rate --absolute-yaw-deg 15.0
```

Los escenarios con `yaw_deg=0.0` tambien deben ejecutar el helper, usando
`--absolute-yaw-deg 0.0`, para evitar que el yaw residual de una corrida
anterior contamine el siguiente escenario. Este comando se ejecuta despues del
despegue y antes de crear el marcador. Si no alcanza la tolerancia configurada,
detener el bloque y registrar la incidencia antes de continuar.

## Enmienda P05-A02

La revision de los logs de S02 mostro que el helper anterior aplicaba
`--relative-yaw-deg 15.0`; por tanto, el yaw real dependia de la orientacion
residual de la corrida previa. Desde `P05-A02`, el generador formal usa
`--absolute-yaw-deg` para todos los escenarios.

## Flujo por corrida

Cada bloque generado sigue esta secuencia:

1. limpiar marcadores residuales `phase05` antes de despegar;
2. despegar hasta la altura del escenario;
3. aplicar yaw si el escenario lo requiere;
4. crear marcador ArUco bajo el vehiculo con el offset del escenario;
5. ejecutar `T0` o `T1`;
6. limpiar marcador;
7. comprobar telemetria;
8. regenerar resumen y reporte.

## Criterio para continuar

Continuar al siguiente bloque solo si:

- PX4 queda en modo seguro despues de cada corrida y con `armed=False`;
- no quedan marcadores residuales; si la limpieza inicial detecta objetos
  `phase05` remanentes, registrar la incidencia y confirmar que fueron
  destruidos antes de despegar;
- `phase05_run_summary.csv` se regenera sin errores;
- no aparecen duplicados no resueltos;
- las corridas fallidas quedan documentadas como `excluded` o `superseded`.

Si un mismo escenario acumula dos o mas exclusiones T1 consecutivas por perdida
terminal del marcador, pausar la secuencia formal antes del siguiente bloque y
ejecutar una prueba diagnostica no formal con `scenario_id` terminado en
`_DIAG`. No modificar la configuracion formal hasta que el diagnostico sustente
una enmienda metodologica documentada.

### Diagnostico de perdida terminal T1

Para `P05_S02_H2_Y04_YAW15`, el diagnostico con yaw absoluto, tolerancia de
perdidas `10` y `landing_complete_altitude=0.90` redujo el error lateral, pero
no alcanzo el umbral visual antes de perder el marcador. Se ejecuto una segunda
prueba diagnostica no formal con:

```text
scenario_id = P05_S02_H2_Y04_YAW15_ABSYAW_H105_DIAG
max_missing_detections = 10
landing_complete_altitude = 1.05
```

La prueba alcanzo `landing_threshold_reached=True` sin aborto, con deteccion
aceptada `100.0 %`, `lost_detection_count=0`, error final `0.0218 m` y cierre
seguro `LOITER`, `armed=False`. Por tanto, desde la enmienda `P05-A03`, la
configuracion formal T1 usa:

```text
landing_complete_altitude_m = 1.05
```

Aunque el parametro se registra historicamente bajo `frozen_t1`, los comandos
formales generados lo aplican a T0 y T1. Por tanto, los pares nuevos o
correctivos posteriores a `P05-A03` deben ejecutarse con ambos tratamientos bajo
`landing_complete_altitude_m=1.05`.

Los T1 excluidos antes de esta enmienda no deben rescatarse por curacion
manual. Si se corrigen repeticiones incompletas, repetir el par completo o
registrar la mezcla de umbrales como incidencia metodologica antes del analisis.

### Incidencia de desarme

Si `run_px4_disarm.py` devuelve `COMMAND_DENIED` y AirSimNH indica que el
vehiculo no esta aterrizado, no repetir el desarme en bucle. Reiniciar AirSimNH
y PX4, luego confirmar:

```text
mode=HOLD
armed=False
alt=0.0
```

Solo despues de esa telemetria limpia se puede iniciar una nueva prueba.

### Cierre inesperado de AirSimNH

Si AirSimNH se cierra durante una corrida:

- detener la secuencia formal;
- reiniciar AirSimNH/PX4 y confirmar telemetria segura antes de repetir;
- no continuar con el siguiente run hasta cerrar o descartar el intento
  interrumpido;
- si existe CSV parcial, regenerar metricas y marcarlo como `excluded` o
  `superseded` segun corresponda;
- si no existe fila formal en `phase05_run_summary.csv`, registrar la incidencia
  en documentacion y repetir el mismo run.

Aplicacion: en S03, el primer intento de `Run 47` genero CSV parcial sin
`land_complete`; se marco como `superseded` por la repeticion valida del mismo
run.

### Aborto aislado por perdida temprana de marcador

Si una T1 aborta de forma aislada por perdida temprana del marcador y otros T1
del mismo escenario si fueron aceptados, repetir primero el mismo run con la
misma configuracion. No adoptar una nueva enmienda metodologica con un unico
aborto aislado.

Aplicacion: en S03, el primer intento de `Run 46` aborto por perdida temprana
del marcador y fue marcado como `superseded` por la repeticion aceptada
`phase05_20260509_003307_468906cb`. Al quedar R03 pareado, se continuo sin
nueva enmienda; despues de cerrar R01-R10, S03 queda completo y el siguiente
bloque pendiente parte en `Run 61` para S04.

Aplicacion S04: en `Run 67`, el primer intento T1 de R04 aborto por perdida
temprana de marcador. Como los T1 de R01-R03 fueron aceptados, se repitio el
mismo run con la misma configuracion. Tras dos cierres intempestivos de
AirSimNH sin filas formales adicionales, la repeticion valida
`phase05_20260509_214330_4ae8d025` quedo aceptada y el intento abortado
`phase05_20260509_212824_d3037b9b` quedo como `superseded`.

## Cierre del bloque formal

Al finalizar los 160 intentos planificados, el cierre cuantitativo se hace con:

```powershell
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```

Usar para tesis los archivos:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_completion_check.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```
