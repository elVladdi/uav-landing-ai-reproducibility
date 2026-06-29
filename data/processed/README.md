# Carpeta `data/processed`

Esta carpeta contiene datos procesados derivados de las corridas experimentales.

## Proposito

Almacenar archivos limpios, resumidos y preparados para analisis estadistico o generacion de tablas y graficos.

## Contenido esperado

Ejemplos de archivos locales:

- CSV consolidado de corridas T0/T1;
- metricas calculadas por `run_id`;
- tablas limpias por escenario experimental;
- resumen por tratamiento;
- datos preparados para pruebas estadisticas;
- diccionarios de variables cuando corresponda.

## Columnas esperadas para Fase 05

Un consolidado experimental deberia incluir, como minimo:

- `run_id`
- `phase`
- `treatment`
- `environment`
- `scenario_id`
- `initial_altitude_m`
- `initial_offset_x_m`
- `initial_offset_y_m`
- `initial_yaw_deg`
- `marker_detected_rate`
- `final_error_x_m`
- `final_error_y_m`
- `final_error_norm_m`
- `landing_time_s`
- `success`
- `abort_reason`
- `mean_lateral_error_m`
- `std_lateral_error_m`
- `max_lateral_error_m`
- `perception_latency_ms_mean`
- `control_latency_ms_mean`
- `notes`

## Politica de versionado

Por defecto, esta carpeta solo publica en Git:

- `README.md`
- `.gitkeep`

Los archivos procesados se ignoran mientras sean intermedios, redundantes o generados automaticamente.

Si un CSV resumido es necesario para reproducir una tabla o una conclusion del documento, puede versionarse como excepcion con `git add -f`, siempre que sea liviano, estable y trazable al script que lo genera.

## Relacion con la reproducibilidad

Esta carpeta es clave para Fase 05 porque concentra los datos que permiten
verificar la comparacion T0/T1 sin depender exclusivamente de archivos crudos
pesados. Los consolidados finales deben poder regenerarse desde scripts y logs
documentados.

Al cierre formal, la fuente curada principal es
`data/logs/phase05_experiments/summary/phase05_run_summary.csv`, desde la cual
se regeneran las tablas versionadas de `outputs/tables/phase05_experiments/`.
