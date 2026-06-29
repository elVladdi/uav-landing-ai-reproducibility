# Criterios de Inclusion y Exclusion

La decision operativa se aplica con la regla de curacion documentada en
`10_regla_curacion_datos.md`. Cada corrida queda marcada como `accepted`,
`excluded` o `superseded` en el resumen generado por
`src/analysis/phase05_metrics.py`.

## Inclusion

Aceptar una corrida para comparacion si cumple:

- se ejecuto en AirSimNH + PX4 SITL;
- tiene `phase=fase05`;
- tiene `treatment` igual a `T0` o `T1`;
- tiene `scenario_id`, `treatment_pair_id` y `repetition`;
- inicio la maniobra con PX4 armado, posicion local valida y altura suficiente;
- genero log completo;
- cerro con evento `land_complete`;
- termino con el vehiculo desarmado;
- tiene `landing_success=True`;
- conserva configuracion documentada de marcador, camara y control.

Para `T1`, ademas debe cumplir `landing_threshold_reached=True`. Para `T0`,
los comandos `command_forward_m_s` y `command_right_m_s` deben permanecer dentro
de la tolerancia configurada de cero horizontal.

## Exclusion

Excluir del analisis comparativo si ocurre:

- cierre inesperado de AirSimNH;
- perdida total de conexion con PX4;
- ausencia de log o log incompleto;
- cambio no documentado de configuracion;
- ejecucion de diagnostico en lugar de tratamiento formal;
- T0 con comandos horizontales distintos de cero;
- T1 sin `--enable-descent` cuando la corrida pretende medir aterrizaje.
- duplicacion no resuelta de la misma clave experimental:
  `experiment_id`, `scenario_id`, `treatment`, `treatment_pair_id` y
  `repetition`.

## Supersesion

Si una corrida se repite para corregir una condicion metodologica, la corrida
anterior no se borra. Debe quedar como `superseded` y apuntar a la corrida
correctiva mediante `superseded_by`.

## Registro de incidencias

Las corridas excluidas no deben borrarse. Deben quedar documentadas como
incidencias tecnicas con `run_id`, causa y decision metodologica.
