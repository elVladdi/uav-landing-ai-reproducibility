# Fase 04 - Objetivo y Alcance

## Proposito

La Fase 04 integra el agente Python con PX4 mediante MAVLink/MAVSDK para
transformar la salida del modulo de percepcion visual en decisiones de control
seguras y trazables. Durante la fase se comprobo una limitacion del plugin
Offboard de MAVSDK (`NO_SETPOINT_SET`) y la ruta activa validada paso a ser
MAVLink directo con `pymavlink`, manteniendo PX4 como autopiloto responsable de
la estabilizacion. Esta fase conecta la percepcion validada en Fase 03 con la
futura experimentacion T0/T1 definida en el perfil del proyecto.

## Objetivo de la fase

Integrar percepcion visual, telemetria PX4, logica de decision y comandos
Offboard para ejecutar correcciones laterales y preparar un descenso asistido
por vision en AirSimNH.

## Alcance

Esta fase cubre:

- lectura de telemetria PX4 y estado local del vehiculo;
- pruebas de armado, despegue, hover, Offboard y aterrizaje en simulacion;
- diagnostico de MAVSDK Offboard y seleccion de MAVLink directo como ruta
  activa de setpoints;
- calculo de comandos laterales a partir del error visual;
- pruebas `dry-run` sin envio de comandos;
- migracion del marcador visual HSV a marcador fiduciario ArUco para las
  pruebas nuevas de control visual;
- correccion lateral a altura fija;
- descenso asistido por vision como ensayo piloto mediante setpoints MAVLink;
- registro CSV de deteccion, telemetria, comandos y estado del controlador;
- documentacion de riesgos y trazabilidad con el perfil.

Esta fase no cubre todavia:

- ejecucion completa del diseno experimental de 160 corridas;
- analisis estadistico final T0/T1;
- pruebas en hardware real;
- uso de `sim_pose` como control autonomo.

## Principio de arquitectura

```text
AirSim       -> entorno visual, fisica y camara bottom_center
PX4          -> autopiloto, modos de vuelo, armado, land y Offboard
Python Agent -> percepcion, decision, logging y setpoints MAVLink directos
```

Regla metodologica: AirSim puede proveer imagenes y escena, pero el control de
vuelo de esta fase debe pasar por PX4. `sim_pose` queda restringido a la
validacion visual cerrada en Fase 03. MAVSDK se conserva como capa de
telemetria/acciones y como diagnostico historico; los comandos activos
validados de control visual se transmiten por MAVLink directo con `pymavlink`.

### Figura de arquitectura final

![Arquitectura final validada de la integración percepción-autopiloto en Fase 04](<Figuras/Arquitectura final validada de la integracion percepcion-autopiloto en fase 04.png>)

*Figura 10. Arquitectura final validada de la integración percepción-autopiloto, incluyendo percepción ArUco, controlador visual, conversión de referencia, MAVLink directo, PX4 Offboard y trazabilidad experimental.*

## Nota metodologica sobre el entorno

En Fase 02 se planteo una estrategia progresiva donde Blocks funcionaba como
entorno controlado principal y AirSimNH como entorno complementario de mayor
complejidad visual. Durante la validacion real del proyecto, la integracion
experimental con PX4 SITL, AirSim y el canal MAVLink/MAVSDK se consolido en
AirSimNH mediante UDP 14601. Por esa razon tecnica, la Fase 04 se ejecuta en
AirSimNH como entorno principal para las pruebas de autopiloto, Offboard y
control visual.

Blocks queda como antecedente y entorno auxiliar de depuracion visual, pero no
se usara como evidencia principal de integracion con autopiloto.

### Figura de soporte

![Evolución metodológica de los entornos de simulación hacia la integración con autopiloto](<Figuras/Evolucion metodologica de los entornos de simulacion hacia la integracion con autopiloto.png>)

*Figura 11. Evolución metodológica desde el uso inicial de Blocks y AirSimNH hacia
la adopción de AirSimNH como entorno principal para la integración con PX4,
MAVLink directo, Offboard y control visual en Fase 04.*

## Criterio de cierre

La Fase 04 puede considerarse lista para pasar a experimentacion cuando exista
evidencia de que el sistema:

- lee telemetria PX4 estable;
- inicia y detiene Offboard de forma controlada por MAVLink directo;
- calcula comandos visuales en `dry-run`;
- detecta un marcador fiduciario ArUco con ID conocido y registra el metodo de
  percepcion usado;
- ejecuta correcciones laterales limitadas;
- ejecuta descenso asistido por vision hasta un umbral piloto de aterrizaje;
- maneja perdida de marcador mediante abort/land;
- genera logs con deteccion, telemetria y comandos;
- permite preparar tratamientos `T0` y `T1`.

## Estado de cierre

La Fase 04 queda concluida tecnicamente con la validacion de P04-V10. Se
obtuvieron tres corridas positivas comparables de descenso asistido por vision
con ArUco reducido y MAVLink directo:

- `phase04_20260503_110722_787b177f`;
- `phase04_20260503_111811_e34f112f`;
- `phase04_20260503_112921_7c3ef4a8`.

En las tres corridas PX4 entro a `OFFBOARD`, se enviaron comandos de descenso
visual limitados, se alcanzo `landing_threshold_reached=True`, no se registro
`abort` y el cierre final recupero `LOITER`, `armed=False`.
