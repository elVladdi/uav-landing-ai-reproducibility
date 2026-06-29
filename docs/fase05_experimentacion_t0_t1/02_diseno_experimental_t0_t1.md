# Diseno Experimental T0/T1

## Tratamientos

`T0` es el tratamiento base. Desciende con velocidad vertical constante,
velocidad lateral cero y sin usar el error visual para corregir. Puede registrar
percepcion pasiva para medir el error, pero esa informacion no interviene en el
control.

`T1` es el tratamiento asistido. Usa la ruta validada en Fase 04: deteccion
ArUco, calculo de error visual, correccion lateral limitada y descenso por
MAVLink directo.

## Unidad de analisis

Cada corrida experimental es una unidad de analisis. Una corrida debe tener:

- `run_id` unico.
- `scenario_id`.
- tratamiento `T0` o `T1`.
- repeticion.
- parametros de escenario.
- telemetria, percepcion, comandos y resultado final.

## Escenarios formales

La configuracion referencial esta en `configs/phase05_experiment_config.json`.
El diseno formal contempla:

- 2 alturas iniciales: 2.0 m y 3.0 m.
- 2 desplazamientos laterales: 0.4 m y 0.8 m.
- 2 orientaciones iniciales: 0 grados y 15 grados.
- 2 tratamientos.
- 10 repeticiones por tratamiento.

Esto produce 8 escenarios y un minimo de 160 corridas.

## Politica de ejecucion

No ejecutar el bloque completo hasta validar el piloto minimo. El piloto debe
comprobar que T0 y T1 producen logs comparables, que el error final puede
calcularse y que el cierre de cada corrida queda en estado seguro.

## Nota sobre orientacion inicial

La orientacion inicial forma parte del diseno formal, pero el primer piloto debe
mantener `yaw_deg=0.0` hasta validar un procedimiento de inicializacion de yaw
compatible con PX4/AirSimNH sin usar `sim_pose` como control autonomo.
