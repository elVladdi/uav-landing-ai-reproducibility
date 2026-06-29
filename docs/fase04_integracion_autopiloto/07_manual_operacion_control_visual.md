# Manual de Operacion - Control Visual

## Activar entorno

```powershell
cd <REPO_ROOT>
.\.venv\Scripts\Activate.ps1
```

## Verificar PX4

```powershell
.\scripts\check_px4_connection.ps1
python src\control\run_px4_telemetry_check.py --duration 10
```

## Verificar percepcion sin comandos

Estos comandos asumen que el marcador ArUco ya esta visible para
`bottom_center`.

```powershell
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 20 --with-px4 --detector aruco
```

Si se desea guardar imagenes anotadas:

```powershell
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 20 --with-px4 --save-annotated --detector aruco
```

Si el UAV esta en tierra, la camara inferior puede no ver la plataforma. En ese
caso, elevar con PX4, repetir el dry-run y aterrizar:

```powershell
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 20 --with-px4 --save-annotated --detector aruco
python src\control\run_px4_land.py --confirm-send
```

## Marcador fiduciario ArUco

La Fase 04 migra las pruebas nuevas a un marcador fiduciario ArUco. La
configuracion por defecto esta en `configs/perception_config.json`:

```text
dictionary_name = DICT_4X4_50
marker_id = 23
```

Verificar que OpenCV tenga el modulo ArUco:

```powershell
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'aruco'))"
```

Generar solo la textura, sin conectar con AirSim:

```powershell
python src\perception\spawn_fiducial_marker.py --generate-only --dictionary-name DICT_4X4_50 --marker-id 23
```

Secuencia centrada con AirSimNH y PX4 ya activos:

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_center --under-vehicle --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06C_ARUCO_FIDUCIAL_DRY_RUN
python src\perception\clear_landing_markers.py
python src\control\run_px4_land.py --confirm-send --timeout 45
```

La prueba centrada ya fue validada con el run
`phase04_20260502_154838_c02260b6`, con 10/10 detecciones aceptadas del ArUco
ID `23`.

El signo lateral con ArUco ya fue validado con desplazamiento positivo y
negativo. Para reproducir esa evidencia, repetir la secuencia usando:

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_offset_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06D_ARUCO_OFFSET_Y_POS
python src\perception\clear_landing_markers.py
```

Luego cambiar a `--offset-y -0.8` y
`--object-name phase04_aruco_marker_offset_y_neg`. Despues de la segunda
corrida, limpiar marcadores y aterrizar:

```powershell
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_offset_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06D_ARUCO_OFFSET_Y_NEG
python src\perception\clear_landing_markers.py
python src\control\run_px4_land.py --confirm-send --timeout 45
```

## Probar Offboard hover

Este comando envia setpoints a PX4. Usarlo solo con AirSimNH y PX4 listos:

```powershell
python src\control\run_offboard_start_diagnostic.py --confirm-send --strategy all
python src\control\run_offboard_hover_test.py --confirm-send --duration 8 --takeoff-altitude 2.0
```

Interpretacion del diagnostico:

- `NO_SETPOINT_SET` en todas las estrategias: MAVSDK no registro ningun
  setpoint; no repetir hover en vuelo.
- `COMMAND_DENIED` u otro rechazo de modo: el setpoint fue registrado, pero PX4
  no acepto Offboard en tierra; se puede intentar P04-V03 con el entorno
  reiniciado y telemetria estable.

Si todas las estrategias devuelven `NO_SETPOINT_SET`, probar la ruta alternativa
con MAVLink directo:

```powershell
python -m pip install -r requirements.txt
python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send
```

No ejecutar MAVSDK y pymavlink al mismo tiempo sobre `UDP 14601`.

Si aparece `struct.error: required argument is not a float`, verificar que se
este usando la version corregida del script. Ese error corresponde al
empaquetado local del modo PX4 y no a un rechazo real de MAVLink por PX4.

Si el resultado muestra `MAV_RESULT_ACCEPTED` pero `post_mode=UNKNOWN`, repetir
con mas tiempo posterior de setpoints para registrar el heartbeat crudo:

```powershell
python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send --post-seconds 3
```

El resultado es suficiente para avanzar si aparece `post_mode=OFFBOARD` o
`px4_main_mode=6` en `notes`.

La ruta MAVLink directa quedo validada en P04-V02C con el run
`phase04_20260502_203009_822c9921`.

## Probar hover MAVLink directo

Este ensayo no usa MAVSDK Offboard. Primero se eleva el UAV con la prueba PX4
action ya validada; luego se ejecuta el hover por MAVLink directo:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_mavlink_direct_hover_test.py --confirm-send --duration 5
```

Si la primera telemetria muestra `mode=OFFBOARD`, `armed=False` y `alt=0.0`, no
intentar despegar todavia. Recuperar primero el modo:

```powershell
python src\control\run_mavlink_mode_recovery.py --confirm-send
python src\control\run_px4_telemetry_check.py --duration 5
```

El script solicita `LAND` al finalizar. Si se desea dejar el UAV en vuelo solo
para diagnostico controlado, agregar `--no-land-after`, pero la opcion
recomendada para la validacion piloto es aterrizar automaticamente.

Si la consola muestra `MAV_RESULT_ACCEPTED` pero el script marca error por falta
de heartbeat inmediato, revisar el CSV: si una fila posterior contiene
`flight_mode=OFFBOARD` o `px4_main_mode=6`, repetir la prueba. Esa condicion
indica confirmacion tardia de modo, no rechazo del canal MAVLink.

El hover minimo por MAVLink directo quedo validado con el run
`phase04_20260503_095523_1799a2c0`: cinco muestras `hover` en `OFFBOARD`,
altitud estable cercana a 2.0 m, `status=ok`, aterrizaje monitoreado y cierre en
`LOITER`, `armed=False`.

## Probar correccion lateral activa

Este ensayo usa ArUco y MAVLink directo. No desciende durante el lazo visual:
mantiene `command_down_m_s=0.0` y envia solo correcciones horizontales
limitadas. El script aterriza al finalizar.

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_active_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --save-annotated --max-horizontal-speed 0.12 --scenario-id P04_V07_ARUCO_ACTIVE_LATERAL_POS
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Aceptar la prueba solo si el CSV contiene `offboard_start` en `OFFBOARD`,
muestras `visual_servo` con `command_sent=True`, detecciones ArUco aceptadas y
una reduccion del error lateral absoluto en la fila `summary`.

El primer ensayo positivo quedo validado con
`phase04_20260503_101736_206196b4`: el error lateral absoluto bajo de `0.4154`
a `0.1797`, con 30/30 detecciones aceptadas y `command_down_m_s=0.0`.

Para cerrar la simetria activa, repetir cambiando el desplazamiento y el
`scenario_id`:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_active_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --save-annotated --max-horizontal-speed 0.12 --scenario-id P04_V07_ARUCO_ACTIVE_LATERAL_NEG
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

La simetria activa quedo validada con
`phase04_20260503_102830_f0c4fefa`: el error lateral absoluto bajo de `0.4017`
a `0.1905`, con 30/30 detecciones aceptadas, `command_right_m_s` negativo y
`command_down_m_s=0.0`.

## Probar abort por marcador no aceptado

Este ensayo usa un ArUco visible pero con ID incorrecto (`24`). Como el detector
espera el ID `23`, el agente debe mantener comandos cero, superar el limite de
detecciones no aceptadas, marcar `abort` y aterrizar.

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_wrong_id_abort --under-vehicle --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 24 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --save-annotated --max-horizontal-speed 0.12 --max-missing-detections 3 --scenario-id P04_V08_ARUCO_WRONG_ID_ABORT
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Aceptar solo si el CSV registra `accepted_detection=False`, `status=abort` o
`aborted=True` en `summary`, comandos en cero y cierre seguro con `LAND`/`LOITER`.

La corrida `phase04_20260503_104002_62c3998b` valido este caso: el marcador con
ID `24` no fue aceptado por el detector configurado para ID `23`; el lazo
registro `accepted_count=0`, `missing_detections=4`, `aborted=True`, comandos
en cero y cierre seguro.

## Ensayo piloto de aterrizaje visual

Ejecutar solo despues de validar dry-run, hover MAVLink directo, correccion
lateral activa y respuesta segura ante perdida de marcador:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_descent_reduced --under-vehicle --z 0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 25 --detector aruco --save-annotated --max-horizontal-speed 0.10 --max-missing-detections 3 --enable-descent --descent-rate 0.08 --centered-cycles-required 5 --landing-complete-altitude 0.80 --scenario-id P04_V09B_ARUCO_VISUAL_DESCENT_REDUCED_MARKER
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Aceptar solo si `offboard_start` queda en `OFFBOARD`, el marcador ID `23` es
aceptado, `centered_cycles` alcanza el umbral, aparece
`controller_reason=vision_descent` con `command_down_m_s > 0.0`, la altitud baja
gradualmente, el `summary` registra `landing_threshold_reached=True` y el cierre
final aterriza y recupera `LOITER`.

La corrida P04-V09A (`phase04_20260503_105624_4ddee5b7`) fue parcial: valido el
inicio del descenso visual, pero el ArUco grande se perdio cerca de `1.52 m`.
Por eso esta secuencia usa marcador reducido y umbral piloto `0.80 m`.

La corrida P04-V09B (`phase04_20260503_110722_787b177f`) valido el descenso
asistido: 96/97 detecciones aceptadas, 92 ciclos con descenso, llegada a
`landing_threshold_reached=True`, sin `abort`, y cierre `LAND`/`LOITER`.

La repeticion P04-V10-02 (`phase04_20260503_111811_e34f112f`) tambien fue
positiva: 81/81 detecciones aceptadas, 77 ciclos de descenso,
`landing_threshold_reached=True`, `aborted=False` y cierre `LAND`/`LOITER`.

La repeticion P04-V10-03 (`phase04_20260503_112921_7c3ef4a8`) cerro la
repetibilidad piloto: 79/80 detecciones aceptadas, 75 ciclos de descenso,
`landing_threshold_reached=True`, `aborted=False` y cierre `LAND`/`LOITER`.

Con estas tres corridas, no quedan comandos pendientes para cerrar Fase 04.

## Repetibilidad piloto P04-V10

P04-V10 uso el mismo protocolo de P04-V09B para dos repeticiones adicionales.
La repeticion 2 y la repeticion 3 quedaron validadas, completando tres corridas
positivas comparables. Los comandos siguientes se conservan como referencia
operativa para reproducir la repetibilidad si fuera necesario.

Repeticion 2:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_repeat_02 --under-vehicle --z 0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 25 --detector aruco --save-annotated --max-horizontal-speed 0.10 --max-missing-detections 3 --enable-descent --descent-rate 0.08 --centered-cycles-required 5 --landing-complete-altitude 0.80 --scenario-id P04_V10_ARUCO_VISUAL_DESCENT_REPEAT_02
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Repeticion 3:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_repeat_03 --under-vehicle --z 0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 25 --detector aruco --save-annotated --max-horizontal-speed 0.10 --max-missing-detections 3 --enable-descent --descent-rate 0.08 --centered-cycles-required 5 --landing-complete-altitude 0.80 --scenario-id P04_V10_ARUCO_VISUAL_DESCENT_REPEAT_03
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

## Dry-run HSV historico con marcador desplazado

Para validar el signo lateral del controlador sin enviar comandos, ejecutar
primero el desplazamiento positivo:

```powershell
python src\perception\clear_landing_markers.py --object-regex ".*phase0[34].*marker.*"
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_landing_marker.py --object-name phase04_marker_offset_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector hsv
python src\perception\clear_landing_markers.py --object-regex ".*phase0[34].*marker.*"
python src\control\run_px4_land.py --confirm-send --timeout 45
```

Luego repetir la misma secuencia con el desplazamiento negativo, cambiando el
nombre del objeto:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase04_marker_offset_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01
```

La validacion queda aceptada si `command_right_m_s` es positivo para
`--offset-y 0.8` y negativo para `--offset-y -0.8`, con deteccion aceptada y
`centered=False`.

## Ajustar signos o ganancias

Archivo:

```text
configs/control_config.json
```

Campos principales:

```json
"gain_forward_mps_per_norm_error": 0.25,
"gain_right_mps_per_norm_error": 0.25,
"forward_error_sign": -1.0,
"right_error_sign": 1.0
```

Si el dron se aleja del marcador, detener la prueba y corregir los signos antes
de repetir.

## Salidas

```text
data/logs/phase04_control/
outputs/figures/phase04_control/
```
