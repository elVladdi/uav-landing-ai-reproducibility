# Fase 06 - Objetivo y Alcance

## Objetivo

La Fase 06 transforma el cierre experimental de Fase 05 en un analisis
estadistico, interpretativo y metodologico de los resultados obtenidos para los
tratamientos:

- `T0`: descenso base sin correccion visual inteligente.
- `T1`: aterrizaje asistido por agente visual ArUco y MAVLink directo.

El objetivo metodologico de esta fase es examinar los resultados
experimentales, las incidencias tecnicas y las principales fuentes de error del
sistema, con el fin de delimitar el alcance real del framework AirSim-PX4 y
orientar mejoras metodologicas posteriores.

Esta fase responde directamente al objetivo especifico asociado al examen de
resultados, incidencias y fuentes de error. Por tanto, no introduce un nuevo
experimento ni modifica las condiciones ya congeladas, sino que analiza la base
experimental cerrada en Fase 05.

## Insumos de entrada

La Fase 06 usa como fuente primaria las tablas curadas generadas al cierre de
Fase 05:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

Como control inicial, se ejecuto el auditor de consolidacion de dataset:

```text
src/analysis/phase06_dataset_audit.py
```

El reporte generado se encuentra en:

```text
outputs/tables/phase06_analysis/phase06_dataset_audit.md
outputs/tables/phase06_analysis/phase06_dataset_audit.csv
```

## Estado de consolidacion del dataset

La auditoria inicial de Fase 06 confirma que la base experimental formal esta
cerrada y es consistente para iniciar el analisis:

- `160/160` corridas aceptadas.
- `80/80` pares T0/T1.
- `8/8` escenarios presentes (`S01` a `S08`).
- `10` repeticiones por escenario y tratamiento.
- `10` pares por escenario.
- `160` identificadores de corrida no vacios y sin duplicados.
- `80` identificadores de par no vacios y sin duplicados.
- Columnas T0 y T1 presentes en la tabla de diferencias pareadas.
- Resultado global de auditoria: `37` verificaciones `OK`, `0` en `REVIEW`.

Este resultado habilita el uso de las tablas curadas de Fase 05 como base
formal para estadistica descriptiva, contraste de hipotesis, tamanos de efecto,
analisis por escenario y discusion de limitaciones.

## Alcance incluido

La Fase 06 incluye:

- Consolidar la evidencia final de Fase 05 antes del analisis.
- Calcular estadistica descriptiva global por tratamiento.
- Comparar T0 y T1 mediante diferencias pareadas.
- Evaluar error final de posicionamiento, tiempo de aterrizaje, dinamica
  lateral de aproximacion, actividad correctiva, tasa de exito y calidad de
  deteccion.
- Aplicar pruebas de normalidad sobre diferencias pareadas cuando corresponda.
- Aplicar pruebas inferenciales para contrastar las hipotesis experimentales.
- Reportar tamanos de efecto y magnitud practica de las diferencias.
- Analizar resultados por escenario (`S01` a `S08`).
- Revisar incidencias, fuentes de error y condiciones tecnicas observadas.
- Delimitar el alcance del framework dentro de simulacion AirSim-PX4.
- Preparar tablas, figuras y texto interpretativo para tesis y articulo.

## Fuera de alcance inmediato

La Fase 06 no incluye:

- Ejecutar nuevas corridas formales.
- Cambiar el detector visual, los parametros de control o el protocolo T0/T1.
- Reabrir la secuencia experimental cerrada de Fase 05.
- Usar corridas `excluded` o `superseded` para promedios o pruebas
  comparativas.
- Extrapolar los resultados a vuelo fisico real.
- Afirmar validacion en drones, camaras o entornos no evaluados.
- Proponer un detector nuevo o una ley de control universal.

Las corridas excluidas o reemplazadas permanecen como evidencia de trazabilidad
y control de calidad, pero no forman parte del conjunto formal usado para
analisis comparativo.

## Preguntas de analisis

La fase debe responder, como minimo, las siguientes preguntas:

- Si T1 reduce el error final de aterrizaje respecto a T0.
- Si T1 modifica el tiempo total de aterrizaje respecto a T0.
- Si T1 modifica la dinamica lateral de aproximacion y la actividad correctiva
  durante el descenso.
- Si T1 modifica la tasa de exito, aborto o resultado terminal.
- En que escenarios la mejora de T1 es mas fuerte o mas debil.
- Que incidencias tecnicas explican variaciones, perdidas de deteccion,
  latencias o comportamientos dinamicos relevantes.
- Cuales son los limites metodologicos del framework evaluado en simulacion.

## Criterio de salida de la fase

La Fase 06 queda completa cuando exista evidencia reproducible de:

- tablas descriptivas T0/T1;
- tabla de contrastes de hipotesis;
- tabla de tamanos de efecto;
- analisis por escenario;
- resumen de incidencias y fuentes de error;
- figuras finales para error, tiempo, diferencias pareadas y tasa de exito;
- discusion de resultados alineada con el alcance de simulacion AirSim-PX4;
- conclusiones que respondan explicitamente a las hipotesis y al objetivo de la
  fase.

El cierre de Fase 06 debe permitir pasar de resultados experimentales curados a
una interpretacion cientifica defendible, trazable y compatible con la
redaccion final de la tesis.
