# Fase 06 - Analisis de Incidencias y Fuentes de Error

## Proposito

Este documento analiza las incidencias tecnicas y posibles fuentes de error
observadas durante el experimento formal T0/T1. Su finalidad es complementar
los resultados estadisticos con una lectura metodologica de los eventos que
pueden afectar la precision, el tiempo de aterrizaje, la deteccion visual y la
dinamica del proceso.

Este analisis responde directamente al objetivo de examinar resultados,
incidencias tecnicas y fuentes de error para delimitar el alcance del framework
AirSim-PX4. Por tanto, no busca reabrir el experimento ni modificar corridas,
sino interpretar los datos aceptados desde una perspectiva de confiabilidad y
limitaciones.

## Fuente de datos

El analisis se realizo sobre la tabla formal de corridas aceptadas:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
```

La base contiene:

- `160` corridas aceptadas.
- `80` corridas T0.
- `80` corridas T1.
- `8` escenarios formales.
- `0` abortos en el conjunto aceptado.

## Script reproducible

El analisis fue generado mediante:

```text
src/analysis/phase06_incident_analysis.py
```

Las salidas producidas son:

```text
outputs/tables/phase06_analysis/phase06_incident_summary.csv
outputs/tables/phase06_analysis/phase06_incident_extreme_runs.csv
outputs/tables/phase06_analysis/phase06_terminal_state_counts.csv
outputs/tables/phase06_analysis/phase06_incident_analysis.md
```

## Resumen global por tratamiento

El resumen por tratamiento muestra diferencias claras en perdidas de deteccion,
latencia, error final maximo y tiempo maximo de aterrizaje:

| Tratamiento | n | Exito | Aborto | Perdidas deteccion media | Tasa deteccion media | Latencia media | Latencia max obs. | Error final max | Tiempo max | Comando horizontal max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| T0 | 80 | 1.0000 | 0.0000 | 21.8750 | 0.6889 | 119.6310 | 532.6800 | 0.8895 | 29.5310 | 0.0000 |
| T1 | 80 | 1.0000 | 0.0000 | 0.2500 | 0.9978 | 75.8052 | 246.4800 | 0.0473 | 43.4070 | 0.1000 |

Ambos tratamientos completaron las corridas aceptadas sin abortos. La
diferencia principal no se encuentra en el estado terminal, sino en la calidad
del proceso: T1 presenta menos perdidas de deteccion y menor error final, pero
tambien mayores tiempos maximos y comandos horizontales activos.

## Estados terminales

Los estados terminales fueron uniformes:

| Tratamiento | Evento terminal | Estado terminal | Aborto | Conteo |
|---|---|---|---|---:|
| T0 | `land_complete` | `landing` | `False` | 80 |
| T1 | `land_complete` | `landing` | `False` | 80 |

No se observaron abortos ni eventos terminales divergentes dentro del conjunto
formal aceptado. Esto permite concentrar el analisis de incidencias en
variables de desempeno y calidad, no en fallas terminales.

## Perdidas de deteccion

T0 presento una media de `21.8750` perdidas de deteccion, mientras que T1
presento una media de `0.2500`. Esta diferencia es una de las incidencias
tecnicas mas relevantes del experimento.

Las mayores perdidas de deteccion se concentraron en T0:

| Ranking | Escenario | Tratamiento | Perdidas | Corrida |
|---:|---|---|---:|---|
| 1 | S06 | T0 | 45 | `phase05_20260607_233910_4a8cd7ec` |
| 2 | S07 | T0 | 44 | `phase05_20260608_113207_9cd80600` |
| 3 | S08 | T0 | 44 | `phase05_20260608_150148_ca339b4f` |
| 4 | S08 | T0 | 44 | `phase05_20260608_154116_86105482` |
| 5 | S04 | T0 | 42 | `phase05_20260607_211514_29807371` |

Estas perdidas no produjeron abortos, pero ayudan a explicar por que T0 tiene
mayor dispersion y mayor error final en escenarios exigentes. En cambio, T1
mantiene deteccion aceptada cercana a `1.0` en la mayoria de escenarios.

## Latencia

T0 presento una latencia media global de `119.6310 ms`, superior a la de T1
(`75.8052 ms`). Tambien presento mayores latencias extremas, con un maximo
observado de `532.6800 ms`.

Las mayores latencias medias fueron:

| Ranking | Escenario | Tratamiento | Latencia media | Corrida |
|---:|---|---|---:|---|
| 1 | S04 | T0 | 312.4915 | `phase05_20260509_212437_424a9706` |
| 2 | S03 | T0 | 266.8020 | `phase05_20260509_010204_ea0ffbac` |
| 3 | S03 | T0 | 235.2427 | `phase05_20260509_000902_46f50524` |
| 4 | S04 | T0 | 219.3668 | `phase05_20260509_211541_7721a9cb` |
| 5 | S04 | T0 | 205.6174 | `phase05_20260509_212246_507d9664` |

Las mayores latencias maximas tambien aparecen principalmente en T0:

| Ranking | Escenario | Tratamiento | Latencia maxima | Corrida |
|---:|---|---|---:|---|
| 1 | S04 | T0 | 532.6800 | `phase05_20260509_212437_424a9706` |
| 2 | S01 | T0 | 530.7900 | `phase05_20260505_171646_b0d3f4a0` |
| 3 | S04 | T0 | 513.6200 | `phase05_20260509_212246_507d9664` |
| 4 | S03 | T0 | 417.5200 | `phase05_20260509_010204_ea0ffbac` |
| 5 | S03 | T0 | 409.8700 | `phase05_20260509_005615_8743cfbe` |

La latencia debe interpretarse como una fuente potencial de variabilidad en la
percepcion y registro de la maniobra. Aunque no impidio el aterrizaje, si puede
afectar la consistencia de la deteccion y la respuesta del sistema.

## Errores finales extremos

Los errores finales mas altos se concentraron en T0:

| Ranking | Escenario | Tratamiento | Error final | Corrida |
|---:|---|---|---:|---|
| 1 | S07 | T0 | 0.8895 | `phase05_20260608_130247_e28ac4f0` |
| 2 | S03 | T0 | 0.8579 | `phase05_20260509_000310_08ba7fc5` |
| 3 | S06 | T0 | 0.8463 | `phase05_20260607_233910_4a8cd7ec` |
| 4 | S04 | T0 | 0.8420 | `phase05_20260607_201947_00bacbf8` |
| 5 | S04 | T0 | 0.8312 | `phase05_20260607_210540_4e06679b` |

Este patron es coherente con los entregables anteriores: T0 aterriza con exito,
pero puede quedar lejos del objetivo cuando la condicion inicial es mas
exigente. T1 reduce el error final maximo a `0.0473 m`, lo cual indica mayor
control de precision final en el conjunto aceptado.

## Tiempos extremos

Los tiempos de aterrizaje mas largos aparecen en T1, especialmente en S07:

| Ranking | Escenario | Tratamiento | Tiempo | Corrida |
|---:|---|---|---:|---|
| 1 | S07 | T1 | 43.4070 | `phase05_20260608_131411_c3801822` |
| 2 | S07 | T1 | 38.7510 | `phase05_20260608_105539_0b6fcf44` |
| 3 | S07 | T1 | 38.5120 | `phase05_20260608_112944_5eb17392` |
| 4 | S07 | T1 | 38.3160 | `phase05_20260608_105157_18017f67` |
| 5 | S07 | T1 | 38.1760 | `phase05_20260608_131743_02ff76bb` |

Esta incidencia no representa falla, sino costo operativo. T1 invierte mas
tiempo para corregir la alineacion visual y reducir el error final. El caso S07
es especialmente relevante porque combina altura `3 m`, desplazamiento `0.8 m`
y yaw `0`, condicion donde el sistema visual logra alta precision pero con
mayor duracion de maniobra.

## Comandos horizontales y posible sobrecorreccion

T0 no envia comandos horizontales de correccion, por lo que su comando
horizontal maximo es `0.0000 m/s`. T1 si utiliza comandos horizontales y alcanzo
un maximo observado de `0.1000 m/s`.

Las corridas con mayor comando horizontal corresponden a T1, principalmente en
S03:

| Ranking | Escenario | Tratamiento | Comando horizontal max | Corrida |
|---:|---|---|---:|---|
| 1 | S03 | T1 | 0.1000 | `phase05_20260509_000451_0b969adf` |
| 2 | S03 | T1 | 0.1000 | `phase05_20260509_001816_20a45b99` |
| 3 | S03 | T1 | 0.1000 | `phase05_20260509_004244_9f022853` |
| 4 | S03 | T1 | 0.1000 | `phase05_20260509_004447_9d806e29` |
| 5 | S03 | T1 | 0.1000 | `phase05_20260509_005801_2841af18` |

Estos valores indican activacion de la correccion visual. No se observa aborto
asociado ni degradacion terminal, pero el uso repetido de comandos maximos debe
considerarse una fuente potencial de sobrecorreccion o saturacion si el sistema
se transfiere a condiciones mas variables.

## Dispersion del error visual

Las mayores dispersiones visuales aparecen en T1, especialmente en escenarios
S03 y S04:

| Categoria | Escenario dominante | Tratamiento dominante | Interpretacion |
|---|---|---|---|
| Mayor dispersion visual X | S03-S04 | T1 | Correccion activa con variabilidad lateral |
| Mayor dispersion visual Y | S03-S04 | T1 | Correccion activa con variabilidad longitudinal |

Esto no contradice la mejora final de T1. Al contrario, puede indicar que T1
esta realizando ajustes activos durante la aproximacion. Sin embargo, tambien
senala que la dinamica del proceso no debe evaluarse solo por el error final,
sino por la evolucion de la correccion.

## Incidencias por escenario

Los escenarios con mas senales de incidencia fueron:

- `S03`: baja deteccion en T0, alta mejora con T1, comandos horizontales altos
  y dispersion visual en T1.
- `S04`: latencias altas en T0, baja deteccion en T0 y alta dispersion visual
  en T1.
- `S07`: mayores tiempos en T1 y errores finales altos en T0.
- `S08`: perdidas de deteccion elevadas en T0 y costo temporal alto en T1.

Estos escenarios comparten condiciones mas exigentes, principalmente
desplazamiento lateral de `0.8 m`. Esto refuerza la conclusion del analisis por
escenario: T1 es mas util cuando el error inicial es mayor, pero tambien
requiere mayor tiempo y actividad de correccion.

## Fuentes de error identificadas

A partir de los datos aceptados, se identifican las siguientes fuentes de error
o variabilidad:

| Fuente | Evidencia | Efecto metodologico |
|---|---|---|
| Perdida temporal de deteccion | Alta en T0, especialmente S03-S04-S07-S08 | Puede aumentar error final y variabilidad |
| Latencia elevada | Maximos superiores a 500 ms en T0 | Puede afectar consistencia perceptual |
| Desplazamiento lateral alto | Mayor mejora y mayor costo temporal con `0.8 m` | Condicion mas exigente para la maniobra |
| Correccion horizontal activa | Comandos maximos de T1 hasta `0.1000 m/s` | Mejora precision pero puede introducir oscilacion |
| Mayor duracion de T1 | Tiempos maximos en S07 | Costo temporal de alineacion visual |
| Dispersion visual en T1 | Mayores dispersiones en S03-S04 | Indica dinamica activa de correccion |

## Interpretacion metodologica

El experimento formal no muestra fallas terminales ni abortos dentro de las
corridas aceptadas. Esto respalda la consistencia operativa del protocolo en
simulacion. Sin embargo, la ausencia de abortos no elimina la existencia de
incidencias intermedias relevantes.

T0 presenta mas perdidas de deteccion, mayor latencia extrema y mayores errores
finales. T1 reduce esas limitaciones en precision y deteccion, pero introduce
otras consideraciones: mayor tiempo de aterrizaje, comandos horizontales
activos y mayor dispersion visual durante la correccion.

Por tanto, T1 debe interpretarse como una mejora en precision final y calidad
de deteccion dentro de AirSim-PX4, no como una solucion sin costo. Su principal
compromiso metodologico es intercambiar tiempo de maniobra y actividad de
control por mayor precision final.

## Delimitacion del alcance

Las incidencias observadas corresponden al entorno simulado AirSim-PX4 y al
protocolo T0/T1 definido en Fase 05. No deben extrapolarse automaticamente a
vuelo fisico real, otras camaras, otros drones ni condiciones visuales no
evaluadas.

El analisis tampoco demuestra ausencia de riesgo en condiciones externas como
iluminacion variable, oclusion, textura irregular, viento, vibracion fisica o
fallas de comunicacion reales. Esas condiciones quedan fuera del alcance del
experimento formal actual.

## Criterio de salida

Este entregable queda completo porque:

- resume incidencias por tratamiento;
- documenta estados terminales y ausencia de abortos;
- identifica perdidas de deteccion relevantes;
- reporta latencias extremas;
- identifica corridas con error final y tiempo extremos;
- interpreta comandos horizontales y dispersion visual;
- delimita fuentes de error y alcance metodologico.

El siguiente entregable debe integrar estos hallazgos en una discusion general
de resultados, relacionando precision, tiempo, deteccion, dinamica lateral y
limitaciones del framework.
