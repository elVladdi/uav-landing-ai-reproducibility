# Protocolo de Validación - Fase 04

## Preparación

Levantar el entorno en el orden documentado en Fase 02:

1. abrir AirSimNH;
2. iniciar PX4 SITL en WSL2;
3. crear el canal MAVLink dedicado hacia UDP 14601;
4. activar `.venv` en PowerShell;
5. validar conexión PX4.

```powershell
cd <REPO_ROOT>
.\.venv\Scripts\Activate.ps1
.\scripts\check_px4_connection.ps1
```

Nota: aunque Blocks fue útil como entorno controlado en fases previas, las
pruebas de Fase 04 se ejecutan en AirSimNH porque alli quedo consolidada la
integracion real AirSimNH + PX4 SITL + MAVSDK por UDP 14601.

## Pruebas mínimas

| Código | Prueba | Comando | Criterio |
| --- | --- | --- | --- |
| P04-V01 | Telemetría PX4 | `python src\control\run_px4_telemetry_check.py` | Log con modo, armado, health y posición NED |
| P04-V02 | Arm/takeoff/land PX4 | `python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0` | PX4 y AirSim muestran movimiento vertical coherente |
| P04-V02B | Diagnóstico Offboard start en tierra | `python src\control\run_offboard_start_diagnostic.py --confirm-send --strategy all` | Distingue si MAVSDK registra setpoints antes de `offboard.start()` |
| P04-V02C | Diagnóstico MAVLink directo | `python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send` | Evalúa si PX4 acepta setpoints sin pasar por MAVSDK Offboard |
| P04-V03 | Offboard hover | `python src\control\run_offboard_hover_test.py --confirm-send --duration 8 --takeoff-altitude 2.0` | Offboard inicia y mantiene setpoint neutro |
| P04-V03B | Hover MAVLink directo | `python src\control\run_mavlink_direct_hover_test.py --confirm-send --duration 5` | Con UAV ya elevado, PX4 entra a `OFFBOARD` por MAVLink directo y mantiene setpoint de posicion actual |
| P04-V04 | Nudge lateral | Ajuste temporal de comandos laterales | Movimiento pequeno y reversible |
| P04-V05 | Percepción + telemetría | `python src\control\run_visual_servo_dry_run.py --with-px4` | Detección y telemetría en el mismo log |
| P04-V06 | Dry-run visual servo | `python src\control\run_visual_servo_dry_run.py` | Calcula comandos sin enviarlos |
| P04-V06B | Dry-run con marcador desplazado | Generar marcador con `--offset-y` en ambos sentidos | El comando lateral calculado no es cero y cambia de signo de forma coherente |
| P04-V06C | Dry-run con marcador fiduciario ArUco | `spawn_fiducial_marker.py` + `run_visual_servo_dry_run.py --detector aruco` | Detecta el ID esperado, calcula error visual y registra `detector_method=aruco_fiducial` |
| P04-V06D | Signo lateral con ArUco desplazado | Generar ArUco con `--offset-y 0.8` y `--offset-y -0.8` | `command_right_m_s` cambia de signo al invertir el desplazamiento lateral |
| P04-V07 | Corrección lateral | Ensayo con `--confirm-send` | Reduce error visual sin descender |
| P04-V08 | Abort por pérdida | Ocultar marcador o bajar confianza | Ejecuta abort/land sin oscilación |
| P04-V09 | Descenso asistido piloto | `python src\control\run_mavlink_visual_servo_test.py --confirm-send --enable-descent` | Desciende solo estando centrado |
| P04-V10 | Repetibilidad piloto | Repetir 3 veces | Logs comparables con mismo escenario |

### Figura de secuencia de validación

![Secuencia de validación técnica de la Fase 04](<Figuras/Secuencia de validación técnica de la fase 04.png>)

*Figura 9. Progresión de las pruebas P04 desde telemetría y despegue PX4 hasta control visual activo, abort seguro, descenso asistido y repetibilidad piloto.*

## Orden recomendado

No ejecutar P04-V09 antes de que P04-V01, P04-V03B, P04-V06D, P04-V07 y
P04-V08 esten aceptadas.

Secuencia inicial:

```powershell
python src\control\run_px4_telemetry_check.py --duration 10
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0
python src\control\run_offboard_start_diagnostic.py --confirm-send --strategy all
python src\control\run_offboard_hover_test.py --confirm-send --duration 8 --takeoff-altitude 2.0
```

Si todas las estrategias de P04-V02B devuelven `NO_SETPOINT_SET`, no ejecutar
P04-V03 en vuelo hasta revisar MAVSDK/PX4. Si al menos una estrategia devuelve
`COMMAND_DENIED` u otro rechazo de modo, el setpoint si fue registrado y el
siguiente paso puede ser P04-V03 con AirSimNH reiniciado y telemetria estable.

Si P04-V02B confirma `NO_SETPOINT_SET` en todas las estrategias, ejecutar la
subfase tecnica P04-V02C con MAVLink directo:

```powershell
python -m pip install -r requirements.txt
python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send
```

No ejecutar P04-V02C simultaneamente con MAVSDK sobre el mismo puerto UDP.

Nota: los intentos P04-V02C iniciales recibieron heartbeat por `pymavlink`, pero
fallaron por un error local al empaquetar el modo PX4 `OFFBOARD`. La prueba debe
repetirse con el script corregido antes de aceptar o descartar MAVLink directo.

La repeticion `phase04_20260502_202237_55b4ea94` confirmo un avance importante:
PX4 respondio `MAV_RESULT_ACCEPTED` a `MAV_CMD_DO_SET_MODE`, pero el modo
posterior fue reportado como `UNKNOWN`. Por ello, el diagnostico P04-V02C debe
registrar ahora los campos crudos del heartbeat y mantener setpoints despues de
la solicitud de modo:

```powershell
python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send --post-seconds 3
```

Aceptar P04-V02C como ruta de setpoints solo si `post_mode=OFFBOARD` o si las
notas registran `px4_main_mode=6`.

La corrida `phase04_20260502_203009_822c9921` cumple este criterio:
`post_mode=OFFBOARD`, `px4_main_mode=6` y `MAV_RESULT_ACCEPTED`.

## Prueba P04-V03B: hover MAVLink directo

Esta prueba reemplaza temporalmente P04-V03 como ensayo de hover activo, porque
MAVSDK Offboard quedo limitado por `NO_SETPOINT_SET`. P04-V03B no arma ni
despega; asume que el UAV ya esta elevado y estable. El script toma la posicion
NED actual, la usa como setpoint de posicion, solicita `OFFBOARD` por MAVLink
directo y mantiene ese setpoint durante unos segundos.

Secuencia:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\control\run_mavlink_mode_recovery.py --confirm-send
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_mavlink_direct_hover_test.py --confirm-send --duration 5
```

El comando de recuperacion solo es necesario si la telemetria previa muestra
`mode=OFFBOARD` o `mode=LAND` estando desarmado y en tierra. Si PX4 ya esta en
`HOLD/LOITER`, se puede omitir.

El script de hover solicita `LAND` al finalizar, salvo que se use
`--no-land-after`.

Criterios de aceptacion:

- precheck con `armed=True`;
- altitud mayor o igual a `0.8 m`;
- evento `offboard_start` con `flight_mode=OFFBOARD`;
- muestras `hover` con `status=ok`;
- comandos enviados (`command_sent=True`) y velocidades cercanas a cero;
- aterrizaje solicitado al final sin traceback.

Nota: la corrida `phase04_20260502_204145_87918081` demostro que PX4 si puede
entrar a `OFFBOARD` en vuelo por MAVLink directo, pero la confirmacion llego
despues de la ventana corta del script. No se acepta como hover porque no hubo
muestras sostenidas `hover`; se debe repetir con la espera corregida.

La repeticion `phase04_20260503_095523_1799a2c0` cerro P04-V03B como validada:
PX4 entro a `OFFBOARD`, registro cinco muestras `hover` con `status=ok` a
aproximadamente 2.0 m y finalizo con aterrizaje y recuperacion a `LOITER`.

Si el UAV no despega visualmente en AirSimNH durante P04-V02, no continuar con
Offboard. Primero debe resolverse la integracion fisica AirSimNH + PX4.

Para descartar que el marcador generado interfiera con el despegue, limpiar los
objetos de marcador y repetir P04-V02 sin plataforma:

```powershell
python src\perception\clear_landing_markers.py --object-regex ".*phase0[34].*marker.*"
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8
```

## Prueba P04-V06B: marcador desplazado

Esta prueba valida los signos del controlador visual sin enviar comandos a PX4.
El UAV debe estar elevado con PX4 y el marcador se genera despues del despegue.

Secuencia para desplazamiento lateral positivo en NED Y:

```powershell
python src\perception\clear_landing_markers.py --object-regex ".*phase0[34].*marker.*"
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_landing_marker.py --object-name phase04_marker_offset_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector hsv
python src\perception\clear_landing_markers.py --object-regex ".*phase0[34].*marker.*"
python src\control\run_px4_land.py --confirm-send --timeout 45
```

Para cerrar la validacion lateral, repetir la misma secuencia cambiando el
nombre del objeto y el desplazamiento:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase04_marker_offset_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01
```

El criterio de aceptacion lateral es que `command_right_m_s` cambie de signo
cuando se invierte `offset-y`. En las corridas
`phase04_20260502_101337_acf15cca` y `phase04_20260502_102006_49f454f1` este
criterio quedo validado: el promedio de `command_right_m_s` cambio de
aproximadamente `+0.088` a `-0.089`.

Como ampliacion, se puede repetir el mismo procedimiento con `--offset-x 0.8` y
`--offset-x -0.8` para verificar el signo longitudinal de
`command_forward_m_s`.

## Prueba P04-V06C: marcador fiduciario ArUco

Esta prueba migra la entrada visual de color/contorno a un marcador fiduciario
ArUco. El marcador configurado por defecto es `DICT_4X4_50`, ID `23`.

Primero verificar que la dependencia de OpenCV incluya el modulo ArUco:

```powershell
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'aruco'))"
```

El segundo valor debe ser `True`. Si es `False`, reinstalar dependencias desde
`requirements.txt`.

Secuencia de validacion centrada:

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_center --under-vehicle --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06C_ARUCO_FIDUCIAL_DRY_RUN
python src\perception\clear_landing_markers.py
python src\control\run_px4_land.py --confirm-send --timeout 45
```

La validacion centrada quedo cerrada con el run
`phase04_20260502_154838_c02260b6`: 10/10 detecciones aceptadas,
`detector_method=aruco_fiducial`, `aruco_id=23`, `centered=True` y comandos
cercanos a cero en dry-run.

Criterios de aceptacion:

- `detected=True` y `accepted_detection=True` en la mayoria de muestras;
- `detector_method=aruco_fiducial` en el CSV;
- `detection_notes` contiene `aruco_id=23`;
- imagen anotada con centro del marcador y error visual;
- comandos cercanos a cero si el marcador esta centrado.

Luego repetir con desplazamiento lateral positivo y negativo para confirmar que
la migracion no cambio la convencion de signos:

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_offset_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06D_ARUCO_OFFSET_Y_POS
python src\perception\clear_landing_markers.py
```

Repetir cambiando a `--offset-y -0.8` y
`--object-name phase04_aruco_marker_offset_y_neg`. Al finalizar ambas corridas,
limpiar marcadores y aterrizar:

```powershell
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_offset_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06D_ARUCO_OFFSET_Y_NEG
```

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_land.py --confirm-send --timeout 45
```

Si el dry-run se ejecuta con el UAV en tierra y devuelve `detected=False`, la
camara inferior puede no estar viendo el marcador. Para repetir el dry-run con
altura real de PX4:

```powershell
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 20 --with-px4 --save-annotated --detector aruco
python src\control\run_px4_land.py --confirm-send
```

## Prueba P04-V07: correccion lateral activa con ArUco

Esta prueba cierra el lazo lateral de forma limitada, sin descenso. El UAV debe
estar elevado, el marcador ArUco debe generarse despues del despegue con un
desplazamiento lateral conocido, y el script debe enviar setpoints MAVLink
directos en `OFFBOARD` a partir del error visual. La velocidad horizontal se
limita por defecto a `0.12 m/s`.

Secuencia inicial recomendada con desplazamiento lateral positivo:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_active_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --save-annotated --max-horizontal-speed 0.12 --scenario-id P04_V07_ARUCO_ACTIVE_LATERAL_POS
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Si la telemetria inicial muestra `mode=OFFBOARD` o `mode=LAND` estando
desarmado y en tierra, recuperar primero:

```powershell
python src\control\run_mavlink_mode_recovery.py --confirm-send
python src\control\run_px4_telemetry_check.py --duration 5
```

Criterios de aceptacion:

- `offboard_start` con `flight_mode=OFFBOARD` y `status=ok`;
- muestras `visual_servo` con `command_sent=True`;
- detecciones ArUco aceptadas con `aruco_id=23`;
- `command_down_m_s=0.0` durante el lazo visual;
- `summary` con `accepted_count>0`;
- reduccion del error lateral absoluto (`last_abs_error_x < first_abs_error_x`)
  o evidencia visual/logica que explique la estabilizacion;
- aterrizaje final o recuperacion segura sin dejar PX4 en `OFFBOARD` desarmado.

Si el primer ensayo con `--offset-y 0.8` reduce el error lateral sin oscilacion,
repetir despues con `--offset-y -0.8` para confirmar simetria antes de avanzar
al descenso asistido.

La corrida `phase04_20260503_101736_206196b4` valido el primer ensayo
(`--offset-y 0.8`): 30/30 detecciones aceptadas, `command_down_m_s=0.0`,
altitud estable y reduccion de error lateral absoluto de `0.4154` a `0.1797`.

La corrida `phase04_20260503_102830_f0c4fefa` valido el segundo ensayo
(`--offset-y -0.8`): 30/30 detecciones aceptadas, `command_down_m_s=0.0`,
altitud estable y reduccion de error lateral absoluto de `0.4017` a `0.1905`.
Por tanto, P04-V07 queda validada en ambos sentidos.

Secuencia reproducible para el desplazamiento negativo:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_active_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --save-annotated --max-horizontal-speed 0.12 --scenario-id P04_V07_ARUCO_ACTIVE_LATERAL_NEG
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

## Prueba P04-V08: abort por marcador no aceptado

Esta prueba valida que el agente no siga corrigiendo ni intente descender cuando
la percepcion no entrega una deteccion aceptada. Para hacerla reproducible, se
genera un marcador ArUco visible pero con ID incorrecto (`24`) mientras el
detector espera el ID configurado (`23`). El resultado esperado es que el lazo
registre detecciones no aceptadas, supere el limite `--max-missing-detections`,
marque `status=abort` y ejecute `LAND`.

Secuencia recomendada:

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_wrong_id_abort --under-vehicle --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 24 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --save-annotated --max-horizontal-speed 0.12 --max-missing-detections 3 --scenario-id P04_V08_ARUCO_WRONG_ID_ABORT
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Criterios de aceptacion:

- `offboard_start` con `flight_mode=OFFBOARD` y `status=ok`;
- filas `visual_servo` con `accepted_detection=False`;
- notas de deteccion indicando que el ID esperado no esta presente o que no hay
  marcador aceptado;
- una fila `visual_servo` o `summary` con `status=abort`;
- `summary` con `aborted=True` y `accepted_count=0`;
- comandos horizontales y de descenso en cero durante el abort;
- aterrizaje final y recuperacion segura a `LOITER`, `armed=False`.

Resultado validado:

- `phase04_20260503_104002_62c3998b`: PX4 entro a `OFFBOARD`, el ArUco con ID
  `24` no fue aceptado por el detector configurado para ID `23`, se registraron
  cuatro detecciones no aceptadas, `accepted_count=0`, `aborted=True`,
  `status=abort` y comandos `forward/right/down` en cero. El ensayo cerro con
  `LAND` y recuperacion a `LOITER`, `armed=False`.

## Prueba P04-V09: descenso asistido piloto con ArUco

Solo despues de validar P04-V07 y la respuesta segura ante marcador no aceptado
en P04-V08, ejecutar un descenso piloto con marcador ArUco centrado. El descenso
se habilita de forma explicita con `--enable-descent`; antes de ello el lazo
mantiene `command_down_m_s=0.0`.

Nota de ajuste posterior a P04-V09A: con el marcador de escala `2.5 x 2.5 m`,
el detector se perdio al descender hasta aproximadamente `1.52 m` porque el
ArUco ocupaba demasiado campo visual y quedaba cerca de los bordes de la camara
inferior. Por tanto, la repeticion recomendada usa un marcador reducido y toma
`0.80 m` como umbral piloto de transicion a `LAND`.

```powershell
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_descent_reduced --under-vehicle --z 0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 25 --detector aruco --save-annotated --max-horizontal-speed 0.10 --max-missing-detections 3 --enable-descent --descent-rate 0.08 --centered-cycles-required 5 --landing-complete-altitude 0.80 --scenario-id P04_V09B_ARUCO_VISUAL_DESCENT_REDUCED_MARKER
python src\perception\clear_landing_markers.py
python src\control\run_px4_telemetry_check.py --duration 5
```

Criterios de aceptacion:

- `offboard_start` con `flight_mode=OFFBOARD`, `status=ok` y `MAV_RESULT_ACCEPTED`;
- detecciones ArUco aceptadas con `aruco_id=23`;
- `centered_cycles` alcanza el umbral configurado antes de iniciar descenso;
- al menos una fila `visual_servo` registra `command_down_m_s > 0.0` y
  `controller_reason=vision_descent`;
- la altitud disminuye de forma gradual sin perdida sostenida del marcador antes
  del umbral de transicion a `LAND`;
- el `summary` reporta `descent_started=True`, `landing_threshold_reached=True`
  y no reporta `aborted=True`;
- cierre con `LAND` y recuperacion a `LOITER`, `armed=False`.

Resultado validado:

- `phase04_20260503_110722_787b177f`: PX4 entro a `OFFBOARD` con `status=ok`;
  el lazo registro 97 muestras `visual_servo`, 96 detecciones aceptadas, 92
  ciclos con `command_down_m_s=0.08`, `descent_started=True`,
  `landing_threshold_reached=True`, `aborted=False` y reduccion de altitud de
  `2.2048 m` a `0.7884 m`. La unica deteccion perdida ocurrio al cruzar el
  umbral de `0.80 m`, sin superar `max_missing_detections=3`; el cierre fue
  `LAND` con recuperacion a `LOITER`, `armed=False`.

## Prueba P04-V10: repetibilidad piloto

Para dejar evidencia minima de repetibilidad, repetir dos corridas adicionales
con el mismo protocolo de P04-V09B. La corrida `phase04_20260503_110722_787b177f`
cuenta como primera corrida positiva de referencia.

La repeticion 2 quedo validada con `phase04_20260503_111811_e34f112f`: 81/81
detecciones aceptadas, 77 comandos de descenso, `landing_threshold_reached=True`,
`aborted=False` y cierre `LAND`/`LOITER`.

La repeticion 3 quedo validada con `phase04_20260503_112921_7c3ef4a8`: 79/80
detecciones aceptadas, 75 comandos de descenso, `landing_threshold_reached=True`,
`aborted=False` y cierre `LAND`/`LOITER`.

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

Criterios de aceptacion:

- cada corrida debe entrar a `OFFBOARD` con `status=ok`;
- `accepted_count` debe ser alto y no debe existir `aborted=True`;
- debe existir `descent_started=True` y `landing_threshold_reached=True`;
- el cierre final debe quedar en `LOITER`, `armed=False`;
- si una corrida falla por cierre de AirSimNH, reiniciar entorno y repetirla,
  documentando la incidencia aparte.

Estado final: P04-V10 queda aceptada con tres corridas positivas comparables:
P04-V09B, P04-V10-02 y P04-V10-03.

## Evidencias esperadas

Los logs se guardan en:

```text
data/logs/phase04_control/
```

Cada CSV debe incluir:

- `run_id`;
- `treatment`;
- `scenario_id`;
- metodo de detector;
- deteccion visual;
- error visual;
- comando calculado/enviado;
- telemetria PX4;
- estado del controlador;
- latencia;
- estado final.
