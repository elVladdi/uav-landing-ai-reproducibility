# Configuracion Congelada

## Base T1

T1 queda congelado a partir de la configuracion tecnica validada al cierre de
Fase 04:

- ruta de control activo: MAVLink directo con `pymavlink`;
- detector: ArUco;
- diccionario: `DICT_4X4_50`;
- ID esperado: `23`;
- camara: `bottom_center`;
- entorno: AirSimNH + PX4 SITL;
- puerto dedicado: UDP 14601;
- velocidad horizontal maxima: 0.10 m/s;
- velocidad de descenso: 0.08 m/s;
- ciclos centrados requeridos: 5;
- umbral formal de transicion a `LAND`: 1.05 m;
- detecciones perdidas maximas: 6.

Los valores estan registrados en `configs/phase05_experiment_config.json`.

## Enmiendas sobre la configuracion base

La configuracion inicial heredada de Fase 04 usaba `landing_complete_altitude_m`
`0.80` y `max_missing_detections` `3`. Durante la ejecucion formal de S02 se
registraron tres enmiendas metodologicas controladas:

- `P05-A01`: aumento de `max_missing_detections` de `3` a `6` por perdidas
  transitorias del marcador cerca del umbral visual.
- `P05-A02`: cambio de inicializacion de yaw relativa a yaw absoluto para
  controlar el factor orientacion inicial.
- `P05-A03`: aumento de `landing_complete_altitude_m` de `0.80` a `1.05` tras
  diagnostico no formal exitoso con yaw absoluto, sin aborto y sin perdidas de
  marcador.

Las corridas ya aceptadas se conservan con su configuracion registrada en log.
El analisis final debe declarar estas enmiendas y sus fechas de adopcion.
Aunque el campo esta en la seccion `frozen_t1` del JSON, el generador formal lo
usa en los comandos T0 y T1 para que cada par posterior a `P05-A03` comparta el
mismo criterio terminal.

## Base T0

T0 usa la misma ruta de comunicacion activa, pero no usa la percepcion para
corregir:

- `command_forward_m_s = 0.0`;
- `command_right_m_s = 0.0`;
- `command_down_m_s = 0.08`;
- detector ArUco solo para logging pasivo;
- mismo marcador, misma camara, misma altura y mismo escenario que T1.

## Reglas de congelamiento

- No cambiar ganancias ni limites durante una serie comparable.
- No mezclar corridas generadas con distintos tamanos de marcador.
- No aceptar corridas con cambios no documentados de AirSim, PX4, camara,
  detector o parametros de control.
- Registrar cualquier cambio como nueva version de configuracion.
