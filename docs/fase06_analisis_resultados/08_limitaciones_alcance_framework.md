# Fase 06 - Limitaciones y Alcance del Framework

## Proposito

Este documento delimita el alcance metodologico del framework AirSim-PX4
evaluado en la Fase 06 y explicita las principales limitaciones del estudio.
Su finalidad es precisar que afirmaciones pueden sostenerse a partir de los
resultados obtenidos y cuales deben quedar fuera del alcance experimental.

La delimitacion no reduce el valor de los resultados. Al contrario, fortalece
su interpretacion academica, porque evita extrapolaciones no justificadas y
ubica la contribucion real del trabajo dentro de las condiciones efectivamente
evaluadas.

## Relacion con los resultados previos

Los entregables anteriores muestran que:

- T1 reduce significativamente el error final de aterrizaje frente a T0.
- T1 incrementa significativamente el tiempo de aterrizaje.
- T1 modifica significativamente la dinamica lateral de aproximacion mediante
  mayor dispersion visual/lateral, mayor actividad correctiva y mayor
  intensidad de comando horizontal.
- T1 mejora la tasa de deteccion aceptada como metrica de apoyo para interpretar
  el comportamiento tecnico del framework.
- T0 y T1 no difieren en exito/fallo porque ambos alcanzan `80/80`
  aterrizajes exitosos en el conjunto formal.
- La mejora de T1 se mantiene en los ocho escenarios evaluados.
- El desplazamiento lateral inicial de `0.8 m` es la condicion donde T1 muestra
  mayor utilidad practica.
- No se registraron abortos en las corridas aceptadas, aunque si existieron
  incidencias intermedias como perdidas de deteccion, latencias y mayor
  actividad de correccion visual.

Estas conclusiones son validas dentro del protocolo experimental definido. El
presente documento establece los limites dentro de los cuales deben ser leidas.

## Alcance validado

El estudio valida experimentalmente, en simulacion, un framework de comparacion
T0/T1 para aterrizaje asistido por vision bajo AirSim-PX4.

El alcance validado incluye:

- ejecucion de corridas formales en entorno simulado;
- comparacion pareada entre T0 y T1;
- uso de plataforma senalizada mediante marcador ArUco;
- integracion de percepcion visual, comandos MAVLink y entorno AirSim-PX4;
- generacion de logs, metricas, tablas y reportes reproducibles;
- analisis de error final, tiempo, dinamica lateral, actividad correctiva,
  deteccion, exito, incidencias y escenarios;
- trazabilidad entre escenario, tratamiento, repeticion, corrida y resultado.

En este marco, la afirmacion principal defendible es que T1 mejora la precision
final del aterrizaje frente a T0 bajo las condiciones simuladas evaluadas.

## Afirmaciones permitidas

A partir de la evidencia generada, se pueden sostener las siguientes
afirmaciones:

- En simulacion AirSim-PX4, T1 reduce significativamente el error final frente
  a T0.
- T1 requiere mayor tiempo de aterrizaje que T0 en el protocolo formal
  evaluado.
- T1 modifica significativamente la dinamica lateral de aproximacion frente a
  T0 mediante mayor actividad correctiva.
- T1 mejora la disponibilidad de deteccion aceptada frente a T0 como metrica de
  apoyo.
- Ambos tratamientos alcanzan aterrizaje exitoso en las 80 corridas pareadas
  aceptadas.
- La mejora de T1 es consistente en los escenarios `S01` a `S08`.
- La mejora absoluta de T1 es mayor cuando el desplazamiento lateral inicial es
  `0.8 m`.
- El framework permite una comparacion reproducible y trazable entre un
  descenso base y un tratamiento visual asistido.

Estas afirmaciones deben mantener siempre la referencia al entorno simulado y
al protocolo usado.

## Afirmaciones no permitidas

Los resultados no autorizan afirmar que:

- el sistema esta listo para vuelo fisico real;
- T1 es universalmente superior a T0 en todos los criterios;
- el framework funciona con cualquier dron, camara, marcador o entorno;
- el detector visual propuesto es nuevo o generalizable a cualquier condicion;
- la ausencia de abortos en simulacion equivale a seguridad operacional real;
- el controlador visual es una ley de control universal;
- el resultado se mantiene bajo viento, vibracion, oclusion, iluminacion
  variable o fallas fisicas;
- AirSim-PX4 sustituye la validacion experimental con hardware real.

Estas afirmaciones requeririan experimentos adicionales fuera del alcance de la
fase actual.

## Validez interna

La validez interna del estudio es fuerte dentro del diseno planteado, porque:

- la base formal esta cerrada y auditada;
- existen `160` corridas aceptadas y `80` pares T0/T1;
- cada escenario cuenta con `10` repeticiones por tratamiento;
- las condiciones T0/T1 se comparan mediante pares por escenario y repeticion;
- las pruebas estadisticas respetan el diseno pareado;
- las corridas `excluded` y `superseded` no se usan para promedios ni
  contrastes;
- las tablas y reportes se generan mediante scripts reproducibles.

Esto permite atribuir las diferencias observadas al tratamiento evaluado dentro
del protocolo definido, con una trazabilidad adecuada entre datos y
conclusiones.

## Limites de validez externa

La validez externa es limitada. Los resultados no deben generalizarse
automaticamente a:

- vuelos fisicos con un UAV real;
- otros modelos de dron;
- otras camaras o configuraciones opticas;
- otros marcadores visuales;
- plataformas de aterrizaje no senalizadas;
- terrenos naturales o no preparados;
- ambientes exteriores;
- condiciones meteorologicas variables;
- escenarios con oclusion parcial o total del marcador;
- condiciones de iluminacion no evaluadas.

La simulacion ofrece control experimental, repetibilidad y trazabilidad, pero
no reproduce toda la complejidad fisica de un vuelo real.

## Limitaciones del entorno AirSim-PX4

AirSim-PX4 permite evaluar de forma controlada la integracion entre entorno
simulado, autopiloto, percepcion y comandos. Sin embargo, su naturaleza
simulada impone limites:

- la dinamica fisica no equivale completamente a la de un UAV real;
- no se modelan todos los efectos de viento, turbulencia o vibracion;
- el comportamiento de sensores simulados puede ser mas estable que el de
  sensores fisicos;
- las condiciones de iluminacion y textura son controladas;
- las fallas de comunicacion reales no estan representadas en toda su
  complejidad;
- la respuesta del sistema depende de la configuracion especifica del entorno.

Por tanto, AirSim-PX4 debe interpretarse como un banco de evaluacion
experimental controlado, no como sustituto definitivo de pruebas fisicas.

## Limitaciones de la plataforma senalizada

El estudio usa una plataforma de aterrizaje senalizada mediante ArUco. Esto
delimita el tipo de problema evaluado.

El framework no demuestra aterrizaje autonomo sobre:

- superficies naturales no preparadas;
- zonas sin marcador;
- plataformas con patrones visuales diferentes;
- superficies deformables o irregulares;
- marcadores parcialmente ocluidos;
- marcadores degradados, rotos o mal iluminados.

La contribucion se ubica en el aterrizaje asistido por vision sobre una
referencia visual preparada. Esta delimitacion es coherente con el objetivo de
comparar T0 y T1 bajo condiciones controladas.

## Limitaciones del detector visual

El detector ArUco se usa como componente de percepcion dentro del framework.
El estudio no propone un detector nuevo ni compara tecnicas alternativas de
percepcion.

No se evalua:

- robustez frente a oclusion severa;
- cambios extremos de iluminacion;
- ruido fisico de camara;
- desenfoque por movimiento real;
- marcadores deteriorados;
- falsos positivos en entornos complejos;
- comparacion con redes neuronales u otros detectores.

Por tanto, los resultados no deben presentarse como validacion general de un
metodo de deteccion visual, sino como evidencia del funcionamiento de una
integracion ArUco-MAVLink-AirSim-PX4 bajo el protocolo definido.

## Limitaciones del control visual

T1 usa comandos MAVLink directos para corregir la aproximacion visual. El
estudio demuestra que esta estrategia mejora la precision final en simulacion,
pero no establece una ley de control universal.

Las limitaciones principales son:

- las ganancias y parametros se evaluaron en escenarios acotados;
- no se demostro estabilidad formal mediante analisis teorico de control;
- no se evaluo respuesta ante perturbaciones fisicas externas;
- no se comparo contra otros controladores visuales;
- no se optimizo explicitamente el compromiso entre precision y tiempo;
- no se evaluo saturacion de comandos en condiciones mas extremas.

La evidencia disponible respalda la utilidad practica de T1 dentro del
framework, pero no convierte el controlador en una solucion general para todo
tipo de aterrizaje autonomo.

## Limitaciones de escenarios

Los escenarios formales `S01` a `S08` varian altura inicial, desplazamiento
lateral y yaw inicial. Esta matriz es suficiente para evaluar diferencias
controladas entre T0 y T1, pero no cubre todo el espacio posible de
condiciones.

No se evaluaron:

- alturas fuera de `2 m` y `3 m`;
- desplazamientos laterales fuera de `0.4 m` y `0.8 m`;
- yaw inicial fuera de `0` y `15` grados;
- desplazamientos en multiples ejes con mayor diversidad;
- condiciones de aproximacion oblicua mas complejas;
- trayectorias iniciales no previstas por el protocolo;
- variaciones dinamicas durante la aproximacion.

Por tanto, el analisis por escenario debe interpretarse como una evaluacion
factorial acotada, no como exploracion exhaustiva del espacio operacional.

## Limitaciones de metricas

Las metricas usadas permiten evaluar precision, tiempo, deteccion, latencia,
comandos, exito e incidencias. Sin embargo, no capturan todos los aspectos de
un aterrizaje autonomo.

Entre las metricas no cubiertas o no desarrolladas exhaustivamente se incluyen:

- consumo energetico;
- desgaste mecanico;
- suavidad fisica del contacto;
- vibracion real;
- robustez a viento;
- error bajo incertidumbre sensorial real;
- seguridad operacional ante fallas externas;
- confort dinamico de trayectoria;
- margen de estabilidad formal.

La interpretacion debe limitarse a las metricas efectivamente registradas y
analizadas.

## Limitaciones sobre dinamica lateral y estabilidad formal

El estudio analiza la dinamica lateral de aproximacion mediante indicadores
operacionales como dispersion visual/lateral, comandos, tiempo, deteccion y
ausencia de abortos. No se realiza una demostracion formal de estabilidad en el
sentido teorico de control.

Por tanto, puede afirmarse que T1 modifica de forma significativa la dinamica
lateral dentro del protocolo simulado, pero no que el sistema sea
matematicamente estable bajo cualquier condicion.

Esta distincion es importante para evitar sobreinterpretar la evidencia
experimental.

## Limitaciones del conjunto aceptado

El analisis formal usa solo corridas con:

```text
curation_status == accepted
```

Las corridas `excluded` y `superseded` no se incorporan a los promedios ni a
los contrastes. Esto es metodologicamente correcto para preservar comparabilidad,
pero tambien significa que el analisis formal describe el conjunto curado y
aceptado, no todas las ejecuciones historicas realizadas durante el desarrollo.

Las corridas excluidas y reemplazadas deben mantenerse como evidencia de
trazabilidad e incidencias, pero no como parte del bloque estadistico formal.

## Compromiso precision-tiempo

Una limitacion practica de T1 es el incremento del tiempo de aterrizaje. La
mejora de precision no ocurre sin costo:

- T1 reduce significativamente el error final.
- T1 mejora significativamente la deteccion aceptada.
- T1 tarda significativamente mas que T0.

Este compromiso debe considerarse al discutir posibles aplicaciones. Si la
prioridad es aterrizar con mayor precision sobre una plataforma senalizada, T1
resulta favorable. Si la prioridad es minimizar el tiempo de maniobra, T0 puede
ser mas rapido, aunque menos preciso.

El framework permite medir ese compromiso, pero no define por si solo cual
criterio debe priorizarse en una aplicacion real.

## Incidencias como limites tecnicos

Las incidencias observadas no invalidan el experimento, pero delimitan su
interpretacion:

- T0 presenta mas perdidas de deteccion y mayores errores finales.
- T0 presenta latencias extremas superiores a `500 ms` en algunas corridas.
- T1 presenta mayor tiempo de aterrizaje.
- T1 requiere comandos horizontales activos.
- T1 muestra mayor dispersion visual en escenarios exigentes.

Estas incidencias muestran que el desempeno del sistema depende de la calidad
de deteccion, la latencia y la dinamica de correccion. Por ello, cualquier
extension futura debe evaluar estos factores con mayor detalle.

## Aporte real del framework

El aporte real del framework no consiste en afirmar que se resolvio
definitivamente el aterrizaje autonomo de UAVs. El aporte consiste en:

- integrar AirSim, PX4, percepcion visual y comandos MAVLink;
- definir un protocolo T0/T1 reproducible;
- generar una matriz experimental cerrada;
- producir metricas comparables y trazables;
- contrastar hipotesis con diseno pareado;
- identificar beneficios y costos de la asistencia visual;
- documentar incidencias y fuentes de error.

Esta contribucion es metodologica y experimental. Su valor esta en permitir una
evaluacion controlada, no en sustituir todas las etapas posteriores de
validacion.

## Proyeccion metodologica

Las limitaciones identificadas sugieren lineas de trabajo posteriores:

- validar el sistema en hardware fisico;
- incorporar variaciones de iluminacion y textura;
- evaluar oclusion parcial del marcador;
- comparar ArUco con otros detectores;
- optimizar el compromiso precision-tiempo;
- analizar estabilidad formal del controlador visual;
- evaluar escenarios con mayor diversidad de desplazamientos y orientaciones;
- medir consumo energetico y robustez ante perturbaciones;
- incluir pruebas con diferentes camaras y configuraciones de UAV.

Estas extensiones no son requisitos para validar la fase actual, pero si
marcan el camino para ampliar la validez externa del framework.

## Formulacion academica recomendada

La formulacion adecuada para la tesis es:

```text
Los resultados demuestran que, bajo condiciones simuladas controladas en
AirSim-PX4, el tratamiento T1 reduce significativamente el error final de
aterrizaje frente a T0 y mejora la deteccion aceptada, a costa de un mayor
tiempo de maniobra. Estos resultados validan el framework como herramienta de
evaluacion experimental en simulacion, pero no sustituyen una validacion fisica
en UAV real.
```

Esta formulacion conserva el valor del resultado y delimita correctamente su
alcance.

## Criterio de salida

Este entregable queda completo porque:

- define el alcance validado del framework;
- distingue afirmaciones permitidas y no permitidas;
- discute validez interna y externa;
- delimita simulacion, detector, control, escenarios y metricas;
- identifica el compromiso precision-tiempo;
- relaciona incidencias con limites tecnicos;
- precisa el aporte metodologico real;
- propone lineas de extension futura;
- prepara la transicion hacia las conclusiones de Fase 06.

El siguiente entregable debe sintetizar las conclusiones de Fase 06 y responder
explicitamente a las hipotesis y al objetivo de la fase.
