# Diccionario de Datos y Metricas

## Identificacion

- `run_id`: identificador unico de corrida.
- `phase`: debe ser `fase05`.
- `treatment`: `T0` o `T1`.
- `scenario_id`: escenario ejecutado.
- `treatment_pair_id`: par T0/T1 comparable.
- `repetition`: repeticion dentro del escenario.
- `curation_status`: decision metodologica para analisis; puede ser
  `accepted`, `excluded` o `superseded`.
- `curation_reason`: motivo de la decision de curacion.
- `superseded_by`: `run_id` de la corrida correctiva cuando corresponde.

## Escenario

- `planned_initial_height_m`: altura inicial declarada.
- `planned_offset_x_m`: desplazamiento longitudinal declarado.
- `planned_offset_y_m`: desplazamiento lateral declarado.
- `planned_yaw_deg`: orientacion inicial declarada.
- `marker_object_name`: nombre del objeto ArUco en AirSim.

## Percepcion

- `detected`: el detector encontro marcador.
- `accepted_detection`: deteccion aceptada por el detector.
- `confidence`: confianza reportada.
- `error_x_norm`, `error_y_norm`: error visual normalizado.
- `latency_ms`: latencia del ciclo captura-percepcion-decision-log.

## Control

- `command_forward_m_s`: comando longitudinal.
- `command_right_m_s`: comando lateral.
- `command_down_m_s`: comando vertical positivo hacia abajo.
- `command_sent`: indica si se envio setpoint.
- `max_abs_horizontal_command_m_s`: maximo absoluto de comandos longitudinales o
  laterales registrados en la corrida resumida.

En T0, `command_forward_m_s` y `command_right_m_s` deben permanecer en cero.

## Telemetria y posicion

- `north_m`, `east_m`, `down_m`: posicion local NED de PX4.
- `altitude_m`: altura derivada de `down_m`.
- `airsim_position_x`, `airsim_position_y`, `airsim_position_z`: pose AirSim
  cuando esta disponible.
- `marker_x_m`, `marker_y_m`, `marker_z_m`: pose del marcador.
- `terminal_event`: ultimo evento usado como cierre de corrida.
- `terminal_mode`: modo PX4 registrado al cierre.
- `terminal_armed`: estado armado/desarmado al cierre.
- `terminal_status`: estado operativo reportado al cierre.

## Metricas principales

- `final_error_m`: distancia horizontal final entre UAV y centro del marcador.
- `landing_time_s`: tiempo hasta alcanzar el umbral de aterrizaje.
- `total_duration_s`: tiempo total hasta el evento terminal de la corrida.
- estabilidad lateral: dispersion de `error_x_norm` o error lateral durante el
  descenso.
- `landing_success`: corrida aceptada como aterrizaje exitoso.
- `landing_threshold_reached`: indica si se alcanzo el umbral formal de
  aterrizaje dentro del lazo visual o de descenso.

## Metricas de apoyo

- tasa de deteccion aceptada;
- detecciones perdidas;
- latencia media y maxima;
- comandos enviados;
- comandos de descenso;
- abortos o fallos.
