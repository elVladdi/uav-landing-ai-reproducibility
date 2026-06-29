# Fase 06 - Estadistica Descriptiva T0/T1

## Proposito

Este documento presenta la estadistica descriptiva inicial de los resultados
formales T0/T1 consolidados en Fase 06. Su objetivo es resumir el comportamiento
global de ambos tratamientos antes de aplicar pruebas inferenciales y calcular
tamanos de efecto.

La estadistica descriptiva permite identificar tendencias principales en error
final, tiempo de aterrizaje, duracion total, calidad de deteccion, latencia,
comportamiento visual y resultado terminal. Estas tendencias no constituyen por
si solas una prueba de hipotesis, pero orientan la interpretacion posterior.

## Fuente de datos

El analisis se genero a partir de las tablas curadas de Fase 05:

```text
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
```

La base usada corresponde al conjunto formal ya auditado:

- `160` corridas aceptadas.
- `80` corridas T0.
- `80` corridas T1.
- `80` pares T0/T1.
- `8` escenarios (`S01` a `S08`).
- `10` pares por escenario.

## Script reproducible

La estadistica descriptiva fue generada mediante:

```text
src/analysis/phase06_descriptive_statistics.py
```

El script produce las siguientes salidas:

```text
outputs/tables/phase06_analysis/phase06_descriptive_by_treatment.csv
outputs/tables/phase06_analysis/phase06_descriptive_by_scenario_treatment.csv
outputs/tables/phase06_analysis/phase06_pairwise_difference_summary.csv
outputs/tables/phase06_analysis/phase06_success_abort_summary.csv
outputs/tables/phase06_analysis/phase06_descriptive_statistics.md
```

## Resumen global por tratamiento

La comparacion descriptiva global muestra una diferencia marcada entre T0 y T1
en precision final, tiempo de aterrizaje y calidad de deteccion.

| Metrica | T0 media | T0 mediana | T0 DE | T1 media | T1 mediana | T1 DE |
|---|---:|---:|---:|---:|---:|---:|
| Error final (m) | 0.5831 | 0.6835 | 0.1984 | 0.0206 | 0.0211 | 0.0103 |
| Tiempo de aterrizaje (s) | 20.6399 | 21.6295 | 5.8172 | 28.8897 | 28.2915 | 5.8212 |
| Duracion total (s) | 28.1459 | 29.2965 | 5.8111 | 36.3884 | 35.8935 | 5.8516 |
| Tasa de deteccion aceptada | 0.6889 | 0.7482 | 0.2277 | 0.9978 | 1.0000 | 0.0058 |
| Perdidas de deteccion | 21.8750 | 18.5000 | 11.2682 | 0.2500 | 0.0000 | 0.6463 |
| Latencia media (ms) | 119.6310 | 108.8755 | 46.2105 | 75.8052 | 78.2775 | 17.2943 |
| Error visual X medio absoluto | 0.2282 | 0.2291 | 0.1194 | 0.0573 | 0.0573 | 0.0310 |
| Error visual Y medio absoluto | 0.2761 | 0.2762 | 0.1400 | 0.0638 | 0.0554 | 0.0359 |
| Comando horizontal maximo (m/s) | 0.0000 | 0.0000 | 0.0000 | 0.0674 | 0.0649 | 0.0246 |

## Precision final de aterrizaje

La diferencia descriptiva mas fuerte aparece en el error final de
posicionamiento. El tratamiento T0 obtuvo una media de `0.5831 m`, mientras que
T1 obtuvo una media de `0.0206 m`.

En terminos descriptivos, esto sugiere que la asistencia visual de T1 concentra
los aterrizajes mucho mas cerca del objetivo final. Tambien se observa menor
dispersion en T1 (`DE = 0.0103`) que en T0 (`DE = 0.1984`), lo cual indica un
comportamiento mas consistente en precision final.

La diferencia pareada global `T0 - T1` para error final fue:

| Metrica | n | Media | Mediana | DE | Min | Max | Direccion |
|---|---:|---:|---:|---:|---:|---:|---|
| Diferencia error final T0-T1 (m) | 80 | 0.5625 | 0.6602 | 0.1973 | 0.2647 | 0.8568 | T1 menor error final |

Como la diferencia se calcula como `T0 - T1`, valores positivos indican menor
error en T1. Todas las diferencias observadas fueron positivas en el rango
resumido, lo que anticipa una ventaja descriptiva consistente de T1 en
precision final.

## Tiempo de aterrizaje y duracion total

T1 presento mayor tiempo de aterrizaje que T0. La media de T0 fue `20.6399 s`,
mientras que la media de T1 fue `28.8897 s`.

La diferencia pareada global `T0 - T1` para tiempo fue:

| Metrica | n | Media | Mediana | DE | Min | Max | Direccion |
|---|---:|---:|---:|---:|---:|---:|---|
| Diferencia tiempo T0-T1 (s) | 80 | -8.2498 | -8.4170 | 2.6649 | -14.8800 | 0.8390 | T1 mayor tiempo de aterrizaje |

El signo negativo indica que T1 tarda mas que T0 en la mayoria de pares. Esta
diferencia es coherente con el comportamiento esperado del tratamiento visual:
T1 introduce correcciones horizontales y un proceso de alineacion visual antes
de completar el aterrizaje.

La duracion total sigue el mismo patron. T0 obtuvo una media de `28.1459 s` y
T1 una media de `36.3884 s`.

## Calidad de deteccion visual

T1 mostro una tasa de deteccion aceptada muy alta y estable. La media global
fue `0.9978`, con mediana `1.0000` y desviacion estandar `0.0058`.

En T0, la tasa media fue `0.6889`, con mayor dispersion (`DE = 0.2277`). Aunque
T0 no usa correccion visual inteligente como mecanismo de aterrizaje, esta
metrica permite comparar la disponibilidad de deteccion durante la maniobra.

La diferencia pareada global `T1 - T0` en deteccion fue:

| Metrica | n | Media | Mediana | DE | Min | Max | Direccion |
|---|---:|---:|---:|---:|---:|---:|---|
| Diferencia deteccion T1-T0 | 80 | 0.3089 | 0.2518 | 0.2286 | 0.0275 | 1.0000 | T1 mayor tasa de deteccion |

Tambien se observa una reduccion clara en perdidas de deteccion: T0 tuvo una
media de `21.8750` perdidas, mientras que T1 tuvo una media de `0.2500`.

## Latencia y comportamiento visual

La latencia media fue menor en T1 (`75.8052 ms`) que en T0 (`119.6310 ms`).
Ademas, T1 mostro menor dispersion en latencia (`DE = 17.2943`) que T0
(`DE = 46.2105`).

Los errores visuales normalizados tambien fueron menores en T1:

- Error visual X medio absoluto: `0.2282` en T0 frente a `0.0573` en T1.
- Error visual Y medio absoluto: `0.2761` en T0 frente a `0.0638` en T1.

Estos resultados son coherentes con la accion del servo visual en T1, que envia
comandos horizontales para corregir la alineacion. Por ello, el comando
horizontal maximo medio es `0.0000 m/s` en T0 y `0.0674 m/s` en T1.

## Exito y abortos

Ambos tratamientos completaron las 80 corridas aceptadas sin abortos:

| Tratamiento | n | Exitos | Tasa de exito | Abortos | Tasa de aborto |
|---|---:|---:|---:|---:|---:|
| T0 | 80 | 80 | 1.0000 | 0 | 0.0000 |
| T1 | 80 | 80 | 1.0000 | 0 | 0.0000 |

Esto indica que, bajo las condiciones simuladas evaluadas, la diferencia
principal entre tratamientos no esta en la ocurrencia del aterrizaje, sino en
la precision final, el tiempo requerido y la calidad del proceso de alineacion.

## Resumen por escenario

El patron general se mantiene en los ocho escenarios: T1 presenta menor error
final medio que T0 en todos los casos, aunque con mayor tiempo medio de
aterrizaje.

| Escenario | Metrica | T0 media | T1 media |
|---|---|---:|---:|
| S01 | Error final (m) | 0.3997 | 0.0205 |
| S01 | Tiempo de aterrizaje (s) | 19.6737 | 26.8151 |
| S01 | Tasa de deteccion aceptada | 0.8419 | 0.9890 |
| S02 | Error final (m) | 0.3800 | 0.0172 |
| S02 | Tiempo de aterrizaje (s) | 15.1730 | 22.1800 |
| S02 | Tasa de deteccion aceptada | 0.7085 | 0.9956 |
| S03 | Error final (m) | 0.7850 | 0.0198 |
| S03 | Tiempo de aterrizaje (s) | 13.4011 | 23.8521 |
| S03 | Tasa de deteccion aceptada | 0.3843 | 1.0000 |
| S04 | Error final (m) | 0.7642 | 0.0265 |
| S04 | Tiempo de aterrizaje (s) | 13.8809 | 23.0627 |
| S04 | Tasa de deteccion aceptada | 0.3954 | 0.9979 |
| S05 | Error final (m) | 0.3436 | 0.0215 |
| S05 | Tiempo de aterrizaje (s) | 25.6573 | 30.3875 |
| S05 | Tasa de deteccion aceptada | 0.8864 | 1.0000 |
| S06 | Error final (m) | 0.4756 | 0.0165 |
| S06 | Tiempo de aterrizaje (s) | 25.6391 | 32.8749 |
| S06 | Tasa de deteccion aceptada | 0.8843 | 1.0000 |
| S07 | Error final (m) | 0.7660 | 0.0224 |
| S07 | Tiempo de aterrizaje (s) | 26.6010 | 36.8115 |
| S07 | Tasa de deteccion aceptada | 0.7311 | 1.0000 |
| S08 | Error final (m) | 0.7507 | 0.0205 |
| S08 | Tiempo de aterrizaje (s) | 25.0928 | 35.1336 |
| S08 | Tasa de deteccion aceptada | 0.6791 | 1.0000 |

Los escenarios con mayor error medio en T0 fueron S03, S04, S07 y S08. En esos
casos, T1 mantuvo errores medios cercanos a `0.02 m`, lo que sugiere que la
correccion visual fue especialmente relevante en condiciones donde el descenso
base acumulo mayor error final.

## Interpretacion descriptiva inicial

La estadistica descriptiva sugiere tres resultados principales:

1. T1 reduce de manera marcada el error final de aterrizaje frente a T0.
2. T1 incrementa el tiempo de aterrizaje, probablemente por el proceso de
   alineacion visual y correccion horizontal.
3. Ambos tratamientos logran aterrizaje exitoso en todas las corridas formales,
   por lo que la comparacion sustantiva se concentra en precision, tiempo,
   deteccion y dinamica lateral del proceso.

Estos resultados deben tratarse como evidencia descriptiva. La decision
estadistica sobre las hipotesis requiere el siguiente paso: evaluar normalidad
de las diferencias pareadas y aplicar las pruebas inferenciales
correspondientes.

## Criterio de salida

Este entregable queda completo porque:

- resume las metricas principales por tratamiento;
- reporta diferencias pareadas globales;
- documenta exito y abortos;
- presenta resultados desagregados por escenario;
- identifica el patron descriptivo principal T0/T1;
- deja preparada la entrada para el contraste de hipotesis.

El siguiente entregable debe abordar el contraste formal de hipotesis mediante
pruebas para muestras pareadas y resultados categoricos, segun corresponda.
