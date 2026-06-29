# Fase 06 - Conclusiones

## Proposito

Este documento presenta las conclusiones finales de la Fase 06 a partir de la
base experimental formal, los analisis estadisticos, el analisis por escenario,
la revision de incidencias y el perfil del proyecto de investigacion.

El perfil plantea como objetivo general desarrollar y evaluar un framework
reproducible AirSim-PX4 para estudiar el aterrizaje autonomo de un UAV asistido
por vision Offboard sobre una plataforma senalizada, en un entorno controlado
de simulacion, mediante metricas de precision final, tiempo de aterrizaje,
dinamica lateral de aproximacion y tasa de exito. Las conclusiones de esta fase se
formulan directamente contra ese marco.

El cierre no busca afirmar que el sistema esta validado para vuelo fisico real,
sino establecer que se obtuvo una evaluacion experimental reproducible,
trazable y cuantitativa dentro de AirSim-PX4.

## Base de evidencia

Las conclusiones se sustentan en el conjunto formal auditado:

- `160` corridas aceptadas.
- `80` corridas T0.
- `80` corridas T1.
- `80` pares T0/T1.
- `8` escenarios formales (`S01` a `S08`).
- `10` pares por escenario.
- `0` abortos en el conjunto aceptado.

La base fue consolidada antes del analisis estadistico y no mezcla corridas
`excluded` ni `superseded` con el bloque formal T0/T1. Esto preserva la
comparabilidad entre tratamientos y permite que las conclusiones se apoyen en
un diseno pareado.

## Conclusion sobre el objetivo general

El objetivo general queda cumplido dentro del alcance declarado. Se desarrollo
y evaluo un framework reproducible AirSim-PX4 para estudiar el aterrizaje
autonomo asistido por vision Offboard sobre una plataforma senalizada en
simulacion controlada.

La evaluacion no se limito a demostrar funcionamiento tecnico. El framework
permitio:

- ejecutar escenarios controlados;
- comparar T0 y T1 bajo condiciones equivalentes;
- registrar telemetria, percepcion, comandos y estados terminales;
- curar datos por corrida;
- construir pares T0/T1;
- calcular metricas de desempeno;
- aplicar pruebas estadisticas pareadas;
- analizar incidencias y fuentes de error;
- delimitar el alcance metodologico de los resultados.

Por tanto, el aporte principal del proyecto se confirma como una contribucion
metodologica y experimental: una estructura reproducible para evaluar si la
asistencia visual Offboard modifica el desempeno del aterrizaje, no un nuevo
detector visual, no una nueva ley universal de control y no una validacion
fisica definitiva.

## Conclusion sobre la hipotesis general

La hipotesis general del perfil plantea que el framework AirSim-PX4 con
asistencia visual Offboard produce diferencias significativas en el desempeno
del aterrizaje autonomo frente a un descenso base sin correccion visual
inteligente, bajo condiciones controladas de simulacion.

La evidencia permite sostener esta hipotesis general de manera matizada:

- si se considera el desempeno como precision final, tiempo y dinamica lateral
  de aproximacion, T1 produce diferencias claras y estadisticamente
  significativas frente a T0;
- si se considera la proporcion de exito/fallo, no se observa diferencia,
  porque ambos tratamientos alcanzan `80/80` aterrizajes exitosos;
- si se considera la disponibilidad visual como metrica de apoyo, T1 mantiene
  una deteccion aceptada muy superior a T0 durante la maniobra.

En consecuencia, el framework si demuestra diferencias significativas de
desempeno, pero esas diferencias deben describirse con precision: T1 mejora la
precision final, incrementa el tiempo de maniobra, modifica significativamente
la dinamica lateral de aproximacion y no modifica la tasa de exito/fallo dentro
del conjunto aceptado.

## Conclusiones por hipotesis especifica

### HE1 - Error final de posicionamiento

La HE1 queda respaldada.

En escenarios iniciales equivalentes, T1 presenta menor error de
posicionamiento final respecto del centro de la plataforma senalizada que T0.
La media de error final fue:

| Tratamiento | Error final medio |
|---|---:|
| T0 | 0.5831 m |
| T1 | 0.0206 m |

La diferencia pareada media `T0 - T1` fue `0.5625 m`. La prueba Wilcoxon
signed-rank rechazo la hipotesis nula (`p = 3.92476e-15`) y el tamano del
efecto fue alto (`Cohen dz = 2.85113`).

La conclusion es que la asistencia visual Offboard reduce de manera
estadisticamente significativa y practicamente relevante el error final de
aterrizaje en simulacion AirSim-PX4.

### HE2 - Tiempo de aterrizaje

La HE2 queda respaldada en el sentido de que T1 modifica significativamente el
tiempo total de aterrizaje.

La media de tiempo fue:

| Tratamiento | Tiempo medio |
|---|---:|
| T0 | 20.6399 s |
| T1 | 28.8897 s |

La diferencia pareada media `T0 - T1` fue `-8.2498 s`. La prueba t pareada
rechazo la hipotesis nula (`p = 2.01596e-42`).

La conclusion no es que T1 sea temporalmente mas eficiente, sino que T1 tarda
mas. El incremento de tiempo se interpreta como costo operacional de la
correccion visual: el sistema invierte mas tiempo para alinear el UAV con la
plataforma y reducir el error final.

### HE3 - Dinamica lateral de aproximacion

La HE3 queda respaldada. La asistencia visual Offboard produce una diferencia
significativa en la dinamica lateral de aproximacion del UAV respecto del
tratamiento base, medida mediante la dispersion del error visual o lateral y la
actividad correctiva durante el descenso.

En el indicador de dispersion visual/lateral combinada, la media observada fue:

| Tratamiento | Dispersion visual combinada media |
|---|---:|
| T0 | 0.0642 |
| T1 | 0.0869 |

La diferencia pareada media `T0 - T1` fue `-0.0227`, lo que indica mayor
dispersion visual combinada en T1. La prueba Wilcoxon signed-rank bilateral
rechazo la hipotesis nula (`p = 0.0271772`).

La actividad correctiva tambien mostro diferencias significativas:

| Indicador HE3 | Diferencia media | Prueba | p-valor |
|---|---:|---|---:|
| Conteo de comandos `T1 - T0` | 46.6625 | t pareada | 7.4351e-42 |
| Maximo comando horizontal `T1 - T0` | 0.0674 m/s | Wilcoxon signed-rank | 7.39174e-15 |

Esta conclusion debe interpretarse como cambio dinamico, no como superioridad
en todos los criterios de trayectoria. T1 corrige mas, genera comandos
horizontales mas intensos y presenta mayor dispersion visual/lateral durante la
aproximacion. Esa dinamica activa es coherente con el menor error final de HE1
y con el mayor tiempo de maniobra de HE2.

### HE4 - Proporcion de exito/fallo

La HE4 no queda respaldada.

La asistencia visual Offboard no modifico significativamente la proporcion de
corridas exitosas, abortadas o fallidas frente a T0 dentro del conjunto formal,
porque ambos tratamientos alcanzaron exito completo:

| Resultado pareado | Conteo |
|---|---:|
| T0 exito / T1 exito | 80 |
| T0 exito / T1 fallo | 0 |
| T0 fallo / T1 exito | 0 |
| T0 fallo / T1 fallo | 0 |

La prueba de McNemar exacta produjo `p = 1`. Por tanto, no existe evidencia de
diferencia en exito/fallo.

La conclusion correcta es que la diferencia principal entre T0 y T1 no esta en
la capacidad basica de aterrizar, sino en la precision final, el tiempo de
maniobra, la disponibilidad de deteccion y la dinamica de correccion.

## Conclusion sobre metricas de apoyo

La tasa de deteccion aceptada constituye una metrica de apoyo importante para
interpretar el comportamiento tecnico del framework.

T1 presento una tasa media de deteccion aceptada de `0.9978`, frente a
`0.6889` en T0. Ademas, T0 tuvo una media de `21.8750` perdidas de deteccion,
mientras que T1 tuvo `0.2500`.

Esto permite concluir que T1 mejora la disponibilidad de informacion visual
durante la maniobra. La deteccion mas completa alimenta la correccion visual,
y esa correccion se refleja en la mayor actividad dinamica reportada en HE3.

## Conclusion sobre el analisis por escenario

T1 redujo el error final medio en los ocho escenarios formales. Esto demuestra
que la mejora de precision no depende de un unico escenario aislado.

Los escenarios con mayor reduccion media de error fueron:

| Escenario | Reduccion media de error |
|---|---:|
| S03 | 0.7652 m |
| S07 | 0.7436 m |
| S04 | 0.7377 m |

Los escenarios con menor reduccion media fueron:

| Escenario | Reduccion media de error |
|---|---:|
| S05 | 0.3220 m |
| S02 | 0.3629 m |
| S01 | 0.3792 m |

La mayor utilidad practica de T1 aparece cuando el desplazamiento lateral
inicial es `0.8 m`. En esa condicion, la reduccion media de error fue
`0.7442 m`, frente a `0.3808 m` con desplazamiento `0.4 m`.

La conclusion por escenario es que T1 es especialmente valioso cuando el error
lateral inicial es mayor, aunque tambien aumenta el costo temporal de la
maniobra.

## Conclusion sobre incidencias y fuentes de error

El conjunto aceptado no presento abortos ni estados terminales divergentes:
todas las corridas terminaron como `land_complete`. Sin embargo, las
incidencias intermedias muestran diferencias importantes entre tratamientos.

T0 presento:

- mas perdidas de deteccion;
- mayor latencia media;
- latencias maximas superiores a `500 ms`;
- errores finales extremos cercanos a `0.8895 m`;
- ausencia de correccion horizontal activa.

T1 presento:

- deteccion aceptada casi completa;
- menor error final maximo (`0.0473 m`);
- mayor tiempo de aterrizaje;
- comandos horizontales activos de hasta `0.1000 m/s`;
- mayor dispersion visual en escenarios exigentes.

La conclusion es que T1 reduce fuentes de error asociadas a precision final y
disponibilidad visual, pero introduce un costo dinamico: mayor tiempo, mayor
actividad de control y mayor dispersion visual durante la aproximacion. Este
resultado es coherente con una estrategia de correccion activa.

## Conclusion sobre el alcance del framework

El framework queda validado como herramienta experimental reproducible en
simulacion AirSim-PX4. Su valor esta en permitir una evaluacion controlada,
pareada y trazable del efecto de la asistencia visual Offboard sobre el
aterrizaje autonomo.

El framework no queda validado como:

- sistema listo para vuelo fisico real;
- detector visual nuevo;
- ley universal de control;
- solucion general para cualquier plataforma o entorno;
- sustituto de pruebas con hardware real.

La conclusion debe mantenerse dentro del alcance declarado en el perfil: una
evaluacion en simulacion controlada sobre una plataforma senalizada.

## Conclusion sobre los objetivos especificos del perfil

Los objetivos especificos del perfil quedan articulados de la siguiente forma:

| Objetivo especifico | Conclusion de cierre |
|---|---|
| Definir arquitectura funcional AirSim-PX4 | Cumplido mediante la integracion de simulacion, percepcion, Offboard, PX4, telemetria y trazabilidad. |
| Implementar percepcion visual | Cumplido como componente operativo para identificar la plataforma senalizada y producir informacion visual util. |
| Integrar asistencia visual Offboard con PX4 y AirSim | Cumplido; T1 ejecuto correcciones durante la aproximacion y produjo efectos medibles. |
| Establecer protocolo reproducible T0/T1 | Cumplido; se ejecutaron 160 corridas aceptadas, 80 pares y 8 escenarios con 10 repeticiones. |
| Calcular y comparar metricas de desempeno | Cumplido; se analizaron error final, tiempo, dinamica lateral, actividad correctiva, exito, deteccion e incidencias. |
| Examinar resultados, incidencias y fuentes de error | Cumplido; se identificaron beneficios, costos, limites tecnicos y alcance metodologico. |

Esta relacion muestra que la Fase 06 no cierra solo un analisis estadistico,
sino el argumento experimental del proyecto.

## Conclusion general de Fase 06

La Fase 06 confirma que la asistencia visual Offboard T1 mejora de forma
significativa la precision final del aterrizaje frente al descenso base T0 en
un entorno AirSim-PX4 controlado. La mejora es consistente en los ocho
escenarios formales y es especialmente marcada cuando el desplazamiento lateral
inicial es mayor.

Al mismo tiempo, T1 incrementa significativamente el tiempo de aterrizaje,
modifica significativamente la dinamica lateral de aproximacion y no modifica
la tasa de exito/fallo, porque ambos tratamientos completaron todas las
corridas aceptadas. La mayor actividad correctiva de T1 explica que el sistema
tarde mas y presente mayor dispersion visual/lateral durante la aproximacion,
aunque termine con mucha mayor precision.

Por tanto, la conclusion final no debe formularse como una superioridad absoluta
de T1 en todos los criterios. La formulacion defendible es:

```text
T1 es significativamente mas preciso que T0 y mantiene exito terminal completo
en simulacion AirSim-PX4, pero requiere mayor tiempo de maniobra y modifica la
dinamica lateral de aproximacion mediante mayor actividad correctiva.
```

Esta conclusion es consistente con el perfil del proyecto, porque reconoce el
problema como una evaluacion experimental del efecto de la asistencia visual,
no como una solucion universal de aterrizaje autonomo.

## Trabajo futuro

A partir de estas conclusiones, las lineas de trabajo futuro mas relevantes
son:

- validar el framework en hardware fisico;
- evaluar condiciones visuales mas variables;
- incorporar oclusion parcial del marcador;
- comparar ArUco con otros detectores o referencias visuales;
- optimizar el compromiso precision-tiempo;
- analizar estabilidad formal del controlador visual;
- evaluar escenarios con mayor diversidad de desplazamientos, alturas y yaw;
- medir consumo energetico y robustez frente a perturbaciones;
- estudiar estrategias para reducir dispersion durante la correccion activa de
  T1.

Estas extensiones ampliarian la validez externa del framework y permitirian
pasar de una validacion simulada controlada hacia etapas progresivas de
validacion fisica.

## Criterio de salida

Este entregable queda completo porque:

- responde al objetivo general del perfil;
- responde a las hipotesis especificas HE1 a HE4;
- distingue resultados respaldados, no respaldados y metricas de apoyo;
- integra precision, tiempo, dinamica lateral, exito, deteccion e incidencias;
- formula una conclusion general equilibrada;
- delimita el alcance del framework;
- propone trabajo futuro coherente con las limitaciones identificadas.

El siguiente entregable debe construir la ayuda memoria de Fase 06 con scripts,
comandos, archivos generados, decisiones metodologicas y resultados clave.
