# Fase 06 - Discusion de Resultados

## Proposito

Este documento integra los resultados obtenidos en la Fase 06 y discute su
significado metodologico para el framework AirSim-PX4 de aterrizaje asistido
por vision. A diferencia de los entregables anteriores, que reportan
estadistica descriptiva, contrastes de hipotesis, analisis por escenario e
incidencias, este entregable interpreta los hallazgos de forma conjunta.

La discusion se centra en responder que indican los resultados sobre el
comportamiento de los tratamientos:

- `T0`: descenso base sin correccion visual inteligente.
- `T1`: aterrizaje asistido por agente visual ArUco y MAVLink directo.

El objetivo no es presentar un nuevo analisis numerico, sino explicar el
sentido experimental de los resultados, sus implicaciones practicas, sus
limites y su valor para la tesis.

## Base de interpretacion

La discusion se apoya en los entregables previos de Fase 06:

```text
03_estadistica_descriptiva_t0_t1.md
04_contraste_hipotesis.md
05_analisis_por_escenario.md
06_analisis_incidencias_fuentes_error.md
```

La base experimental usada esta consolidada y auditada:

- `160` corridas aceptadas.
- `80` corridas T0.
- `80` corridas T1.
- `80` pares T0/T1.
- `8` escenarios formales.
- `10` pares por escenario.
- `0` abortos en el conjunto aceptado.

Por tanto, las interpretaciones se realizan sobre el bloque formal del
experimento, no sobre corridas diagnosticas ni registros reemplazados.

## Resultado central del experimento

El resultado principal es que T1 reduce de forma clara, consistente y
estadisticamente significativa el error final de aterrizaje frente a T0.

La media de error final fue:

| Tratamiento | Error final medio |
|---|---:|
| T0 | 0.5831 m |
| T1 | 0.0206 m |

La diferencia pareada media `T0 - T1` fue `0.5625 m`, con una mediana de
`0.6602 m`. El contraste formal mediante Wilcoxon signed-rank rechazo la
hipotesis nula para HE1 (`p = 3.92476e-15`). Ademas, el tamano del efecto fue
alto (`Cohen dz = 2.85113`), lo que indica que el resultado no depende
unicamente del p-valor, sino tambien de una diferencia practica relevante.

Desde el punto de vista metodologico, esto significa que el agente visual T1 no
solo introduce una mejora numerica marginal. En las condiciones simuladas
evaluadas, cambia el comportamiento final del aterrizaje: el sistema deja de
aterrizar simplemente cerca de la zona prevista y pasa a concentrar los
aterrizajes alrededor del marcador visual con errores medios cercanos a
`0.02 m`.

## Precision frente a exito terminal

Un punto importante de interpretacion es que ambos tratamientos alcanzaron
`80/80` aterrizajes exitosos y `0` abortos. Por ello, el aporte de T1 no debe
describirse como una mejora en la capacidad basica de aterrizar, porque T0
tambien completo las maniobras del conjunto formal.

La diferencia esta en la calidad del aterrizaje:

- T0 aterriza, pero puede quedar con errores finales altos.
- T1 aterriza y ademas reduce de forma marcada el error final.

Esto es relevante para la tesis porque evita una conclusion simplista. El
resultado no es "T1 permite aterrizar y T0 no"; el resultado correcto es que,
bajo las condiciones simuladas evaluadas, ambos tratamientos aterrizan, pero T1
mejora sustancialmente la precision final.

La prueba categorica para HE4 mediante McNemar exacto no rechazo la hipotesis
nula (`p = 1`) porque no hubo pares discordantes: todos los pares fueron
exitosos en ambos tratamientos. Esta ausencia de diferencia en exito/fallo no
debilita los resultados de precision; mas bien delimita donde esta el efecto
real de T1.

## Costo temporal de la correccion visual

La mejora de precision de T1 ocurre con un costo temporal. El tiempo medio de
aterrizaje fue:

| Tratamiento | Tiempo medio |
|---|---:|
| T0 | 20.6399 s |
| T1 | 28.8897 s |

La diferencia pareada media `T0 - T1` fue `-8.2498 s`, lo que indica que T1
tardo mas que T0. La prueba t pareada rechazo la hipotesis nula para HE2
(`p = 2.01596e-42`), por lo que la modificacion del tiempo es estadisticamente
significativa.

Este incremento no debe interpretarse como una falla del sistema, sino como el
costo operacional de introducir alineacion visual. T1 invierte tiempo en
corregir el desplazamiento horizontal y estabilizar la aproximacion visual
antes de completar el aterrizaje. Esa decision de control mejora la precision
final, pero alarga la maniobra.

La discusion correcta, por tanto, no es si T1 es "mejor" en todos los sentidos,
sino que T1 desplaza el compromiso del sistema: sacrifica velocidad de
aterrizaje para ganar precision final. Para una aplicacion donde la exactitud
del punto de contacto sea prioritaria, este compromiso puede ser favorable. En
una aplicacion donde el tiempo sea critico, el costo temporal deberia evaluarse
con criterios operativos adicionales.

## Disponibilidad visual como metrica de apoyo

T1 tambien mejora de forma significativa la tasa de deteccion aceptada frente a
T0. La media global fue:

| Tratamiento | Tasa media de deteccion aceptada |
|---|---:|
| T0 | 0.6889 |
| T1 | 0.9978 |

Esta mejora tiene una interpretacion doble. Por un lado, confirma que durante
T1 la percepcion visual se mantiene disponible de forma mas estable. Por otro
lado, ayuda a explicar la reduccion del error final: una deteccion mas
consistente ofrece al sistema mejor informacion para corregir la trayectoria
durante la aproximacion.

No obstante, la tasa de deteccion no debe interpretarse de manera aislada. En
T1 tambien aparecen comandos horizontales activos y mayor dispersion visual en
escenarios exigentes. Esto indica que la deteccion alimenta un proceso dinamico
de correccion, no una simple observacion pasiva.

## Dinamica lateral de aproximacion

La HE3 evalua si la asistencia visual Offboard modifica significativamente la
dinamica lateral de aproximacion respecto del tratamiento base. La evidencia
indica que si existe una modificacion estadisticamente significativa.

El indicador de dispersion visual/lateral combinada mostro una diferencia
pareada media `T0 - T1` de `-0.0227`. El signo negativo indica que T1 presenta
mayor dispersion visual/lateral durante la aproximacion. Como el contraste de
HE3 es bilateral, esta diferencia respalda la modificacion dinamica
(`p = 0.0271772`).

La actividad correctiva refuerza esta lectura. T1 genero en promedio `46.6625`
comandos mas que T0 (`p = 7.4351e-42`) y aumento la intensidad maxima del
comando horizontal en `0.0674 m/s` (`p = 7.39174e-15`). Por tanto, T1 no solo
termina mas cerca de la plataforma; tambien cambia el proceso de aproximacion
mediante correcciones laterales activas.

Esta diferencia dinamica es coherente con los resultados de HE1 y HE2: T1
corrige mas, tarda mas y aterriza con mucha mayor precision final.

## Consistencia por escenario

El analisis por escenario muestra que T1 reduce el error final medio en los
ocho escenarios formales. Este punto es importante porque evita que la mejora
global sea atribuida a uno o dos escenarios dominantes.

Los errores finales medios de T1 se mantuvieron aproximadamente entre
`0.0165 m` y `0.0265 m`, aun cuando los errores de T0 variaron de forma mucho
mas amplia. Esto indica que T1 estabiliza la precision final frente a
condiciones iniciales distintas.

Los escenarios con mayor reduccion de error fueron:

| Escenario | Reduccion media de error |
|---|---:|
| S03 | 0.7652 m |
| S07 | 0.7436 m |
| S04 | 0.7377 m |

Los escenarios con menor reduccion de error fueron:

| Escenario | Reduccion media de error |
|---|---:|
| S05 | 0.3220 m |
| S02 | 0.3629 m |
| S01 | 0.3792 m |

La diferencia entre estos grupos no significa que T1 falle en los escenarios
con menor reduccion. Significa que en esos escenarios T0 ya presentaba errores
menores, por lo que la mejora absoluta disponible era mas baja. En cambio, en
escenarios con mayor error base, T1 tiene mas margen para corregir.

## Papel del desplazamiento lateral

El factor experimental con mayor influencia practica fue el desplazamiento
lateral inicial. Con desplazamiento `0.4 m`, la reduccion media de error fue
`0.3808 m`; con desplazamiento `0.8 m`, fue `0.7442 m`.

Este resultado sugiere que T1 es especialmente util cuando el error lateral
inicial es mayor. En esos casos, el descenso base T0 acumula errores finales
mas altos, mientras que la asistencia visual de T1 puede corregir la posicion
durante la aproximacion.

Sin embargo, el desplazamiento `0.8 m` tambien aumento el costo temporal. El
delta medio de tiempo `T0 - T1` paso de `-6.5286 s` con `0.4 m` a `-9.9710 s`
con `0.8 m`. Esto confirma que la correccion visual tiene un costo proporcional
a la exigencia de la condicion inicial.

Desde la perspectiva del framework, este hallazgo es valioso: el sistema no
solo funciona mejor en promedio, sino que su utilidad practica aumenta en los
casos donde la correccion es mas necesaria.

## Papel de la altura y del yaw inicial

La altura inicial mostro un efecto mucho menos marcado que el desplazamiento
lateral. La reduccion media de error fue muy similar:

- `0.5612 m` para altura `2 m`.
- `0.5637 m` para altura `3 m`.

Esto sugiere que, dentro de las alturas evaluadas, la ventaja de T1 en
precision final se mantiene estable.

El yaw inicial de `15 grados` produjo una reduccion media de error ligeramente
mayor que yaw `0 grados`:

- `0.5525 m` con yaw `0`.
- `0.5725 m` con yaw `15`.

La diferencia existe, pero es moderada frente al efecto del desplazamiento
lateral. Por tanto, la discusion debe evitar atribuir al yaw un papel
dominante. En el conjunto evaluado, el desplazamiento lateral explica mejor los
escenarios de mayor mejora y mayor costo temporal.

## Incidencias y fuentes de error

El analisis de incidencias ayuda a interpretar por que T1 mejora la precision y
por que su mejora no debe entenderse como ausencia de limitaciones.

T0 presento:

- mas perdidas de deteccion;
- mayor latencia media;
- latencias extremas superiores a `500 ms`;
- errores finales maximos cercanos a `0.8895 m`;
- ausencia de correccion horizontal activa.

T1 presento:

- deteccion aceptada casi completa;
- menor error final maximo (`0.0473 m`);
- mayor tiempo de aterrizaje;
- comandos horizontales activos de hasta `0.1000 m/s`;
- mayor dispersion visual en escenarios exigentes.

La lectura metodologica es que T1 reduce algunas fuentes de error asociadas a
precision y deteccion, pero introduce otras variables que deben vigilarse:
tiempo, actividad de control y posible oscilacion durante la correccion.

En particular, los escenarios S03, S04, S07 y S08 concentraron senales
relevantes de incidencia. Estos escenarios coinciden con condiciones mas
exigentes, especialmente desplazamiento lateral de `0.8 m`. Esto refuerza la
idea de que T1 es mas util cuando la condicion inicial es mas dificil, pero
tambien mas activo y costoso en esos mismos casos.

## Interpretacion de la dinamica lateral

La dinamica lateral del descenso no debe reducirse solo a la ausencia de
abortos. Aunque todos los aterrizajes aceptados terminaron en `land_complete`,
las metricas intermedias muestran diferencias importantes en el proceso.

T0 tiene menor actividad de control horizontal porque no corrige visualmente,
pero eso no implica mayor calidad de aterrizaje. De hecho, su menor actividad
se acompana de errores finales mas altos.

T1 tiene mayor actividad de correccion y cierta dispersion visual durante la
aproximacion, pero logra errores finales mucho menores. En consecuencia, HE3
debe leerse como evidencia de modificacion dinamica: T1 corrige mas, tarda mas
y termina mas cerca del objetivo.

## Significado para el framework AirSim-PX4

Los resultados respaldan el valor del framework AirSim-PX4 como entorno de
evaluacion controlada para comparar tratamientos de aterrizaje. La estructura
T0/T1 permitio aislar el efecto de la asistencia visual bajo escenarios
repetibles, con trazabilidad de corridas, pares, metricas e incidencias.

El aporte metodologico principal no es solamente haber obtenido un buen
resultado para T1. El aporte esta en haber construido una cadena reproducible:

```text
escenarios -> corridas -> logs -> metricas -> pares T0/T1 -> pruebas -> discusion
```

Esa cadena permite defender los resultados de forma mas solida que una
demostracion aislada. Tambien permite identificar limites, costos y condiciones
donde el tratamiento visual es mas beneficioso.

## Alcance real de los resultados

Los resultados deben interpretarse dentro del alcance definido para la tesis:
simulacion AirSim-PX4 con plataforma senalizada mediante ArUco y condiciones
experimentales controladas.

No corresponde afirmar que el sistema esta listo para vuelo fisico real. El
experimento no evalua:

- viento fisico;
- vibracion de sensores reales;
- variaciones amplias de iluminacion;
- oclusion del marcador;
- terrenos naturales no preparados;
- diferentes camaras o drones;
- fallas reales de comunicacion;
- incertidumbre aerodinamica externa al simulador.

Por ello, la conclusion correcta es que T1 mejora de forma significativa la
precision final dentro del framework simulado evaluado. La validacion fisica
queda como una etapa posterior y no debe confundirse con los resultados
presentes.

## Implicaciones para la tesis

Los hallazgos sostienen una conclusion equilibrada:

1. El framework permite ejecutar y analizar comparaciones T0/T1 de forma
   reproducible.
2. La asistencia visual T1 mejora significativamente la precision final.
3. La mejora se mantiene en todos los escenarios formales.
4. La mayor utilidad practica aparece con desplazamiento lateral inicial alto.
5. La mejora de precision implica mayor tiempo de aterrizaje.
6. La tasa de exito no diferencia a los tratamientos porque ambos completaron
   todas las corridas aceptadas.
7. Las incidencias intermedias muestran que el sistema tiene limites y costos,
   aunque no haya abortos en el conjunto formal.

Esta interpretacion es metodologicamente mas fuerte que afirmar simplemente
que T1 es superior. T1 es superior en precision bajo las condiciones evaluadas
y modifica de forma significativa la dinamica lateral; T0 es mas rapido, pero
menos preciso; ambos aterrizan con exito en simulacion.

## Riesgos de interpretacion

Para mantener rigor academico, deben evitarse las siguientes interpretaciones:

- Afirmar que T1 es universalmente mejor en todos los criterios.
- Presentar el 100% de exito como prueba de validez en vuelo real.
- Ignorar el costo temporal de T1.
- Confundir baja tasa de abortos con ausencia de incidencias.
- Generalizar resultados de AirSim-PX4 a cualquier dron o entorno fisico.
- Tratar el detector ArUco como una contribucion nueva si el aporte real esta
  en la integracion, evaluacion y trazabilidad experimental.

La discusion debe conservar el equilibrio entre evidencia positiva y
delimitacion metodologica.

## Sintesis de la discusion

El experimento muestra que la asistencia visual T1 mejora de forma significativa
la precision final del aterrizaje frente a T0, con una reduccion media de error
de `0.5625 m` y errores finales medios cercanos a `0.02 m`. Esta mejora es
consistente en los ocho escenarios y se acentua cuando el desplazamiento
lateral inicial es mayor.

El beneficio viene acompanado de un costo temporal medio de aproximadamente
`8.2498 s` adicionales. Este costo es coherente con el proceso de alineacion y
correccion visual. T1 tambien mejora la disponibilidad de deteccion, pero
mantiene actividad de control que debe considerarse al discutir la dinamica
lateral y posibles fuentes de oscilacion.

Como ambos tratamientos alcanzaron 100% de exito en el conjunto aceptado, la
diferencia cientificamente relevante no esta en aterrizar o no aterrizar, sino
en como aterrizan: con que precision, en cuanto tiempo, con que calidad de
deteccion, con que actividad correctiva y bajo que incidencias.

En consecuencia, los resultados apoyan la utilidad del framework AirSim-PX4
para evaluar aterrizaje asistido por vision en simulacion controlada, y muestran
que T1 es una estrategia mas precisa que T0 bajo el protocolo formal. Al mismo
tiempo, los resultados delimitan claramente el alcance: no sustituyen una
validacion fisica y no deben extrapolarse fuera de las condiciones simuladas
evaluadas.

## Criterio de salida

Este entregable queda completo porque:

- integra estadistica descriptiva, contraste de hipotesis, escenarios e
  incidencias;
- interpreta el efecto principal de T1 sobre precision final;
- discute el costo temporal de la asistencia visual;
- diferencia precision final de exito terminal;
- explica el papel del desplazamiento lateral, altura y yaw;
- incorpora fuentes de error e incidencias tecnicas;
- delimita el alcance real del framework AirSim-PX4;
- prepara la transicion hacia el entregable de limitaciones y alcance.

El siguiente entregable debe formalizar las limitaciones del estudio y el
alcance metodologico del framework evaluado.
