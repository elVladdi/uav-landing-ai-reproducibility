# Fase 05 - Objetivo y Alcance

## Objetivo

La Fase 05 transforma la validacion tecnica piloto de Fase 04 en una evaluacion
experimental reproducible entre dos tratamientos:

- `T0`: descenso base sin correccion visual inteligente.
- `T1`: aterrizaje asistido por agente visual ArUco y MAVLink directo.

El objetivo metodologico es medir si la incorporacion del agente visual mejora
el desempeno del aterrizaje respecto a un esquema base comparable.

## Alcance incluido

- Definir el protocolo experimental T0/T1.
- Implementar un T0 comparable con T1.
- Congelar la configuracion T1 validada en Fase 04.
- Definir escenarios controlados por altura inicial, desplazamiento lateral y
  orientacion inicial.
- Registrar metricas de precision, tiempo, dinamica lateral, actividad correctiva, exito, detecciones,
  latencia, comandos y abortos.
- Ejecutar primero un piloto minimo antes del bloque completo.
- Preparar la estructura para analisis estadistico posterior.

## Fuera de alcance inmediato

- Ejecutar las 160 corridas completas sin validar antes el piloto.
- Cambiar el detector visual o las ganancias de T1 durante la comparacion.
- Usar `sim_pose` como mecanismo de control autonomo.
- Tratar las corridas diagnosticas de Fase 04 como datos del experimento formal.

## Criterio de salida de la fase

La fase queda lista para analisis cuando exista una matriz depurada con corridas
comparables por `scenario_id`, tratamiento y repeticion, y cuando las metricas
principales puedan calcularse para T0 y T1 bajo las mismas condiciones iniciales.
