# Justificacion Academica de la Eleccion del Marcador Fiduciario ArUco

## Proposito del documento

Este documento sustenta la decision metodologica de emplear un marcador
fiduciario ArUco como referencia visual principal en la Fase 04 del proyecto
UAV Landing AI. La justificacion se formula en dos niveles: primero, frente a
un marcador basado solo en color/HSV; segundo, frente a otros sistemas de
marcadores fiduciarios planos, especialmente AprilTag. La decision se evalua
en funcion del objetivo de la fase: integrar percepcion visual, PX4,
telemetria y logica de control para un aterrizaje autonomo asistido por vision
en AirSimNH. La ruta activa final de control en Fase 04 se consolido mediante
MAVLink directo con `pymavlink`, despues de documentar la limitacion del plugin
Offboard de MAVSDK en la configuracion local.

## Contexto metodologico

El aterrizaje autonomo basado en vision requiere que el UAV identifique una
referencia visual en la escena, estime su posicion relativa en la imagen y
transforme esa informacion en acciones de guiado o control. La literatura
reciente sobre aterrizaje visual de UAV senala que la vision por computador es
una alternativa atractiva por su autonomia, bajo costo y capacidad de operar
como complemento de otros sistemas de navegacion, aunque tambien introduce
retos de robustez, precision, iluminacion y complejidad computacional (Xin et
al., 2022). En revisiones especificas sobre navegacion visual para UAV, estos
retos se relacionan directamente con la estabilidad del modulo perceptivo, la
integracion con el controlador y la calidad de la referencia visual utilizada
(Arafat et al., 2023).

En este proyecto, el marcador HSV/color implementado en Fase 03 cumplio una
funcion instrumental: validar el flujo de captura de imagen, segmentacion,
calculo de error visual, generacion de imagenes anotadas y registro de
resultados. Sin embargo, para la Fase 04 se requiere una referencia visual mas
trazable, reproducible y defendible experimentalmente, ya que la salida de
percepcion se convierte en entrada de una logica de control conectada al
autopiloto. En ese contexto, los marcadores fiduciarios planos resultan
pertinentes porque permiten resolver problemas de identificacion y localizacion
monocular mediante patrones artificiales de bajo costo computacional
(Jurado-Rodríguez et al., 2023).

## ArUco frente a marcador HSV/color

La principal limitacion de un marcador HSV/color es que la deteccion se basa en
propiedades cromaticas o de contorno, no en una identidad codificada. Esto
significa que una region de color similar, una textura del entorno o una
variacion de iluminacion puede producir respuestas ambiguas. Para una fase de
percepcion aislada, esa estrategia es suficiente si el entorno esta controlado;
para una fase de integracion con autopiloto, en cambio, la ausencia de un ID
verificable debilita la trazabilidad experimental.

Los marcadores fiduciarios planos, por definicion, incorporan un patron
interno que permite identificar de manera unica el marcador detectado
(Jurado-Rodríguez et al., 2023). En el caso de ArUco, el sistema propuesto por
Garrido-Jurado et al. (2014) se basa en diccionarios configurables de
marcadores binarios cuadrados, con criterios orientados a maximizar la
distancia entre marcadores y reducir confusiones. Esta caracteristica es
especialmente util para el presente proyecto porque permite fijar de antemano
un diccionario y un identificador, en este caso `DICT_4X4_50`, ID `23`, y
verificar en el log que la deteccion corresponde al marcador esperado.

La comparacion con enfoques puramente cromaticos tambien puede justificarse por
robustez operacional. Olson (2011) senala, al discutir sistemas previos de
marcadores, que los esquemas basados en umbralizacion simple pueden ser rapidos
pero menos robustos frente a cambios de iluminacion. De manera complementaria,
el estudio comparativo de Jurado-Rodríguez et al. (2023) reporta que algunos
sistemas basados en informacion de color, como ChromaTag, son sensibles a
cambios de iluminacion. Aunque el detector HSV de este proyecto no es
equivalente a ChromaTag, ambos comparten una dependencia relevante respecto de
la informacion cromatica. Por tanto, migrar a un marcador binario fiduciario
reduce la dependencia del color como criterio primario de identificacion.

En sintesis, ArUco supera al marcador HSV/color en esta fase porque aporta:

- identidad verificable del marcador;
- menor ambiguedad semantica que una region de color;
- compatibilidad con imagenes anotadas y logs trazables;
- continuidad con el calculo de error visual ya implementado;
- potencial de evolucion hacia estimacion de pose si la fase experimental lo
  requiere.

## ArUco frente a otros marcadores fiduciarios

La eleccion de ArUco no implica que sea universalmente superior a todos los
sistemas fiduciarios. AprilTag, por ejemplo, es una alternativa solida y
ampliamente reconocida. Olson (2011) presenta AprilTag como un sistema robusto
y flexible, capaz de proporcionar localizacion 6-DoF desde una imagen y
diseñado para operar en condiciones de baja resolucion, rotacion, iluminacion
no uniforme y escenas con desorden visual. Por tanto, desde una perspectiva
puramente algoritmica, AprilTag constituye una opcion valida para aplicaciones
de robotica y vision.

La seleccion debe realizarse, sin embargo, segun los requisitos concretos del
proyecto. Jurado-Rodríguez et al. (2023) comparan sistemas fiduciarios planos
en terminos de sensibilidad, especificidad, exactitud, costo computacional,
robustez ante oclusion y velocidad. En su estudio, ArUco y ArUco3 aparecen
como alternativas relevantes por disponibilidad, documentacion, capacidad de
estimacion de pose y mantenimiento. El mismo estudio indica que ArUco esta
integrado en el repositorio OpenCV-Contrib, mientras que ArUco3 se describe
como accesible y documentado. Para este proyecto, ese aspecto de integracion es
decisivo: el stack experimental ya utiliza OpenCV, Python y un entorno `.venv`
en Windows, por lo que ArUco reduce la incorporacion de dependencias externas.

El criterio computacional tambien favorece a la familia ArUco en este contexto.
Jurado-Rodríguez et al. (2023) reportan que ArUco3, ArUco, Jumarker y STag se
encuentran entre los sistemas con mayor tasa de procesamiento, y que la familia
ArUco muestra ventajas de velocidad frente a otros metodos evaluados. En una
arquitectura de aterrizaje visual, donde el detector alimenta un lazo de
control con telemetria y comandos MAVLink hacia PX4, el costo computacional no es un
detalle secundario: afecta latencia, frecuencia de control y estabilidad del
comportamiento visual. La literatura de servoing visual para UAV enfatiza
precisamente la importancia de una realimentacion visual suficientemente rapida
y estable para producir acciones de control oportunas (Chuang et al., 2019;
Keipour et al., 2022).

Adicionalmente, los marcadores planos no solo sirven para detectar un centro en
la imagen; tambien pueden apoyar una estimacion geometrica de pose. Adámek et
al. (2023) senalan que los marcadores fiduciarios planos se emplean
frecuentemente para estimar la pose de una camara respecto del marcador, aunque
la incertidumbre de esa pose varia con distancia, angulo y geometria de
observacion. Esta observacion es importante porque permite justificar una
decision gradual: en la Fase 04 se usa ArUco para deteccion de ID y calculo de
error visual 2D; en fases posteriores, si se requiere, puede extenderse hacia
estimacion de pose con fundamentos geometricos. En esa linea, metodos como
EPnP e IPPE proporcionan bases conocidas para resolver la pose a partir de
correspondencias 3D-2D o de objetos planares (Collins & Bartoli, 2014; Lepetit
et al., 2009).

## Criterios de seleccion aplicados al proyecto

La decision se apoya en una matriz de criterios tecnica y metodologica:

| Criterio | Marcador HSV/color | ArUco | AprilTag / otros fiduciarios |
| --- | --- | --- | --- |
| Identidad verificable | No codifica ID | Codifica ID mediante diccionario | Codifica ID |
| Integracion con OpenCV | Alta para segmentacion HSV | Alta mediante `cv2.aruco` en OpenCV-Contrib | Variable segun libreria/bindings |
| Complejidad de dependencias | Baja | Baja-media; requiere `opencv-contrib-python` | Media; puede requerir dependencias adicionales |
| Trazabilidad experimental | Limitada al color/contorno detectado | Alta: diccionario, ID, notas de deteccion | Alta |
| Costo computacional | Bajo | Adecuado para lazo visual | Variable segun detector |
| Potencial de pose | No directo | Posible con esquinas del marcador | Posible |
| Adecuacion a Fase 04 | Util como etapa inicial | Adecuado para integracion con control | Valido, pero con mayor friccion de integracion |

Bajo estos criterios, ArUco ofrece el mejor compromiso entre robustez,
simplicidad, reproducibilidad y compatibilidad con el sistema ya implementado.
AprilTag no se descarta por inferioridad tecnica; se reconoce como una
alternativa robusta. Sin embargo, para esta tesis, cuyo alcance inmediato es
integrar percepcion, PX4/MAVLink y control visual en simulacion, ArUco presenta
menor friccion de integracion y suficiente respaldo academico.

## Validacion experimental en el proyecto

La decision bibliografica fue contrastada con una validacion piloto en AirSimNH.
Tras ajustar la textura del marcador y los parametros de deteccion, la corrida
`phase04_20260502_154838_c02260b6` obtuvo 10/10 detecciones aceptadas con
`detector_method=aruco_fiducial` y `aruco_id=23` registrado en
`detection_notes`. Todas las muestras quedaron centradas (`centered=True`) y
los comandos calculados permanecieron cercanos a cero, sin envio a PX4
(`command_sent=False`). Esta evidencia confirma que ArUco puede reemplazar al
marcador HSV/color como referencia perceptiva principal de la fase, manteniendo
la misma interfaz de control basada en `error_x_norm`, `error_y_norm`,
`confidence` y `detected`.

Esta validacion no agota la evaluacion experimental. De acuerdo con la
literatura de aterrizaje visual y servoing visual, el siguiente paso debe ser
verificar que el error visual producido por el marcador fiduciario genere
correcciones laterales coherentes y, posteriormente, que el lazo cerrado reduzca
el error durante una maniobra segura de alineamiento y descenso (Keipour et
al., 2022; Mu et al., 2023; Xin et al., 2022).

## Conclusion

La eleccion de ArUco se justifica por su equilibrio entre fundamento academico,
trazabilidad experimental, disponibilidad tecnica e integracion directa con el
pipeline existente. Frente a HSV/color, ArUco aporta identidad verificable,
menor ambiguedad y posibilidad futura de estimacion de pose. Frente a otros
fiduciarios como AprilTag, ArUco no se adopta por superioridad absoluta, sino
por adecuacion al contexto experimental: OpenCV ya forma parte del proyecto,
`cv2.aruco` permite generar y detectar marcadores sin introducir una nueva
familia de dependencias, y la literatura comparativa lo ubica como una opcion
rapida, documentada y competitiva para marcadores planos. Por ello, ArUco es
una eleccion metodologicamente defendible para la Fase 04 y una base razonable
para las fases posteriores de evaluacion del aterrizaje autonomo asistido por
vision.

## Referencias

Adámek, R., Brablc, M., Vávra, P., Dobossy, B., Formánek, M., & Radil, F.
(2023). Analytical models for pose estimate variance of planar fiducial
markers for mobile robot localisation. *Sensors, 23*(12), 5746.
https://doi.org/10.3390/s23125746

Arafat, M. Y., Alam, M. M., & Moh, S. (2023). Vision-based navigation
techniques for unmanned aerial vehicles: Review and challenges. *Drones,
7*(2), 89. https://doi.org/10.3390/drones7020089

Chuang, H.-M., He, Y.-Z., & Fujii, T. (2019). Autonomous target tracking of
UAV using high-speed visual servoing system. *Applied Sciences, 9*(21), 4552.
https://doi.org/10.3390/app9214552

Collins, T., & Bartoli, A. (2014). Infinitesimal plane-based pose estimation.
*International Journal of Computer Vision, 109*(3), 252-286.
https://doi.org/10.1007/s11263-014-0725-5

Garrido-Jurado, S., Muñoz-Salinas, R., Madrid-Cuevas, F. J., &
Marín-Jiménez, M. J. (2014). Automatic generation and detection of highly
reliable fiducial markers under occlusion. *Pattern Recognition, 47*(6),
2280-2292. https://doi.org/10.1016/j.patcog.2014.01.005

Jurado-Rodríguez, D., Muñoz-Salinas, R., Garrido-Jurado, S., &
Medina-Carnicer, R. (2023). Planar fiducial markers: A comparative study.
*Virtual Reality, 27*(3), 1733-1749.
https://doi.org/10.1007/s10055-023-00772-5

Keipour, A., Pereira, G. A. S., Bonatti, R., Garg, R., Rastogi, P., Dubey, G.,
& Scherer, S. (2022). Visual servoing approach to autonomous UAV landing on a
moving vehicle. *Sensors, 22*(17), 6549. https://doi.org/10.3390/s22176549

Lepetit, V., Moreno-Noguer, F., & Fua, P. (2009). EPnP: An accurate O(n)
solution to the PnP problem. *International Journal of Computer Vision,
81*(2), 155-166. https://doi.org/10.1007/s11263-008-0152-6

Mu, L., Li, Q., Wang, B., Zhang, Y., Feng, N., Xue, X., & Sun, W. (2023). A
vision-based autonomous landing guidance strategy for a micro-UAV by the
modified camera view. *Drones, 7*(6), 400.
https://doi.org/10.3390/drones7060400

Olson, E. (2011). AprilTag: A robust and flexible visual fiducial system. In
*Proceedings of the IEEE International Conference on Robotics and Automation*
(pp. 3400-3407). IEEE. https://doi.org/10.1109/ICRA.2011.5979561

Xin, L., Tang, Z., Gai, W., & Liu, H. (2022). Vision-based autonomous landing
for the UAV: A review. *Aerospace, 9*(11), 634.
https://doi.org/10.3390/aerospace9110634
