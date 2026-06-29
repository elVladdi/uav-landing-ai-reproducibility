# Diseño de Control Offboard y MAVLink Directo

## Decisión de enlace activo

El diseño inicial consideró MAVSDK Offboard como API de alto nivel para enviar
setpoints. Las pruebas P04-V02B/P04-V03 mostraron que, en la configuración local
PX4 SITL + AirSimNH + UDP 14601, `offboard.start()` devolvia
`NO_SETPOINT_SET` aun después de primar varias familias de setpoints. Para no
confundir una limitación de API con una imposibilidad del autopiloto, se evaluó
MAVLink directo con `pymavlink`.

La ruta activa validada de Fase 04 es:

```text
Percepción ArUco -> controlador visual -> velocidad cuerpo
-> conversión a LOCAL_NED con yaw PX4 -> SET_POSITION_TARGET_LOCAL_NED
-> PX4 OFFBOARD -> AirSimNH
```

### Figura del lazo cerrado

![Lazo cerrado de control visual con ArUco y MAVLink directo](<Figuras/Lazo cerrado de control visual con ArUco y MAVLink directo.png>)

*Figura 7. Flujo validado de percepción ArUco, controlador visual, conversión a `LOCAL_NED`, envío de setpoints por MAVLink directo y realimentación de telemetría PX4.*

MAVSDK queda documentado como ruta inicial, diagnóstico y posible capa de
telemetría/acciones. Los ensayos activos validados de corrección lateral y
descenso asistido usan setpoints MAVLink directos.

## Entradas

El agente usa dos entradas principales:

- percepción visual desde `bottom_center`;
- telemetría PX4 en coordenadas NED.

La percepción entrega `error_x_norm`, `error_y_norm`, `confidence`,
`detected` y `method`. PX4 entrega modo de vuelo, armado, posición local,
velocidad local y estado de salud.

Para las pruebas nuevas de Fase 04, la fuente visual recomendada es el detector
fiduciario ArUco (`aruco_fiducial`). El detector HSV/contornos queda disponible
como respaldo y para reproducir la evidencia historica de Fase 03.

## Salida de control

La salida lógica del controlador visual es un comando de velocidad en cuerpo:

```text
forward_m_s
right_m_s
down_m_s
yawspeed_deg_s
```

En la ruta validada, ese comando no se envía como MAVSDK
`VelocityBodyYawspeed`. El script activo convierte `forward_m_s` y `right_m_s`
al marco local NED usando el yaw reportado por PX4 y transmite
`SET_POSITION_TARGET_LOCAL_NED` mediante `pymavlink`. `down_m_s` se usa solo
cuando el descenso se habilita explícitamente con `--enable-descent`.

Los comandos están saturados por `configs/control_config.json` y por los límites
adicionales de cada script piloto.

## Mapeo visual inicial

El controlador visual está en:

```text
src/control/visual_servo_controller.py
```

La configuración de signos está en:

```json
"forward_error_sign": -1.0,
"right_error_sign": 1.0
```

Estos signos deben verificarse antes de cerrar el lazo. La prueba correcta es
ejecutar `run_visual_servo_dry_run.py`, observar el marcador desplazado en la
imagen y confirmar que el comando calculado empuja el UAV hacia el centro de la
plataforma.

En la validación piloto P04-V06B se verificó el signo lateral con el marcador
HSV desplazado en ambos sentidos sobre el eje `Y` de AirSimNH. Posteriormente,
en P04-V06D se repitió la misma verificación con marcador fiduciario ArUco
(`DICT_4X4_50`, ID `23`). En ambos casos, los resultados confirmaron que
`command_right_m_s` cambia de signo de forma coherente al invertir
`--offset-y`. La verificacion equivalente sobre `--offset-x` queda como
ampliacion si se requiere cerrar tambien el signo longitudinal antes del ensayo
con comandos activos.

## Máquina de estados

La lógica de aterrizaje piloto está en:

```text
src/control/landing_state_machine.py
src/control/run_mavlink_visual_servo_test.py
```

Estados:

| Estado | Función |
| --- | --- |
| `align` | Corrige desplazamiento lateral sin descender |
| `descend` | Desciende solo si el marcador permanece centrado |
| `land` | Ordena aterrizaje cuando se alcanza baja altura |
| `abort` | Interrumpe por pérdida de marcador, timeout o condición insegura |
### Figura de máquina de estados

![Maquina de estados del aterrizaje visual asistido](<Figuras/Máquina de estados del aterrizaje visual asistido.png>)

*Figura 8. Máquina de estados del ensayo piloto de aterrizaje visual asistido, con estados `align`, `descend`, `land` y `abort`.*


En la implementación validada, `run_mavlink_visual_servo_test.py` ejecuta esta
lógica de forma explícita: primero corrige/alinea, luego activa descenso tras
varios ciclos centrados, marca `landing_ready` al alcanzar el umbral piloto y
finalmente solicita `LAND`/`LOITER`.

## Seguridad

Los scripts que envian comandos requieren:

```powershell
--confirm-send
```

Si no se pasa esa bandera, el script se detiene antes de armar, despegar o
enviar setpoints.

Reglas adicionales:

- no ejecutar MAVSDK y `pymavlink` simultáneamente sobre UDP 14601;
- no generar el marcador antes del despegue, para evitar interferencia fisica o
  visual;
- mantener `command_down_m_s=0.0` en las pruebas de correccion lateral;
- habilitar descenso solo con `--enable-descent`;
- abortar y aterrizar si se supera el máximo de detecciones perdidas.

## Variables configurables

Archivo:

```text
configs/control_config.json
```

Parámetros principales:

- frecuencia de control;
- altura de despegue;
- velocidad máxima lateral;
- velocidad máxima de descenso;
- confianza mínima de detección;
- tolerancia de centrado;
- ciclos centrados requeridos;
- máximo de detecciones perdidas;
- acción de abort.
