# Fase 06 - Contraste de Hipotesis

## Proposito

Este documento presenta el contraste formal de hipotesis para el experimento
T0/T1. A diferencia de la estadistica descriptiva, aqui se evalua si las
diferencias observadas entre tratamientos son estadisticamente significativas
bajo el diseno pareado definido en Fase 05.

El analisis usa los `80` pares T0/T1 consolidados y auditados en Fase 06. Para
las variables continuas se evalua primero la normalidad de las diferencias
pareadas. Segun ese resultado, se aplica una prueba parametrica pareada o una
prueba no parametrica para muestras relacionadas.

## Fuente de datos

El contraste se genero a partir de:

```text
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
```

Las salidas del contraste se encuentran en:

```text
outputs/tables/phase06_analysis/phase06_hypothesis_tests.csv
outputs/tables/phase06_analysis/phase06_effect_sizes.csv
outputs/tables/phase06_analysis/phase06_categorical_tests.csv
outputs/tables/phase06_analysis/phase06_hypothesis_tests.md
```

## Script reproducible

El analisis fue generado mediante:

```text
src/analysis/phase06_hypothesis_tests.py
```

El script fue ejecutado con `scipy` instalado en el entorno virtual del
proyecto, por lo que las pruebas reportadas corresponden a implementaciones
estadisticas estandar:

- Shapiro-Wilk para normalidad de diferencias.
- t de Student pareada cuando la diferencia cumple normalidad.
- Wilcoxon signed-rank cuando la diferencia no cumple normalidad.
- McNemar exacto para el resultado categorico de exito/fallo.

El nivel de significancia usado fue:

```text
alpha = 0.05
```

## Hipotesis evaluadas

Las hipotesis de Fase 06 se organizaron de la siguiente forma:

| Hipotesis | Variable | Diferencia evaluada | Sentido del contraste |
|---|---|---|---|
| HE1 | Error final | `final_error_m_delta_t0_minus_t1` | T1 reduce el error final frente a T0 |
| HE2 | Tiempo de aterrizaje | `landing_time_s_delta_t0_minus_t1` | T1 modifica el tiempo frente a T0 |
| HE3 | Dinamica lateral de aproximacion | `visual_dispersion_norm_delta_t0_minus_t1` | T1 modifica la dispersion visual/lateral frente a T0 |
| HE3 | Dinamica lateral de aproximacion | `command_count_delta_t1_minus_t0` | T1 modifica la actividad correctiva frente a T0 |
| HE3 | Dinamica lateral de aproximacion | `max_abs_horizontal_command_m_s_delta_t1_minus_t0` | T1 modifica la intensidad correctiva lateral frente a T0 |
| HE4 | Exito de aterrizaje | `landing_success` pareado | T1 modifica la proporcion de exito/fallo |

Para HE1, una diferencia positiva `T0 - T1` indica menor error final en T1.
Para HE2, se uso una prueba bilateral porque interesa detectar modificacion del
tiempo, no solo reduccion. Para HE3, se uso una lectura bilateral porque la
hipotesis evalua modificacion de la dinamica lateral, medida mediante
dispersion visual/lateral y actividad correctiva durante el descenso.

## Seleccion de pruebas

El criterio de seleccion fue:

1. Calcular la diferencia pareada por cada par T0/T1.
2. Aplicar Shapiro-Wilk sobre la distribucion de diferencias.
3. Si `p >= 0.05`, usar t pareada.
4. Si `p < 0.05`, usar Wilcoxon signed-rank.
5. Para exito/fallo, usar McNemar exacto sobre pares discordantes.

Este flujo respeta el diseno pareado del experimento y evita tratar T0 y T1
como grupos independientes.

## Resultados de normalidad y contraste

Los resultados inferenciales fueron:

| Hipotesis | Metrica | n | Normalidad | Prueba aplicada | Estadistico | p-valor | Decision |
|---|---|---:|---|---|---:|---:|---|
| HE1 | Error final `T0 - T1` | 80 | Shapiro-Wilk, p = `7.66472e-08` | Wilcoxon signed-rank | 3240 | `3.92476e-15` | Rechazar H0 |
| HE2 | Tiempo `T0 - T1` | 80 | Shapiro-Wilk, p = `0.157444` | t pareada | -27.6887 | `2.01596e-42` | Rechazar H0 |
| HE3 | Dispersion visual/lateral `T0 - T1` | 78 | Shapiro-Wilk, p = `1.26775e-05` | Wilcoxon signed-rank | 1097 | `0.0271772` | Rechazar H0 |
| HE3 | Actividad correctiva `T1 - T0` | 80 | Shapiro-Wilk, p = `0.565142` | t pareada | 27.1885 | `7.4351e-42` | Rechazar H0 |
| HE3 | Intensidad correctiva lateral `T1 - T0` | 80 | Shapiro-Wilk, p = `6.42363e-06` | Wilcoxon signed-rank | 0 | `7.39174e-15` | Rechazar H0 |

En HE1 y en dos indicadores de HE3, las diferencias no cumplieron normalidad,
por lo que se aplico Wilcoxon signed-rank. En HE2 y en el conteo de comandos
de HE3, la diferencia no rechazo normalidad, por lo que se aplico t pareada.

La HE3 queda respaldada como modificacion significativa de la dinamica lateral
de aproximacion: T1 presenta mayor dispersion visual/lateral, mayor actividad
correctiva y mayor intensidad de comando horizontal que T0.

## Tamano del efecto e interpretacion practica

Ademas del p-valor, se calculo la magnitud de las diferencias:

| Hipotesis | Metrica | Diferencia media | Diferencia mediana | Cohen dz | Cambio porcentual medio | Interpretacion |
|---|---|---:|---:|---:|---:|---|
| HE1 | Error final | 0.562492 m | 0.660237 m | 2.85113 | 0.964637 | T1 reduce el error final frente a T0 |
| HE2 | Tiempo de aterrizaje | -8.24981 s | -8.417 s | -3.09569 | -0.399703 | T1 modifica el tiempo de aterrizaje frente a T0 |
| HE3 | Dispersion visual/lateral | -0.0226746 | -0.00869731 | -0.399055 | -0.352955 | T1 modifica la dispersion visual/lateral frente a T0 |
| HE3 | Actividad correctiva | 46.6625 | 45.5 | 3.03976 | 0.54568 | T1 incrementa la actividad correctiva frente a T0 |
| HE3 | Intensidad correctiva lateral | 0.0674045 | 0.0649284 | 2.74316 |  | T1 incrementa la intensidad correctiva lateral frente a T0 |

La magnitud de HE1 indica una reduccion media del error final de
aproximadamente `0.5625 m` respecto a T0. El cambio porcentual medio indica que
la reduccion equivale aproximadamente al `96.46%` del error medio de T0.

En HE2, la diferencia media fue negativa porque se calculo como `T0 - T1`. Esto
indica que T1 tardo mas que T0, con un incremento medio aproximado de
`8.2498 s`. El cambio porcentual medio equivale a un incremento cercano al
`39.97%` respecto al tiempo medio de T0.

En HE3, la diferencia de dispersion visual/lateral fue significativa y
negativa en la forma `T0 - T1`, lo que indica mayor dispersion combinada en
T1. Este resultado se complementa con dos indicadores de actividad correctiva:
T1 genero en promedio `46.6625` comandos mas que T0 y aumento la intensidad
maxima del comando horizontal en `0.0674 m/s`.

Por tanto, HE3 no se interpreta como menor variabilidad, sino como evidencia de
que la asistencia visual Offboard modifica la dinamica lateral durante la
aproximacion. La mayor actividad correctiva es coherente con la reduccion del
error final observada en HE1.

## Resultado categorico de exito/fallo

Para HE4 se evaluo la variable `landing_success` mediante McNemar exacto:

| Hipotesis | Resultado | Pares | T0 exito/T1 exito | T0 exito/T1 fallo | T0 fallo/T1 exito | T0 fallo/T1 fallo | Prueba | p-valor | Decision |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| HE4 | `landing_success` | 80 | 80 | 0 | 0 | 0 | McNemar exacto | 1 | No rechazar H0 |

No existen pares discordantes: los 80 pares tuvieron exito tanto en T0 como en
T1. Por tanto, no hay evidencia de diferencia en la proporcion de exito/fallo.
La diferencia principal entre tratamientos no se encuentra en aterrizar o no
aterrizar, sino en la precision final, el tiempo requerido y la dinamica de
correccion durante la maniobra.

## Decision por hipotesis

### HE1 - Error final

Se rechaza la hipotesis nula. T1 reduce significativamente el error final de
aterrizaje frente a T0.

La prueba aplicada fue Wilcoxon signed-rank debido a que las diferencias no
cumplieron normalidad. El resultado fue estadisticamente significativo
(`p = 3.92476e-15`) y la magnitud practica fue alta (`Cohen dz = 2.85113`).

### HE2 - Tiempo de aterrizaje

Se rechaza la hipotesis nula. T1 modifica significativamente el tiempo de
aterrizaje frente a T0.

La prueba aplicada fue t pareada porque las diferencias de tiempo no rechazaron
normalidad. El resultado fue estadisticamente significativo
(`p = 2.01596e-42`). La diferencia media indica que T1 tarda mas que T0, lo cual
se interpreta como el costo temporal asociado a la alineacion y correccion
visual.

### HE3 - Dinamica lateral de aproximacion

Se rechaza la hipotesis nula. T1 modifica significativamente la dinamica lateral
de aproximacion frente a T0.

La evidencia se sostiene en tres indicadores:

- dispersion visual/lateral combinada: Wilcoxon signed-rank, `p = 0.0271772`;
- actividad correctiva por conteo de comandos: t pareada, `p = 7.4351e-42`;
- intensidad correctiva lateral: Wilcoxon signed-rank, `p = 7.39174e-15`.

La interpretacion practica es que T1 no solo aterriza con menor error final,
sino que tambien cambia el proceso de aproximacion. El tratamiento asistido por
vision produce mas actividad de correccion lateral y mayor intensidad de
comando horizontal, lo cual explica que el sistema tarde mas pero termine mucho
mas cerca de la plataforma.

### HE4 - Exito/fallo

No se rechaza la hipotesis nula. No se detecta diferencia en la proporcion de
exito/fallo entre T0 y T1.

Este resultado no implica ausencia de mejora general de T1, sino que ambos
tratamientos lograron aterrizaje exitoso en todas las corridas formales. La
mejora de T1 se expresa principalmente en precision final y dinamica de
correccion, no en tasa de exito dentro del conjunto aceptado.

## Sintesis inferencial

El contraste de hipotesis confirma estadisticamente el patron observado en la
estadistica descriptiva:

- T1 reduce de forma significativa el error final de aterrizaje.
- T1 incrementa significativamente el tiempo de aterrizaje.
- T1 modifica significativamente la dinamica lateral de aproximacion.
- T0 y T1 no difieren en exito/fallo porque ambos alcanzaron 100% de exito en
  las corridas aceptadas.

Estos resultados respaldan que el agente visual mejora la precision del
aterrizaje en simulacion AirSim-PX4, introduce un costo temporal y cambia de
forma medible la dinamica de correccion lateral durante la aproximacion.

## Criterio de salida

Este entregable queda completo porque:

- define las hipotesis HE1 a HE4;
- documenta el criterio de seleccion de pruebas;
- reporta normalidad de diferencias pareadas;
- aplica pruebas inferenciales acordes al diseno experimental;
- incorpora tamanos de efecto e interpretacion practica;
- distingue entre significancia estadistica y relevancia metodologica;
- deja preparado el paso hacia el analisis por escenario.

El siguiente entregable debe analizar la consistencia de estos resultados en
los escenarios `S01` a `S08`.
