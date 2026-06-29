# Justificacion del uso de MAVLink para control activo

## Proposito

Esta nota sustenta la decision tecnica de evaluar MAVLink directo como ruta de
control activo en la Fase 04. La decision surge despues de validar percepcion
ArUco y signos laterales en `dry-run`, y despues de confirmar que el arranque
Offboard mediante MAVSDK/Python devuelve `NO_SETPOINT_SET` en la configuracion
actual PX4 SITL + AirSimNH + UDP 14601.

MAVSDK no se descarta como concepto: se reconoce como una API de alto nivel
basada en MAVLink. Sin embargo, al fallar especificamente el plugin Offboard de
MAVSDK, resulta metodologicamente valido diagnosticar el canal de menor nivel
con `pymavlink` para separar un problema de API de un problema real del
autopiloto, del canal MAVLink o de la configuracion PX4.

## Sustento tecnico en la literatura revisada

La literatura local del proyecto muestra que las arquitecturas de UAV autonomos
basados en vision suelen separar tres capas: percepcion en un computador
companero, generacion de referencias o comandos en una capa de decision, y
ejecucion estabilizada por el autopiloto. En esa separacion, MAVLink aparece
como protocolo recurrente para transmitir telemetria y comandos entre el agente
externo y el controlador de vuelo.

Aliane (2024) describe PX4 como un autopiloto abierto con soporte de
computadores companeros, comunicacion MAVLink y APIs de alto nivel como MAVSDK.
Esto respalda la arquitectura general del proyecto: mantener PX4 como controlador
de vuelo y ubicar el agente visual Python en una capa superior que envia
referencias al autopiloto.

Lukash y Prystavka (2025) presentan una plataforma de investigacion para
autonomia visual en UAV donde el analisis de video, el logging y el control
automatico se integran mediante MAVLink/MAVSDK hacia el controlador de vuelo. El
aporte es relevante porque la arquitectura sincroniza imagen, telemetria y
acciones de control, que es exactamente la necesidad experimental de la Fase 04.

Pulungan et al. (2024) muestran que Python puede emplearse sobre MAVLink,
mediante DroneKit, para operaciones autonomas de cuadricopteros. Aunque el
trabajo usa DroneKit y no `pymavlink`, aporta evidencia de que el uso de Python
como agente externo que transmite comandos por MAVLink es una practica aceptada
en prototipos UAV.

Ribayee et al. (2025) integran simulacion 3D, MAVProxy, DroneKit y MAVLink para
visualizar y controlar un UAV autonomo en SITL. Esta referencia es importante
para el proyecto porque muestra una ruta experimental cercana: simulacion,
protocolo MAVLink, Python y control en entorno seguro antes de pruebas reales.

Llerena Cana et al. (2022) usan PX4, MAVLink, MAVSDK y AirSim para un sistema de
aterrizaje multirrotor basado en vision. Un punto clave de ese trabajo es que no
modifican el controlador interno de PX4; en su lugar, usan el autopiloto y su
sistema de navegacion como capa estable, mientras la vision corrige la
referencia de aterrizaje. Esto justifica que, si el Offboard por setpoints no
queda validado, el proyecto pueda adoptar una variante basada en referencias de
posicion, waypoints o comandos de aterrizaje enviados por MAVLink.

Delbene et al. (2022) muestran una arquitectura de aterrizaje visual donde el
computador a bordo estima pose relativa y genera setpoints para el autopiloto,
que conserva la estabilizacion de bajo nivel. Esta separacion confirma que el
objetivo no es reemplazar PX4, sino alimentarlo con referencias visuales
trazables.

Keipour et al. (2022) proponen un controlador de servoing visual que genera
comandos de velocidad directamente desde el espacio imagen. Esta referencia
respalda el tipo de accion que se busca en la Fase 04: convertir el error visual
del marcador en comandos laterales y verticales, siempre con limites y
condiciones de seguridad.

Yang et al. (2024) usan PX4, MAVROS y MAVLink en un esquema de servoing visual
predictivo. Aunque el vehiculo es de ala fija, el trabajo refuerza que MAVLink y
sus interfaces asociadas son una capa comun para comunicar simulador, autopiloto
y algoritmo de control visual.

## Decision metodologica para la Fase 04

Con base en la evidencia experimental y bibliografica, la Fase 04 adopta la
siguiente decision:

1. Mantener PX4 como autopiloto responsable de estabilizacion, modos de vuelo y
   seguridad basica.
2. Mantener Python como agente de percepcion, decision y logging.
3. Usar MAVLink como protocolo de integracion para control activo en tiempo real.
4. Evaluar `pymavlink` como ruta directa de diagnostico y control cuando MAVSDK
   Offboard no registre setpoints.
5. Conservar MAVSDK para telemetria o acciones de alto nivel solo si no
   interfiere con el canal MAVLink directo.

Esta decision no cambia el objetivo de la fase; solo ajusta la ruta tecnica para
cumplirlo. El objetivo sigue siendo que la salida del modulo de percepcion
visual alimente una logica de control o aterrizaje autonomo validada de forma
segura y gradual.

## Verificacion experimental realizada

Para declarar MAVLink directo como ruta validada se ejecuto el diagnostico
P04-V02C con el script corregido:

```powershell
python src\control\run_mavlink_direct_offboard_diagnostic.py --confirm-send
```

La prueba se definio positiva si demostraba que:

- se recibe heartbeat por `pymavlink`;
- se envian setpoints `SET_POSITION_TARGET_LOCAL_NED`;
- PX4 responde al intento de modo `OFFBOARD` con un resultado interpretable;
- el fallo, si ocurre, ya no es un error local de empaquetado de Python.

PX4 acepto `OFFBOARD`, por lo que se avanzo al hover minimo con setpoint neutro
por MAVLink directo y luego a correccion visual activa.

La corrida `phase04_20260502_202237_55b4ea94` produjo una primera evidencia
favorable: PX4 respondio `MAV_RESULT_ACCEPTED` a la solicitud
`MAV_CMD_DO_SET_MODE` enviada por MAVLink directo despues de recibir setpoints.
El modo posterior fue reportado como `UNKNOWN`, por lo que se requiere una
repeticion con registro de heartbeat crudo antes de cerrar la validacion.

La repeticion `phase04_20260502_203009_822c9921` cerro esta verificacion:
`post_mode=OFFBOARD`, `px4_main_mode=6` y `MAV_RESULT_ACCEPTED`. Con ello,
MAVLink directo queda justificado no solo bibliograficamente, sino tambien como
ruta experimental viable en la configuracion local AirSimNH + PX4 SITL.

La viabilidad experimental se amplio con:

- `phase04_20260503_095523_1799a2c0`: hover minimo por MAVLink directo;
- `phase04_20260503_101736_206196b4` y
  `phase04_20260503_102830_f0c4fefa`: correccion lateral activa en ambos
  sentidos;
- `phase04_20260503_104002_62c3998b`: abort seguro por marcador no aceptado;
- `phase04_20260503_110722_787b177f`: descenso asistido piloto con ArUco
  reducido hasta `landing_threshold_reached=True`;
- `phase04_20260503_111811_e34f112f`: repeticion positiva del descenso
  asistido.
- `phase04_20260503_112921_7c3ef4a8`: tercera corrida positiva comparable del
  descenso asistido, con `landing_threshold_reached=True` y cierre
  `LAND`/`LOITER`.

## Referencias

Aliane, N. (2024). A survey of open-source UAV autopilots. *Electronics, 13*(23),
4785. https://doi.org/10.3390/electronics13234785

Delbene, A., Baglietto, M., & Simetti, E. (2022). Visual servoed autonomous
landing of an UAV on a catamaran in a marine environment. *Sensors, 22*(9),
3544. https://doi.org/10.3390/s22093544

Keipour, A., Pereira, G. A. S., Bonatti, R., Garg, R., Rastogi, P., Dubey, G., &
Scherer, S. (2022). Visual servoing approach to autonomous UAV landing on a
moving vehicle. *Sensors, 22*(17), 6549. https://doi.org/10.3390/s22176549

Llerena Cana, J. P., Garcia Herrero, J., & Molina Lopez, J. M. (2022). Error
reduction in vision-based multirotor landing system. *Sensors, 22*(10), 3625.
https://doi.org/10.3390/s22103625

Lukash, Y., & Prystavka, P. (2025). A research platform for vision-based UAV
autonomy: Architecture and implementation. In *Fourth International Conference
on Cyber Hygiene & Conflict Management in Global Information Networks*.

Pulungan, A. B., Putra, Z. Y., Sidiqi, A. R., Hamdani, & Parigalan, K. E.
(2024). Drone Kit-Python for autonomous quadcopter navigation. *International
Journal on Informatics Visualization*.

Ribayee, M. A. K., Anicho, O., & Secco, E. L. (2025). An approach to simulation
and navigation of autonomous unmanned aerial vehicle in 3D. *Drone Applications
and Vehicles*. https://doi.org/10.70322/dav.2025.10013

Yang, L., Wang, X., Zhou, Y., Liu, Z., & Shen, L. (2024). Online predictive
visual servo control for constrained target tracking of fixed-wing unmanned
aerial vehicles. *Drones, 8*(4), 136. https://doi.org/10.3390/drones8040136
