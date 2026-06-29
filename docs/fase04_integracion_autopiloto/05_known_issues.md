# Incidencias y Riesgos - Fase 04

## KI-0401: Signos de control no calibrados

**Estado:** validado lateralmente en dry-run HSV y ArUco.

El error visual no garantiza por sí solo la dirección correcta del movimiento
en cuerpo. Antes de enviar comandos laterales se debe ejecutar dry-run y
confirmar que los signos configurados acercan el marcador al centro.

Medida:

- usar `run_visual_servo_dry_run.py`;
- revisar `forward_error_sign` y `right_error_sign`;
- probar desplazamientos pequeños antes del descenso.
- conservar la validación ArUco en ambos sentidos antes de enviar comandos
  activos.

## KI-0402: Offboard requiere setpoints continuos

**Estado:** limitación confirmada en la configuración actual.

PX4 Offboard requiere flujo continuo de setpoints. Si el flujo se interrumpe,
PX4 puede activar failsafe.

Durante las primeras pruebas P04-V03 se observó `NO_SETPOINT_SET` al iniciar
Offboard. Esto indica que PX4/MAVSDK no acepto el setpoint inicial como valido
antes de `offboard.start()`. También se observó que PX4 seguía en `TAKEOFF` y
aún no había alcanzado la altura objetivo cuando se intentó activar Offboard.
En intentos posteriores con el UAV ya estabilizado en `HOLD` a unos 2.0 m, el
error persistio incluso al primar con setpoints NED locales, por lo que la
incidencia queda acotada al arranque Offboard por MAVSDK en esta configuracion.
El diagnostico en tierra `phase04_20260502_171849_0ebbbb3a` confirmo el mismo
resultado para `position_ned`, `velocity_ned`, `position_velocity_ned` y
`velocity_body`.

Medida:

- mantener frecuencia de control mayor a 2 Hz;
- esperar altura suficiente despues de `takeoff`;
- iniciar Offboard con varios setpoints de posicion NED actual antes de `start()`;
- registrar eventos de stop/abort;
- probar primero hover;
- si `NO_SETPOINT_SET` persiste con posicion local valida y altura estable,
  ejecutar `run_offboard_start_diagnostic.py` en tierra para separar registro
  de setpoint MAVSDK de rechazo de modo PX4;
- tratar P04-V03 como limitacion tecnica y no avanzar a comandos activos si el
  diagnostico devuelve `NO_SETPOINT_SET` para todas las estrategias.
- no repetir P04-V03 en vuelo sin cambiar primero la estrategia tecnica
  (version/libreria MAVSDK, canal MAVLink, o envio de setpoints por otra capa).

## KI-0403: Perdida o falso positivo del marcador

**Estado:** mitigado parcialmente por migración a ArUco.

AirSimNH puede contener texturas que produzcan falsos positivos HSV. Una
detección incorrecta no debe generar descenso.

Medida:

- exigir confianza minima;
- exigir centrado durante varios ciclos;
- abortar por detecciones perdidas;
- revisar imagen anotada si hay dudas.
- para las pruebas nuevas, usar marcador fiduciario ArUco con ID esperado
  (`DICT_4X4_50`, ID `23`) y registrar `detector_method`.

## KI-0404: IP y puertos WSL2 variables

**Estado:** controlado por documentacion.

La conexion PX4/AirSim/MAVSDK depende de IPs y puertos. Si WSL2 cambia IP, el
canal MAVLink puede fallar.

Medida:

- validar `scripts/check_px4_connection.ps1`;
- mantener `configs/px4_airsim.env`;
- recrear el canal MAVLink dedicado si es necesario.

## KI-0405: Uso indebido de sim_pose

**Estado:** control metodologico.

`sim_pose` fue valido en Fase 03 para posicionar la escena y validar
percepcion. En Fase 04 no debe usarse como control autonomo.

Medida:

- documentar cualquier uso de `sim_pose` como diagnostico visual;
- no incluir `sim_pose` en evidencias de control ni aterrizaje autonomo.

## KI-0406: Despegue PX4 no alcanza 3 m dentro del timeout inicial

**Estado:** observado.

Durante P04-V03, el despegue hacia 3 m no alcanzo el umbral interno de 2.4 m
dentro del timeout configurado. La ultima altura registrada fue
aproximadamente 1.84 m.

Medida:

- usar una altura piloto menor para pruebas iniciales, por ejemplo
  `--takeoff-altitude 2.0`, que queda como valor piloto por defecto de Fase 04;
- aceptar temporalmente una altura minima de 1.0 m o 55% de la altura objetivo
  para iniciar pruebas piloto de Offboard;
- confirmar aterrizaje completo antes de repetir una prueba;
- ampliar el timeout de espera de despegue a 45 s;
- aceptar P04-V03 solo cuando el script entre al loop de hover y registre
  muestras con `command_sent=True`.

## KI-0407: PX4 queda en LAND y rechaza armado

**Estado:** observado.

Despues de enviar `land` con el UAV ya en tierra y desarmado, PX4 puede quedar
temporalmente en modo `LAND`. En ese estado, una llamada posterior a `arm()`
puede ser rechazada con `COMMAND_DENIED`.

Medida:

- no enviar `land` si el vehiculo ya esta en tierra y desarmado;
- solicitar `HOLD` como recuperacion si PX4 queda en `LAND`;
- si `HOLD` tambien es rechazado, reiniciar PX4/AirSimNH antes de repetir.

## KI-0408: Marcador generado puede interferir con la observacion del despegue

**Estado:** confirmado inicialmente.

El marcador usado en Fase 03 se genera como un objeto 3D (`Cube` o equivalente)
con escala grande y textura. Aunque se crea con `physics_enabled=False`, puede
mantener colision de malla o cubrir visualmente la zona de despegue. Durante las
pruebas P04-V02 se observo que PX4 y AirSim reportaban movimiento vertical, pero
el observador no percibia claramente la elevacion cuando el marcador grande
estaba bajo el UAV. Al limpiar el marcador y repetir P04-V02, el UAV alcanzo
aproximadamente 2 m y el usuario confirmo visualmente la elevacion.

Medida:

- repetir P04-V02 sin marcador generado para aislar la causa;
- borrar objetos de marcador con `src/perception/clear_landing_markers.py`;
- generar la plataforma despues del despegue para dry-run de percepcion;
- limpiar el marcador antes de aterrizar si queda debajo del UAV;
- usar un marcador con menor escala/espesor para futuras pruebas;
- documentar si el marcador se mantiene como objeto 3D o se reemplaza por una
  textura/plataforma no obstructiva.

## KI-0409: Dependencia ArUco requiere OpenCV contrib

**Estado:** riesgo controlado por configuracion.

El detector fiduciario usa `cv2.aruco`, que no siempre esta disponible cuando
se instala `opencv-python` basico. Si el modulo no existe, la deteccion ArUco no
puede ejecutarse.

Medida:

- usar `opencv-contrib-python` en `requirements.txt`;
- verificar `hasattr(cv2, "aruco")` dentro de `.venv`;
- no mezclar instalaciones simultaneas de `opencv-python` y
  `opencv-contrib-python`.

## KI-0410: Marcador fiduciario debe generarse despues del despegue

**Estado:** riesgo conocido.

Aunque el marcador ArUco es visualmente mas formal, sigue generandose como un
objeto 3D plano dentro de AirSim. Por tanto, conserva el riesgo de interferir
con el despegue si se coloca bajo el UAV antes de armar.

Medida:

- despegar primero con PX4;
- generar el marcador con `spawn_fiducial_marker.py --under-vehicle`;
- ejecutar `dry-run`;
- limpiar el marcador antes de aterrizar.

## KI-0411: Timeout de telemetria despues de comando LAND

**Estado:** observado y mitigado en helper.

Durante la validacion P04-V06D con ArUco desplazado negativo, el helper
`run_px4_land.py` envio correctamente el comando `land` y PX4 reporto
`mode=LAND` con altura aproximada de `0.42 m`. Despues de ese punto, MAVSDK
produjo un timeout al leer un stream de telemetria, lo que genero un traceback
en consola. La incidencia ocurre despues de la validacion visual y no afecta el
resultado del signo lateral.

Medida:

- capturar explicitamente `asyncio.TimeoutError` al leer telemetria;
- tratar muestras incompletas durante aterrizaje como espera, no como crash;
- confirmar estado final con `run_px4_telemetry_check.py` si el helper reporta
  telemetria incompleta.

## KI-0412: Cierre inesperado de AirSimNH durante recuperacion Offboard

**Estado:** observado.

Durante el intento P04-V03 `phase04_20260502_165235_e10bc1e2`, AirSimNH se
cerro inesperadamente despues de fallar `offboard.start()` con
`NO_SETPOINT_SET` y durante la fase de recuperacion/aterrizaje. El CSV muestra
que antes del fallo PX4 habia alcanzado aproximadamente 2.0 m, con
`armed=True`, `flight_mode=HOLD` y posicion local valida.

Medida:

- reiniciar AirSimNH y PX4 SITL despues de un cierre inesperado del simulador;
- no repetir Offboard sobre una sesion parcialmente recuperada;
- conservar el run como fallo controlado de P04-V03;
- continuar las pruebas de percepcion y dry-run solo despues de validar
  telemetria en tierra con `run_px4_telemetry_check.py`.

## KI-0413: Perdida de enlace simulador-PX4 durante telemetria

**Estado:** observado.

Durante la telemetria `phase04_20260502_171144_c8e2b45a`, AirSimNH se cerro
inesperadamente incluso sin enviar comandos de control. PX4 mostro mensajes
`simulator_mavlink poll timeout`, y el CSV paso de una muestra normal
(`mode=HOLD`, `armed=False`, altitud cercana a 0.0 m) a una muestra con
telemetria incompleta (`flight_mode` y posicion NED vacios).

Medida:

- no continuar con diagnosticos Offboard si aparece `simulator_mavlink poll timeout`;
- reiniciar AirSimNH y PX4 SITL desde cero;
- validar primero una telemetria de 5 s con todas las muestras completas;
- registrar muestras incompletas como `status=warning`, no como validacion
  positiva.

## KI-0414: Empaquetado incorrecto de modo PX4 en pymavlink

**Estado:** resuelto y validado experimentalmente.

Durante los primeros intentos P04-V02C con MAVLink directo, `pymavlink` recibio
heartbeat correctamente, pero el script fallo al solicitar `OFFBOARD`. La causa
fue local: `master.mode_mapping()["OFFBOARD"]` devuelve una tupla PX4 con
`base_mode`, `custom_mode` y `custom_sub_mode`, y el script la estaba pasando
como un unico argumento a `master.set_mode(...)`. Esto produjo
`struct.error: required argument is not a float`.

Medida aplicada:

- desempaquetar la tupla PX4 antes de llamar a `master.set_mode(...)`;
- repetir `run_mavlink_direct_offboard_diagnostic.py --confirm-send`;
- aceptar o rechazar P04-V02C solo con el resultado posterior a la correccion.

Resolucion:

- La correccion permitio ejecutar nuevamente P04-V02C. La corrida
  `phase04_20260502_203009_822c9921` envio setpoints MAVLink directos antes y
  despues de solicitar `OFFBOARD`; PX4 respondio
  `MAV_CMD_DO_SET_MODE:MAV_RESULT_ACCEPTED` y el heartbeat posterior reporto
  `post_mode=OFFBOARD`, `custom_mode=393216`, `px4_main_mode=6` y
  `px4_sub_mode=0`. Con ello, el error de empaquetado queda cerrado y P04-V02C
  queda validado como ruta viable de setpoints Offboard por MAVLink directo.

## KI-0415: Modo PX4 aceptado por MAVLink pero reportado como UNKNOWN

**Estado:** resuelto en diagnostico.

En la corrida `phase04_20260502_202237_55b4ea94`, PX4 respondio
`MAV_RESULT_ACCEPTED` al comando `MAV_CMD_DO_SET_MODE` para solicitar
`OFFBOARD`, despues de recibir setpoints MAVLink directos. Sin embargo, la
lectura textual posterior de `pymavlink` reporto `post_mode=UNKNOWN`.

Esto no equivale a `NO_SETPOINT_SET`: el comando fue aceptado por PX4. La duda
en ese momento era si `UNKNOWN` correspondia a una limitacion de decodificacion
de `pymavlink` o a que PX4 no se sostuvo en Offboard despues de la solicitud.

Medida:

- registrar campos crudos del heartbeat: `base_mode`, `custom_mode`,
  `px4_main_mode` y `px4_sub_mode`;
- continuar enviando setpoints despues de solicitar el modo;
- aceptar MAVLink directo como ruta de setpoints solo si el modo se decodifica
  como `OFFBOARD` o si `px4_main_mode=6`;
- si el `COMMAND_ACK` sigue siendo aceptado pero el modo no queda en Offboard,
  evaluar una estrategia MAVLink basada en referencias de posicion/waypoints o
  comando `LAND` asistido por vision.

Resolucion:

- La corrida `phase04_20260502_203009_822c9921` resolvio la duda: el heartbeat
  posterior reporto `post_mode=OFFBOARD` y `px4_main_mode=6`. Por tanto,
  `UNKNOWN` fue una condicion transitoria o de lectura insuficiente, no una
  invalidacion del canal MAVLink directo.

## KI-0416: Hover MAVLink directo debe iniciar con UAV ya elevado

**Estado:** riesgo controlado por precheck.

El nuevo ensayo P04-V03B no arma ni despega. Si se ejecuta en tierra, no valida
hover y puede dejar una interpretacion experimental incorrecta. El objetivo de
P04-V03B es aislar el control Offboard por MAVLink directo usando una posicion
local ya estable.

Medida:

- ejecutar primero `run_px4_takeoff_land_test.py --no-land-after`;
- exigir `armed=True` y altitud minima de `0.8 m`;
- abortar si no hay `LOCAL_POSITION_NED`;
- solicitar `LAND` al finalizar por defecto.

## KI-0417: Confirmacion tardia de OFFBOARD en P04-V03B

**Estado:** resuelto en P04-V03B.

En `phase04_20260502_204145_87918081`, PX4 acepto el comando de modo
`OFFBOARD` por MAVLink directo y una fila posterior registro
`flight_mode=OFFBOARD` con `px4_main_mode=6`. Sin embargo, el script esperaba un
heartbeat inmediato durante la fila `offboard_start`; al no recibirlo dentro de
la ventana corta, marco error y solicito `LAND` antes de registrar muestras de
hover.

Medida:

- conservar el intento como avance parcial, no como hover validado;
- ampliar `--mode-timeout` por defecto a 5 s;
- agregar una ventana `--heartbeat-grace` antes de declarar fallo;
- repetir P04-V03B y aceptar solo si hay muestras `hover` con
  `flight_mode=OFFBOARD` y `status=ok`.

Resolucion:

- La repeticion `phase04_20260503_095523_1799a2c0` valido el criterio:
  `offboard_start` quedo en `OFFBOARD` con `status=ok`, se registraron cinco
  muestras `hover` sostenidas en `OFFBOARD` a aproximadamente 2.0 m y el
  aterrizaje finalizo con recuperacion a `LOITER`.

## KI-0418: PX4 queda en OFFBOARD desarmado y rechaza armado posterior

**Estado:** mitigado; recuperacion validada.

Despues del intento P04-V03B parcial, PX4 quedo reportando `OFFBOARD` estando
desarmado y en tierra. Al intentar repetir P04-V02 con `run_px4_takeoff_land_test.py`,
el comando `arm()` fue rechazado con `COMMAND_DENIED`. Este estado es residual
del ensayo Offboard y no representa una falla de despegue de PX4.

Medida:

- si `run_px4_telemetry_check.py` reporta `mode=OFFBOARD`, `armed=False` y
  `alt=0.0`, ejecutar:

```powershell
python src\control\run_mavlink_mode_recovery.py --confirm-send
```

- confirmar luego que la telemetria sale de `OFFBOARD`;
- `prepare_for_arm()` ahora intenta recuperarse automaticamente de `LAND` u
  `OFFBOARD` si el UAV esta desarmado y en tierra;
- el helper `run_px4_land.py` tambien intenta recuperacion desde `OFFBOARD`;
- el hover MAVLink directo monitorea el aterrizaje y solicita `LOITER` al quedar
  en tierra para evitar repetir este estado residual.

Resolucion:

- La corrida `phase04_20260503_095351_8516dc78` valido el helper
  `run_mavlink_mode_recovery.py`: PX4 acepto `LOITER` con
  `MAV_RESULT_ACCEPTED`, quedo desarmado en tierra y permitio ejecutar luego el
  despegue `phase04_20260503_095441_325bf1b6`.
- La corrida `phase04_20260503_095523_1799a2c0` comprobo que, despues del hover
  MAVLink directo, el aterrizaje puede cerrar en `LOITER`, `armed=False`,
  `altitude_m=0.0`, sin dejar nuevamente a PX4 bloqueado en `OFFBOARD`.

## KI-0419: Correccion lateral activa puede oscilar o aumentar el error

**Estado:** mitigado y validado en ambos sentidos.

Aunque los signos laterales fueron validados en `dry-run`, cerrar el lazo con
comandos reales puede introducir retardo, sobrecorreccion u oscilacion. La
primera prueba activa no debe incluir descenso ni velocidades altas.

Medida:

- limitar la velocidad horizontal inicial a `0.12 m/s`;
- mantener `command_down_m_s=0.0` durante P04-V07;
- usar ArUco desplazado despues del despegue, no antes;
- aceptar la corrida solo si el error lateral absoluto disminuye o se estabiliza
  de forma explicable;
- aterrizar o abortar si se pierden detecciones durante mas de los ciclos
  configurados;
- no ejecutar descenso asistido hasta validar al menos una correccion lateral
  activa segura.

Resolucion parcial:

- La corrida `phase04_20260503_101736_206196b4` valido la correccion lateral
  activa con ArUco desplazado positivo. El error lateral absoluto disminuyo de
  `0.4154` a `0.1797` mientras `command_down_m_s` permanecio en `0.0`, con
  30/30 detecciones aceptadas y cierre seguro por `LAND`/`LOITER`.
- La corrida `phase04_20260503_102830_f0c4fefa` valido la simetria con ArUco
  desplazado negativo. El error lateral absoluto disminuyo de `0.4017` a
  `0.1905`, `command_right_m_s` fue negativo y `command_down_m_s` se mantuvo en
  `0.0`.
- La corrida `phase04_20260503_104002_62c3998b` valido el control de seguridad
  P04-V08 con ArUco de ID incorrecto. El lazo entro a `OFFBOARD`, mantuvo
  comandos `forward/right/down` en cero, supero el limite de detecciones no
  aceptadas, marco `status=abort`, ejecuto `LAND` y recupero `LOITER`.
- Con P04-V08 validada, el siguiente riesgo a controlar es el descenso asistido
  P04-V09, que debe iniciar con velocidad vertical baja y marcador centrado.

## KI-0420 - Perdida de ArUco durante descenso por tamano aparente excesivo

Estado: mitigado experimentalmente.

Descripcion:

En P04-V09A (`phase04_20260503_105624_4ddee5b7`) el descenso visual se inicio
correctamente y mantuvo `command_down_m_s=0.08` durante 42 muestras, pero el
marcador ArUco de escala `2.5 x 2.5 m` dejo de detectarse alrededor de `1.52 m`.
Las imagenes anotadas muestran que el patron ocupaba demasiado campo visual y
quedaba cerca de los bordes de la camara inferior. El sistema respondio de forma
segura: cancelo el descenso, envio comandos cero, marco `abort` y aterrizo.

Medida:

- repetir P04-V09 con marcador reducido (`scale-x=1.2`, `scale-y=1.2`);
- usar `landing_complete_altitude=0.80` como umbral piloto de transicion a
  `LAND`, no como metrica final de precision;
- conservar las imagenes anotadas de P04-V09A como evidencia de la causa
  tecnica de la perdida de deteccion.

Resolucion:

- La corrida `phase04_20260503_110722_787b177f` valido la mitigacion: con ArUco
  reducido se mantuvieron 96 detecciones aceptadas de 97 muestras visuales, se
  enviaron 92 comandos de descenso (`command_down_m_s=0.08`), se alcanzo
  `landing_threshold_reached=True` a `0.7884 m` y el sistema cerro con
  `LAND`/`LOITER` sin `abort`.
- La mitigacion se repitio positivamente en `phase04_20260503_111811_e34f112f`
  y `phase04_20260503_112921_7c3ef4a8`, cerrando P04-V10 con tres corridas
  comparables.
