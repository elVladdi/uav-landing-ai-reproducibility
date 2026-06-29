# Fase 06 - Analisis por Escenario

## Proposito

Este documento analiza los resultados T0/T1 desagregados por escenario
experimental. Su objetivo es determinar si el efecto observado globalmente se
mantiene en los escenarios `S01` a `S08`, y bajo que condiciones la asistencia
visual de T1 produce mayor mejora o mayor costo temporal.

El analisis por escenario complementa la estadistica descriptiva global y el
contraste de hipotesis. Mientras los entregables anteriores confirman una
mejora general de T1 en precision final, este documento identifica en que
condiciones esa mejora es mas fuerte, mas moderada o mas costosa en tiempo.

## Fuente de datos

El analisis usa como entrada:

```text
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
```

La base contiene:

- `8` escenarios formales (`S01` a `S08`).
- `10` pares T0/T1 por escenario.
- `80` pares T0/T1 en total.

## Script reproducible

El analisis fue generado mediante:

```text
src/analysis/phase06_scenario_analysis.py
```

Las salidas producidas son:

```text
outputs/tables/phase06_analysis/phase06_scenario_analysis.csv
outputs/tables/phase06_analysis/phase06_scenario_factor_summary.csv
outputs/tables/phase06_analysis/phase06_scenario_rankings.csv
outputs/tables/phase06_analysis/phase06_scenario_analysis.md
```

## Variables consideradas

Para cada escenario se resumieron:

- error final medio en T0;
- error final medio en T1;
- reduccion media de error `T0 - T1`;
- tiempo medio de aterrizaje en T0;
- tiempo medio de aterrizaje en T1;
- diferencia media de tiempo `T0 - T1`;
- ganancia media de deteccion `T1 - T0`;
- altura inicial;
- desplazamiento lateral en `Y`;
- yaw inicial.

La diferencia de error se interpreta asi:

```text
T0 - T1 > 0  => T1 reduce el error final.
```

La diferencia de tiempo se interpreta asi:

```text
T0 - T1 < 0  => T1 tarda mas que T0.
```

## Resumen por escenario

El patron general se mantiene en los ocho escenarios: T1 reduce el error final
medio respecto a T0 en todos los casos. Al mismo tiempo, T1 incrementa el
tiempo medio de aterrizaje en todos los escenarios.

| Escenario | Altura | Offset Y | Yaw | Error T0 | Error T1 | Reduccion error | Tiempo T0 | Tiempo T1 | Delta tiempo T0-T1 | Ganancia deteccion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S01 | 2.0 | 0.4 | 0 | 0.3997 | 0.0205 | 0.3792 | 19.6737 | 26.8151 | -7.1414 | 0.1471 |
| S02 | 2.0 | 0.4 | 15 | 0.3800 | 0.0172 | 0.3629 | 15.1730 | 22.1800 | -7.0070 | 0.2870 |
| S03 | 2.0 | 0.8 | 0 | 0.7850 | 0.0198 | 0.7652 | 13.4011 | 23.8521 | -10.4510 | 0.6157 |
| S04 | 2.0 | 0.8 | 15 | 0.7642 | 0.0265 | 0.7377 | 13.8809 | 23.0627 | -9.1818 | 0.6024 |
| S05 | 3.0 | 0.4 | 0 | 0.3436 | 0.0215 | 0.3220 | 25.6573 | 30.3875 | -4.7302 | 0.1136 |
| S06 | 3.0 | 0.4 | 15 | 0.4756 | 0.0165 | 0.4591 | 25.6391 | 32.8749 | -7.2358 | 0.1157 |
| S07 | 3.0 | 0.8 | 0 | 0.7660 | 0.0224 | 0.7436 | 26.6010 | 36.8115 | -10.2105 | 0.2689 |
| S08 | 3.0 | 0.8 | 15 | 0.7507 | 0.0205 | 0.7302 | 25.0928 | 35.1336 | -10.0408 | 0.3209 |

Los errores finales de T1 permanecen en un rango estrecho, aproximadamente
entre `0.0165 m` y `0.0265 m`, incluso cuando el error medio de T0 cambia de
manera importante entre escenarios. Esto indica que T1 estabiliza la precision
final en condiciones iniciales distintas.

## Escenarios con mayor reduccion de error

Los escenarios con mayor reduccion media de error fueron:

| Ranking | Escenario | Reduccion media de error | Interpretacion |
|---:|---|---:|---|
| 1 | S03 | 0.7652 | Mayor reduccion media de error final con T1 |
| 2 | S07 | 0.7436 | Alta reduccion media de error final con T1 |
| 3 | S04 | 0.7377 | Alta reduccion media de error final con T1 |

Estos escenarios comparten desplazamiento lateral alto (`0.8 m`) o condiciones
donde T0 acumulo mayor error final. En ellos, el agente visual tiene mas margen
para corregir la trayectoria antes del aterrizaje.

S03 y S04 corresponden a altura inicial de `2 m` con desplazamiento `0.8 m`.
S07 corresponde a altura inicial de `3 m` con desplazamiento `0.8 m`. En los
tres casos, T1 llevo el error final medio a valores cercanos a `0.02 m`.

## Escenarios con menor reduccion de error

Los escenarios con menor reduccion media de error fueron:

| Ranking | Escenario | Reduccion media de error | Interpretacion |
|---:|---|---:|---|
| 1 | S05 | 0.3220 | Menor reduccion media de error final con T1 |
| 2 | S02 | 0.3629 | Reduccion moderada de error final con T1 |
| 3 | S01 | 0.3792 | Reduccion moderada de error final con T1 |

Estos escenarios tienen errores medios de T0 mas bajos que los escenarios de
desplazamiento alto. Por tanto, la mejora absoluta de T1 es menor, aunque el
error final de T1 sigue siendo bajo.

Este resultado no contradice la eficacia de T1; indica que cuando T0 ya parte
de una condicion menos exigente, la reduccion absoluta disponible tambien es
menor.

## Costo temporal por escenario

T1 incremento el tiempo medio de aterrizaje en todos los escenarios. Los
mayores costos temporales fueron:

| Ranking | Escenario | Delta tiempo T0-T1 | Interpretacion |
|---:|---|---:|---|
| 1 | S03 | -10.4510 | Mayor incremento temporal de T1 |
| 2 | S07 | -10.2105 | Alto incremento temporal de T1 |
| 3 | S08 | -10.0408 | Alto incremento temporal de T1 |

El signo negativo se debe a que la diferencia se calcula como `T0 - T1`. Por
tanto, valores mas negativos indican que T1 tardo mas.

Los escenarios con mayor costo temporal coinciden en gran medida con los de
mayor correccion requerida, especialmente aquellos con desplazamiento lateral
de `0.8 m`. Esto sugiere que el costo temporal de T1 esta asociado al proceso
de alineacion visual y correccion horizontal.

Los menores costos temporales fueron:

| Ranking | Escenario | Delta tiempo T0-T1 | Interpretacion |
|---:|---|---:|---|
| 1 | S05 | -4.7302 | Menor incremento temporal de T1 |
| 2 | S02 | -7.0070 | Incremento temporal moderado |
| 3 | S01 | -7.1414 | Incremento temporal moderado |

S05 presenta el menor costo temporal y tambien una de las menores reducciones
absolutas de error. Esto refuerza la idea de que T1 invierte mas tiempo cuando
la correccion visual requerida es mayor.

## Ganancia de deteccion por escenario

Las mayores ganancias medias de deteccion aceptada fueron:

| Ranking | Escenario | Ganancia media de deteccion | Interpretacion |
|---:|---|---:|---|
| 1 | S03 | 0.6157 | Mayor mejora media en tasa de deteccion aceptada |
| 2 | S04 | 0.6024 | Alta mejora media en tasa de deteccion aceptada |
| 3 | S08 | 0.3209 | Mejora media relevante en tasa de deteccion aceptada |

S03 y S04 presentan las mayores ganancias de deteccion y corresponden a
desplazamiento lateral de `0.8 m` con altura inicial de `2 m`. En estos casos,
T0 mostro menor disponibilidad de deteccion aceptada, mientras que T1 mantuvo
tasas cercanas a `1.0`.

## Analisis por factores experimentales

El resumen por factores muestra como cambian las diferencias medias segun
altura, desplazamiento lateral y yaw:

| Factor | Nivel | Pares | Reduccion error | Delta tiempo T0-T1 | Ganancia deteccion |
|---|---:|---:|---:|---:|---:|
| Altura | 2.0 | 40 | 0.5612 | -8.4453 | 0.4131 |
| Altura | 3.0 | 40 | 0.5637 | -8.0543 | 0.2048 |
| Offset Y | 0.4 | 40 | 0.3808 | -6.5286 | 0.1659 |
| Offset Y | 0.8 | 40 | 0.7442 | -9.9710 | 0.4520 |
| Yaw | 0.0 | 40 | 0.5525 | -8.1333 | 0.2863 |
| Yaw | 15.0 | 40 | 0.5725 | -8.3664 | 0.3315 |

### Altura inicial

La reduccion media de error fue muy similar entre `2 m` y `3 m`:

- `0.5612 m` para altura `2 m`.
- `0.5637 m` para altura `3 m`.

Esto sugiere que, dentro de las alturas evaluadas, la ventaja de T1 en
precision final se mantiene estable. El costo temporal fue levemente mayor en
`2 m`, pero la diferencia no parece dominante en comparacion con el efecto del
desplazamiento lateral.

### Desplazamiento lateral

El desplazamiento lateral muestra el efecto mas claro:

- Con `0.4 m`, la reduccion media de error fue `0.3808 m`.
- Con `0.8 m`, la reduccion media de error fue `0.7442 m`.

El desplazamiento `0.8 m` casi duplica la mejora absoluta respecto a `0.4 m`.
Sin embargo, tambien aumenta el costo temporal:

- `-6.5286 s` con `0.4 m`.
- `-9.9710 s` con `0.8 m`.

Esto indica que T1 es especialmente valioso cuando el error lateral inicial es
mayor, aunque requiere mas tiempo para corregir la alineacion.

### Yaw inicial

El yaw inicial de `15 grados` produjo una reduccion media de error ligeramente
mayor que `0 grados`:

- `0.5525 m` con yaw `0`.
- `0.5725 m` con yaw `15`.

Tambien se observa una ganancia de deteccion algo mayor con yaw `15 grados`
(`0.3315`) que con yaw `0 grados` (`0.2863`). La diferencia es moderada, por lo
que el yaw parece afectar menos que el desplazamiento lateral en el conjunto
evaluado.

## Interpretacion general

El analisis por escenario confirma que T1 no solo mejora el promedio global,
sino que reduce el error final en todos los escenarios formales. La mejora es
mas pronunciada cuando el desplazamiento lateral inicial es mayor (`0.8 m`),
lo que coincide con situaciones donde T0 acumula errores finales mas altos.

El costo temporal tambien se distribuye de forma consistente: T1 tarda mas en
todos los escenarios, especialmente cuando debe corregir desplazamientos
laterales mayores. Por tanto, la mejora de precision no es gratuita; implica
un proceso adicional de alineacion visual.

En conjunto, los resultados sugieren que el framework AirSim-PX4 con asistencia
visual T1 es mas efectivo en escenarios donde el aterrizaje base presenta mayor
error inicial acumulado, pero esa efectividad viene acompanada de mayor tiempo
de maniobra.

## Criterio de salida

Este entregable queda completo porque:

- reporta resultados T0/T1 para `S01` a `S08`;
- identifica escenarios con mayor y menor mejora de error;
- identifica escenarios con mayor y menor costo temporal;
- resume ganancias de deteccion por escenario;
- interpreta los resultados por altura, desplazamiento lateral y yaw;
- confirma la consistencia del patron global en todos los escenarios.

El siguiente entregable debe analizar incidencias, fuentes de error y eventos
tecnicos relevantes registrados durante el experimento formal.
