# Subfase Tecnica - Alternativas de Control Activo

## Motivo

El objetivo del proyecto requiere que el agente Python pueda transformar la
salida visual en comandos de control reales hacia el UAV. La validacion de
percepcion, telemetria, despegue/aterrizaje PX4 y visual-servo en `dry-run`
quedo avanzada; sin embargo, el arranque Offboard mediante MAVSDK no fue
validado.

El diagnostico P04-V02B confirmo que `offboard.start()` devuelve
`NO_SETPOINT_SET` para las estrategias `position_ned`, `velocity_ned`,
`position_velocity_ned` y `velocity_body`. Esto impide cerrar el lazo de control
activo con MAVSDK Offboard en la configuracion actual.

## Pregunta tecnica

Determinar si el bloqueo pertenece a:

- el plugin Offboard de MAVSDK/Python;
- la version actual de MAVSDK (`3.15.3`);
- el canal MAVLink dedicado `UDP 14601`;
- parametros/modos PX4;
- o una limitacion de la integracion PX4 SITL + AirSimNH en esta sesion.

## Alternativas

### A. MAVSDK con otro canal o version

Probar una version distinta de MAVSDK o un canal MAVLink alternativo, sin
modificar la arquitectura conceptual. Esta opcion conserva la API de alto nivel,
pero puede consumir tiempo en compatibilidades.

### B. MAVLink directo con pymavlink

Enviar setpoints MAVLink directos (`SET_POSITION_TARGET_LOCAL_NED`) y solicitar
modo `OFFBOARD` sin pasar por el plugin Offboard de MAVSDK. Esta opcion permite
diagnosticar si PX4 acepta setpoints por MAVLink aunque MAVSDK no los registre.

Script inicial:

```powershell
python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send
```

Este script no arma ni despega. Solo envia setpoints de velocidad cero y solicita
`OFFBOARD` en tierra para observar si PX4 cambia de modo, rechaza el modo o no
responde.

### C. Mantener MAVSDK para acciones y usar MAVLink directo para setpoints

Usar MAVSDK para telemetria, armado, despegue y aterrizaje, pero usar pymavlink
para setpoints de control activo. Esta opcion conserva parte del trabajo actual
y aisla el problema al envio de setpoints.

## Criterio de avance

No se debe intentar correccion lateral activa ni descenso asistido hasta obtener
una de estas evidencias:

- Offboard inicia correctamente y registra setpoints con `command_sent=True`;
- o MAVLink directo confirma cambio a `OFFBOARD` o rechazo distinto a
  `NO_SETPOINT_SET`, demostrando que los setpoints llegan a PX4.

## Nota metodologica

Esta subfase no cambia el objetivo de la Fase 04. Solo cambia la ruta tecnica
para cumplir el mismo requisito: que el agente visual pueda enviar comandos de
control al autopiloto de forma trazable y segura.

## Decision provisional

La ruta recomendada pasa a ser **MAVLink directo con pymavlink** como siguiente
verificacion tecnica. La razon es doble:

- experimentalmente, MAVSDK Offboard ya devolvio `NO_SETPOINT_SET` en todas las
  estrategias probadas;
- bibliograficamente, la literatura revisada usa MAVLink, MAVSDK, DroneKit,
  MAVROS o interfaces equivalentes para comunicar computador companero,
  telemetria, referencias visuales y autopiloto.

El sustento academico se documenta en:

```text
docs/fase04_integracion_autopiloto/12_justificacion_control_activo_mavlink.md
```

### Figura de decision tecnica

![Decision tecnica para el control activo: de MAVSDK Offboard a MAVLink directo](<Figuras/Decisión técnica para el control activo - de MAVSDK Offboard a MAVLink directo.png>)

*Figura: decision tecnica que descarta MAVSDK Offboard como ruta activa en esta configuracion y valida MAVLink directo con `pymavlink` para setpoints activos.*

## Nota sobre P04-V02C

Los primeros intentos P04-V02C recibieron heartbeat por `pymavlink`, pero
fallaron antes de completar la solicitud de modo porque el script enviaba la
tupla PX4 completa de `OFFBOARD` como un unico parametro. Se corrigio
`run_mavlink_direct_offboard_diagnostic.py` para desempaquetar
`base_mode`, `custom_mode` y `custom_sub_mode` antes de llamar a
`master.set_mode(...)`.

Por tanto, esos intentos no invalidan MAVLink directo; solo registran un error
local de implementacion ya corregido.

La repeticion posterior `phase04_20260502_202237_55b4ea94` ya no presento ese
error y obtuvo `MAV_RESULT_ACCEPTED` para `MAV_CMD_DO_SET_MODE`, despues de
enviar setpoints MAVLink directos. Esto confirma una diferencia importante
respecto a MAVSDK Offboard: el canal MAVLink directo si llega a PX4 y PX4 acepta
la solicitud de modo. Como el heartbeat posterior fue traducido por `pymavlink`
como `UNKNOWN`, se amplio el diagnostico para registrar los campos crudos del
modo PX4 y sostener setpoints despues de la solicitud.

La corrida `phase04_20260502_203009_822c9921` cerro la verificacion: el modo
posterior fue `OFFBOARD`, con `px4_main_mode=6`, y el comando fue aceptado por
PX4. Por tanto, la alternativa B queda seleccionada para el siguiente escalon:
hover minimo por MAVLink directo (`P04-V03B`).

La corrida `phase04_20260503_095523_1799a2c0` valido ese siguiente escalon:
con el UAV previamente elevado a aproximadamente 2.0 m, PX4 acepto `OFFBOARD`,
registro muestras sostenidas de hover con `status=ok` y aterrizo con
recuperacion final a `LOITER`. Por tanto, la subfase tecnica selecciona
formalmente **MAVLink directo con pymavlink** como ruta activa para el siguiente
paso experimental: correccion lateral limitada basada en error visual.

Script seleccionado para ese paso:

```powershell
python src\control\run_mavlink_visual_servo_test.py --confirm-send --duration 6 --detector aruco --max-horizontal-speed 0.12
```

La prueba P04-V07 debe mantenerse sin descenso. Su objetivo no es aterrizar,
sino demostrar que la salida de percepcion ArUco puede convertirse en comandos
MAVLink activos que reducen el error lateral bajo limites de seguridad.

La corrida `phase04_20260503_101736_206196b4` valido esta capacidad para un
desplazamiento positivo (`--offset-y 0.8`): el error lateral absoluto disminuyo
aproximadamente 56.7%, no se envio descenso y el cierre fue seguro. La subfase
quedo reforzada con `phase04_20260503_102830_f0c4fefa`, donde el desplazamiento
negativo (`--offset-y -0.8`) redujo el error lateral absoluto aproximadamente
52.6%, con comando lateral de signo contrario y sin descenso.

Con ambos sentidos validados, MAVLink directo queda seleccionado como ruta
activa para la integracion percepcion-control. La respuesta segura ante marcador
no aceptado tambien quedo validada con `phase04_20260503_104002_62c3998b`
(`P04-V08`): el sistema entro a `OFFBOARD`, mantuvo comandos cero, aborto por
perdida de deteccion aceptada y cerro con `LAND`/`LOITER`.

El siguiente escalon es P04-V09: usar el mismo canal MAVLink directo para un
descenso asistido piloto con ArUco centrado, habilitando la velocidad vertical
solo con `--enable-descent`.

La primera corrida P04-V09A (`phase04_20260503_105624_4ddee5b7`) confirmo que
el canal MAVLink directo puede iniciar descenso asistido por vision
(`command_down_m_s=0.08`) con el marcador centrado, pero no cerro la validacion
porque el ArUco de escala `2.5 x 2.5 m` se perdio al aproximarse a `1.52 m`.
La repeticion P04-V09B debe usar marcador reducido y umbral piloto de transicion
a `LAND`.

La corrida P04-V09B (`phase04_20260503_110722_787b177f`) valido esa repeticion:
con marcador reducido, el lazo alcanzo `landing_threshold_reached=True`, no
registro `abort`, mantuvo 92 comandos de descenso y cerro con `LAND`/`LOITER`.
Por tanto, la subfase de alternativa MAVLink directo queda tecnicamente
cerrada como ruta activa para Fase 04; resta solo repetir el ensayo para
repetibilidad piloto (`P04-V10`).

La repeticion `phase04_20260503_111811_e34f112f` confirmo el mismo patron de
exito: 81/81 detecciones aceptadas, 77 comandos de descenso, llegada al umbral
piloto y cierre seguro.

La repeticion `phase04_20260503_112921_7c3ef4a8` completo P04-V10 con tres
corridas positivas comparables. Por tanto, la subfase de control activo queda
cerrada: MAVLink directo con `pymavlink` es la ruta seleccionada y validada para
los setpoints activos de Fase 04.
