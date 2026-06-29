# Ayuda Memoria - Fase 04

## Punto de partida

La Fase 04 inicia despues de cerrar:

- Fase 02: AirSimNH + PX4 SITL + MAVSDK validado por UDP 14601;
- Fase 03: detector visual HSV/contornos validado en Blocks y AirSimNH.

## Archivos agregados

```text
configs/control_config.json
src/control/control_config.py
src/control/px4_offboard_control.py
src/control/visual_servo_controller.py
src/control/landing_state_machine.py
src/control/airsim_vision.py
src/control/run_px4_telemetry_check.py
src/control/run_px4_takeoff_land_test.py
src/control/run_offboard_start_diagnostic.py
src/control/run_mavlink_direct_offboard_diagnostic.py
src/control/run_mavlink_direct_hover_test.py
src/control/run_mavlink_mode_recovery.py
src/control/run_mavlink_visual_servo_test.py
src/control/run_offboard_hover_test.py
src/control/run_visual_servo_dry_run.py
src/control/run_visual_landing_trial.py
src/control/run_px4_land.py
src/perception/clear_landing_markers.py
src/perception/detector_factory.py
src/perception/fiducial_marker_detector.py
src/perception/spawn_fiducial_marker.py
src/logging/experiment_logger.py
docs/fase04_integracion_autopiloto/
```

## Decision metodologica principal

El control autonomo debe pasar por PX4, no por `sim_pose`. AirSim se mantiene
como fuente de imagen y entorno simulado. La fase inicio con MAVSDK Offboard,
pero la ruta activa validada paso a MAVLink directo con `pymavlink` despues de
confirmar la limitacion `NO_SETPOINT_SET` del plugin Offboard en esta
configuracion. Esto conserva la alineacion con el perfil: percepcion, decision
y autopiloto integrados en simulacion.

En la migracion interna de Fase 04, el marcador HSV/contornos queda como
respaldo historico y las pruebas nuevas pasan a usar marcador fiduciario ArUco
(`DICT_4X4_50`, ID `23`). Esto fortalece la trazabilidad de la percepcion sin
cambiar la salida usada por el controlador visual.

## Estado de validacion actual

Quedan validadas la telemetria PX4, el despegue/aterrizaje basico, el dry-run
visual con HSV, la migracion ArUco centrada, el signo lateral ArUco con
desplazamiento positivo/negativo, el hover por MAVLink directo, la correccion
lateral activa, el abort por marcador no aceptado y el descenso asistido piloto
con ArUco reducido.

El diagnostico P04-V02B confirmo que, en la configuracion actual
MAVSDK/PX4/AirSimNH, `offboard.start()` devuelve `NO_SETPOINT_SET` para todas
las familias de setpoints probadas. La subfase P04-V02C/P04-V03B valido que
PX4 si acepta setpoints `SET_POSITION_TARGET_LOCAL_NED` por MAVLink directo y
entra a `OFFBOARD`. Por ello, MAVLink directo con `pymavlink` queda como ruta
activa de control para Fase 04.

El cierre tecnico principal se obtuvo con P04-V09B
(`phase04_20260503_110722_787b177f`), donde el agente activo descenso visual,
alcanzo `landing_threshold_reached=True`, aterrizo y recupero `LOITER` sin
`abort`. P04-V10 agrega repetibilidad piloto; la repeticion 2
(`phase04_20260503_111811_e34f112f`) y la repeticion 3
(`phase04_20260503_112921_7c3ef4a8`) tambien fueron positivas.

Con esas tres corridas, la Fase 04 queda concluida. La siguiente etapa ya no es
una validacion tecnica de integracion, sino la preparacion formal de la fase
experimental T0/T1.

## Tratamientos

La fase prepara:

- `T0`: descenso automatico/base sin correccion visual inteligente;
- `T1`: aterrizaje autonomo asistido por agente visual.

La ejecucion masiva de ambos tratamientos queda para la fase experimental.

## Nota para futuras corridas

Antes de aceptar un resultado como avance de Fase 04, debe existir CSV con:

- deteccion visual;
- metodo de deteccion (`detector_method`) y notas del marcador fiduciario si se
  usa ArUco;
- telemetria PX4;
- comando calculado;
- comando enviado si corresponde;
- estado del controlador;
- evento de land/abort;
- run_id y scenario_id.
