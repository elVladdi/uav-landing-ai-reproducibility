# Justificación metodológica de las fases del proyecto

## Propósito del documento

Este documento justifica la organización metodológica del proyecto **UAV Landing AI** en fases progresivas. La finalidad es explicar por qué el desarrollo no se ejecuta directamente como una comparación experimental final, sino como una secuencia incremental de definición, configuración, percepción, integración y evaluación. Esta organización busca fortalecer la validez interna del experimento, la seguridad operativa, la trazabilidad de decisiones técnicas y la reproducibilidad de los resultados.

El proyecto se orienta al desarrollo y evaluación de un agente visual para el aterrizaje autónomo de un vehículo aéreo no tripulado (UAV) sobre una plataforma señalizada en un entorno controlado de simulación. La estrategia metodológica adoptada responde a la naturaleza integrada del sistema: el aterrizaje asistido por visión requiere coordinar simulación, percepción visual, autopiloto, comandos de control, registro de datos, curación de corridas y análisis cuantitativo.

## Fundamento general de la organización por fases

La literatura sobre aterrizaje autónomo de UAV muestra que la fase final de aproximación y aterrizaje exige precisión espacial, estabilidad y capacidad de corrección ante incertidumbre perceptual o degradación de posicionamiento global. Las revisiones sobre navegación visual para UAV destacan que la visión por computador puede complementar o sustituir fuentes globales de posicionamiento cuando se requiere estimar la relación espacial entre el vehículo y una zona o plataforma de aterrizaje (Arafat et al., 2023; Semerikov et al., 2025; Xin et al., 2022). En consecuencia, el problema no puede reducirse a detectar un objeto en una imagen; debe evaluarse si la información visual se transforma en acciones de control que mejoran el aterrizaje.

La organización por fases permite reducir gradualmente la incertidumbre experimental. Primero, se define el sistema y sus variables; luego, se valida el entorno de simulación; posteriormente, se verifica la percepción visual; después, se integra la percepción con el autopiloto; a continuación, se ejecuta la comparación formal entre un tratamiento base y un tratamiento asistido por visión; finalmente, se analizan los resultados, se contrastan las hipótesis y se delimitan las conclusiones. Esta secuencia es coherente con investigaciones que separan percepción, decisión y control en arquitecturas de UAV con autopiloto y computadora externa o agente de alto nivel (Aliane, 2024; Boiteau et al., 2024; Sandino et al., 2020).

Además, el uso de simulación controlada es metodológicamente pertinente para ensayos con UAV porque permite repetir escenarios, reducir riesgos y documentar condiciones experimentales. AirSim ofrece un entorno visual y físico con sensores simulados e interfaces de control, mientras que PX4 SITL y MAVLink/MAVSDK permiten aproximar una arquitectura de autopiloto real en condiciones reproducibles (Aliane, 2024; Shah et al., 2017). La literatura sobre simulación y reproducibilidad en robótica aérea también enfatiza la necesidad de conservar configuraciones, parámetros, código, datos y evidencias para permitir comparación y replicación de resultados (Dimmig et al., 2025; Kedron & Frazier, 2022; Phadke et al., 2023).

![Secuencia metodológica incremental del proyecto UAV Landing AI](assets/figures/secuencia_metodologica_fases.png)

*Figura 1. Secuencia metodológica incremental del proyecto, desde la definición del sistema hasta la comparación experimental T0/T1.*

## Justificación de la Fase 01: Definición del sistema y delimitación del alcance

La Fase 01 cumple una función de delimitación conceptual y experimental. Antes de construir o ejecutar un sistema autónomo, es necesario especificar qué sistema se desarrollará, qué componentes lo integran, qué queda dentro y fuera del alcance, cuáles serán los tratamientos comparados y qué métricas permitirán evaluar desempeño.

Esta fase es necesaria porque el concepto de “agente de inteligencia artificial” puede ser ambiguo si no se define operacionalmente. En el contexto del proyecto, el agente se entiende como un sistema modular que percibe información visual, estima un error relativo, decide correcciones y registra evidencias para evaluación. Esta definición es coherente con arquitecturas de UAV donde la percepción y la decisión de alto nivel se separan del control de bajo nivel ejecutado por el autopiloto (Boiteau et al., 2024; Sandino et al., 2020).

La Fase 01 también permite establecer la comparación experimental entre `T0` y `T1`. `T0` representa el tratamiento base sin corrección visual inteligente, mientras que `T1` representa el aterrizaje asistido por el agente visual. Esta distinción es central porque la pregunta de investigación no se limita a demostrar que el sistema puede detectar una plataforma, sino a determinar si el uso de visión mejora el desempeño del aterrizaje respecto a una condición base.

## Justificación de la Fase 02: Configuración y validación del entorno experimental

La Fase 02 se justifica por la necesidad de contar con un entorno experimental estable, controlado y reproducible. En sistemas UAV, las pruebas físicas directas pueden introducir riesgos operativos, costos y variabilidad difícil de controlar. Por ello, la simulación permite ejecutar validaciones progresivas antes de pasar a escenarios más exigentes o reales. AirSim se ha utilizado como simulador visual y físico para investigación en autonomía robótica, con sensores simulados y soporte para integración con controladores externos (Shah et al., 2017). Asimismo, PX4 SITL y MAVLink/MAVSDK son herramientas utilizadas para investigación, educación y validación de autopilotos UAV (Aliane, 2024).

La Fase 02 no solo instala herramientas; establece la base metodológica de la reproducibilidad. Validar AirSimNH, PX4 SITL, cámara simulada, conexión Python/MAVSDK, canal MAVLink y logging permite asegurar que las fases posteriores no dependan de configuraciones implícitas o no trazables. Esta decisión se alinea con recomendaciones sobre reproducibilidad computacional, donde se enfatiza la necesidad de documentar código, datos, configuración, parámetros y procedencia de resultados (Kedron & Frazier, 2022).

En el proyecto, Blocks se conserva como antecedente metodológico y entorno auxiliar de baja complejidad visual, mientras que AirSimNH se consolida como entorno experimental principal para las fases de integración y comparación formal. Esta transición responde a la necesidad de que la evidencia final provenga de un entorno compatible con PX4 SITL, MAVLink/MAVSDK, cámara simulada y ejecución de corridas trazables.

## Justificación de la Fase 03: Validación de la percepción visual

La Fase 03 valida el módulo de percepción antes de conectarlo al control de vuelo. Esta separación es metodológicamente necesaria porque una falla perceptual puede generar errores de control, pérdida de marcador, abortos o resultados no atribuibles al tratamiento experimental. La literatura sobre aterrizaje visual señala que la detección de plataformas, marcadores o zonas de aterrizaje es una etapa crítica para estimar la relación entre el UAV y el objetivo (Arafat et al., 2023; Xin et al., 2022).

En esta fase, la detección inicial basada en HSV/color permite comprobar captura de cámara, segmentación, estimación de centroide, cálculo de error visual y generación de evidencia anotada. Esta aproximación es válida como etapa inicial en condiciones controladas, porque permite verificar el flujo de percepción sin introducir todavía el riesgo de comandos activos al autopiloto.

Sin embargo, para el cierre del lazo de control y la experimentación formal, el proyecto adopta ArUco como marcador fiduciario. Esta decisión está sustentada en la literatura sobre marcadores planares, que destaca la utilidad de ArUco y AprilTag para identificación visual, trazabilidad y estimación relativa en aplicaciones robóticas (Garrido-Jurado et al., 2014; Jurado-Rodríguez et al., 2023). Además, trabajos de aterrizaje UAV con plataformas señalizadas han empleado marcadores ArUco para reconocimiento de plataforma y apoyo al control de aterrizaje (Liu et al., 2019).

## Justificación de la Fase 04: Integración con autopiloto y cierre percepción-control

La Fase 04 se justifica porque la detección visual por sí sola no demuestra mejora en el aterrizaje. La mejora depende de cerrar el lazo entre percepción y control: el error visual debe transformarse en comandos o referencias que modifiquen el comportamiento del UAV. La literatura sobre servoing visual muestra que el error en el plano de imagen puede utilizarse como señal de control para reducir la diferencia entre la posición observada del objetivo y una referencia deseada (Bin, 2020; Keipour et al., 2022). Otros trabajos integran marcadores, sensores y control visual para aterrizaje autónomo sobre plataformas o vehículos (Delbene et al., 2022; Liu et al., 2019).

En esta fase se valida progresivamente la integración con PX4: telemetría, comandos seguros, diagnóstico Offboard, cálculo de comandos en `dry-run`, detección ArUco, corrección lateral activa, abort seguro y descenso asistido. Esta progresión es necesaria para reducir riesgos antes de la comparación formal. Un sistema de aterrizaje autónomo no debe enviar comandos de descenso o corrección lateral sin haber validado previamente signos, límites de velocidad, recuperación de modo, detección confiable y condiciones de aborto.

La decisión de utilizar MAVLink directo con `pymavlink` como ruta activa de control se justifica por la necesidad de enviar setpoints visuales trazables y efectivos al autopiloto. La literatura sobre arquitecturas UAV respalda la separación entre el agente externo y el autopiloto, así como el uso de MAVLink, PX4, MAVSDK, ROS/MAVROS o interfaces similares para integrar percepción y control (Aliane, 2024; Bautista et al., 2023; Boiteau et al., 2024).

## Justificación de la Fase 05: Experimentación formal T0/T1

La Fase 05 constituye la etapa de evaluación experimental. Su propósito es comparar cuantitativamente el tratamiento base `T0` con el tratamiento visual `T1` bajo escenarios controlados y repetibles. Esta fase responde directamente a la pregunta de investigación: determinar si el agente visual mejora el desempeño del aterrizaje autónomo frente a una condición base sin corrección visual inteligente.

La literatura sobre evaluación de desempeño UAV recomienda utilizar métricas de precisión, trayectoria, tiempo, éxito y variables operacionales para medir diferencias de forma objetiva (Boshoff et al., 2025). En aterrizaje visual, también son relevantes el error final, la dispersión, la actividad correctiva, la tasa de detección, la pérdida de objetivo y la confiabilidad de la aproximación (Ge et al., 2023; Llerena Caña et al., 2022). En consecuencia, la Fase 05 no solo ejecuta corridas: define escenarios, tratamientos, repeticiones, reglas de inclusión/exclusión, curación de datos y análisis pareado.

La comparación `T0/T1` permite aislar el efecto del agente visual. `T0` representa una condición base de descenso sin corrección lateral inteligente; `T1` incorpora percepción ArUco y control visual mediante MAVLink directo. Al mantener escenarios equivalentes, tratamiento pareado y métricas comunes, el análisis puede estimar si la incorporación de visión reduce el error final, modifica el tiempo de aterrizaje, modifica la dinámica lateral de aproximación y afecta la tasa de éxito.

## Justificación de la Fase 06: Análisis de resultados y cierre interpretativo

La Fase 06 constituye el cierre analítico del proyecto. Su función no es modificar el experimento ni añadir nuevas corridas, sino transformar el dataset aceptado de Fase 05 en evidencia cuantitativa, interpretación académica y conclusiones trazables. Esta separación es metodológicamente importante porque evita confundir la etapa de generación de datos con la etapa de análisis de resultados.

En esta fase se audita la consistencia del dataset, se calculan estadísticas descriptivas, se contrastan hipótesis, se estiman tamaños de efecto, se examinan diferencias por escenario y se analizan incidencias o fuentes de error. La literatura sobre evaluación de desempeño UAV respalda el uso de métricas objetivas para valorar precisión, tiempo, trayectoria, dinámica de corrección y éxito (Boshoff et al., 2025), mientras que la literatura sobre reproducibilidad enfatiza la necesidad de conservar scripts, resúmenes curados y criterios de análisis que permitan auditar los resultados (Kedron & Frazier, 2022; Phadke et al., 2023).

La Fase 06 también cumple una función interpretativa. Los resultados muestran que el tratamiento visual `T1` reduce de forma marcada el error final de aterrizaje, incrementa el tiempo de descenso y modifica significativamente la dinámica lateral mediante mayor actividad correctiva. Esta lectura evita una conclusión simplificada del tipo "el agente visual mejora todo"; en cambio, permite formular una conclusión técnicamente más sólida: el agente mejora la precisión final en simulación controlada, a cambio de una estrategia más lenta y más activa durante la aproximación.

## Matriz de justificación metodológica por fase

| Fase | Rol metodológico | Riesgo que controla | Evidencia generada | Soporte académico principal |
|---|---|---|---|---|
| Fase 01 - Definición del sistema | Delimita sistema, alcance, tratamientos, variables y métricas. | Ambigüedad conceptual, objetivos no operacionales o comparación experimental indefinida. | Arquitectura funcional, definición `T0/T1`, métricas preliminares y registro mínimo por corrida. | Arafat et al. (2023); Boiteau et al. (2024); Sandino et al. (2020). |
| Fase 02 - Entorno experimental | Configura y valida simulador, autopiloto, conexión y logging. | Falta de reproducibilidad, configuración no trazable o entorno inestable. | Validación AirSimNH/PX4, cámara, conexión, logs y configuración final. | Aliane (2024); Shah et al. (2017); Kedron & Frazier (2022); Phadke et al. (2023). |
| Fase 03 - Percepción visual | Valida captura, detección, centroide, error visual y evidencia anotada. | Fallas perceptuales antes de activar control de vuelo. | Imágenes crudas/anotadas, resultados de detección, error visual y transición HSV→ArUco. | Garrido-Jurado et al. (2014); Jurado-Rodríguez et al. (2023); Liu et al. (2019). |
| Fase 04 - Integración con autopiloto | Cierra el lazo percepción-control con validaciones seguras. | Comandos incorrectos, signos invertidos, pérdida de marcador o control inseguro. | Dry-run, corrección lateral, abort seguro, descenso asistido y ruta MAVLink validada. | Keipour et al. (2022); Delbene et al. (2022); Aliane (2024); Bautista et al. (2023). |
| Fase 05 - Experimentación T0/T1 | Ejecuta comparación formal con escenarios, repeticiones y métricas. | Conclusiones sin evidencia cuantitativa o datos no curados. | Corridas formales, resumen curado, diferencias pareadas, reporte y análisis estadístico. | Boshoff et al. (2025); Ge et al. (2023); Llerena Caña et al. (2022). |
| Fase 06 - Análisis de resultados | Audita el dataset, contrasta hipótesis e interpreta los resultados. | Interpretaciones no trazables, lectura parcial de métricas o conclusiones sin delimitación metodológica. | Estadística descriptiva, pruebas pareadas, tamaños de efecto, análisis por escenario, incidencias, discusión, limitaciones y conclusiones. | Boshoff et al. (2025); Kedron & Frazier (2022); Phadke et al. (2023). |

## Relación con la validez y reproducibilidad

La secuencia metodológica fortalece la validez interna porque evita atribuir el resultado final a componentes no verificados. Si el sistema fallara en la Fase 05 sin haber validado percepción, entorno y control, no sería posible determinar si el problema se debe al detector, al autopiloto, a la configuración del simulador, al canal de comunicación o al diseño experimental. Si los resultados de Fase 05 se interpretaran sin una Fase 06 explícita, tampoco sería posible distinguir entre mejora de precisión, incremento de tiempo, dinámica lateral, éxito operativo y fuentes de error. Por ello, cada fase produce una evidencia parcial que habilita la siguiente.

También fortalece la reproducibilidad. El proyecto conserva documentación de configuración, comandos, rutas, criterios de aceptación, evidencias visuales, logs, resúmenes curados, scripts de análisis y reportes formales. Esto permite que otro investigador pueda revisar el flujo completo desde la definición del sistema hasta el análisis de resultados. En esta lógica, los logs crudos pueden permanecer fuera del repositorio si son pesados, pero los resúmenes curados, reglas de curación, scripts y reportes formales deben permanecer versionados para permitir auditoría académica.

## Limitaciones de la justificación

Esta versión se redacta a partir de la documentación del repositorio y de las referencias ya registradas en el estado del arte. Para una versión final de tesis, se recomienda contrastar cada afirmación con los PDF originales de las referencias principales, especialmente cuando se usen citas específicas para sustentar decisiones metodológicas. No obstante, la bibliografía actualmente disponible en el proyecto es suficiente para justificar la estructura general de fases, porque cubre visión para aterrizaje UAV, marcadores fiduciarios, servoing visual, integración con autopiloto, simulación, reproducibilidad, métricas de desempeño y análisis de resultados.

## Referencias

Arafat, M. Y., Alam, M. M., & Moh, S. (2023). Vision-Based Navigation Techniques for Unmanned Aerial Vehicles: Review and Challenges. *Drones, 7*(2), 89. https://doi.org/10.3390/drones7020089

Aliane, N. (2024). A Survey of Open-Source UAV Autopilots. *Electronics, 13*(23), 4785. https://doi.org/10.3390/electronics13234785

Bautista, N., Gutierrez, H., Inness, J., & Rakoczy, J. (2023). Precision landing of a quadcopter drone by smartphone video guidance sensor in a GPS-denied environment. *Sensors, 23*(4), 1934. https://doi.org/10.3390/s23041934

Bin, E. (2020). *MPC-based Visual Servo Control for UAVs* (Master’s thesis, KTH Royal Institute of Technology). KTH DiVA.

Boiteau, S., Vanegas, F., & Gonzalez, F. (2024). Framework for Autonomous UAV Navigation and Target Detection in Global-Navigation-Satellite-System-Denied and Visually Degraded Environments. *Remote Sensing, 16*(3), 471. https://doi.org/10.3390/rs16030471

Boshoff, M., Barros, G., & Kuhlenkötter, B. (2025). Performance measurement of unmanned aerial vehicles to suit industrial applications. *Production Engineering, 19*, 429–453. https://doi.org/10.1007/s11740-024-01313-y

Delbene, A., Baglietto, M., & Simetti, E. (2022). Visual Servoed Autonomous Landing of an UAV on a Catamaran in a Marine Environment. *Sensors, 22*(9), 3544. https://doi.org/10.3390/s22093544

Dimmig, C. A., Silano, G., McGuire, K., Gabellieri, C., Hönig, W., Moore, J. L., & Kobilarov, M. (2025). Survey of simulators for aerial robots: An overview and in-depth systematic comparisons. *IEEE Robotics & Automation Magazine, 32*(2), 153–166. https://doi.org/10.1109/MRA.2024.3433171

Garrido-Jurado, S., Muñoz-Salinas, R., Madrid-Cuevas, F. J., & Marín-Jiménez, M. J. (2014). Automatic generation and detection of highly reliable fiducial markers under occlusion. *Pattern Recognition, 47*(6), 2280–2292. https://doi.org/10.1016/j.patcog.2014.01.005

Ge, Z., Jiang, J., Pugh, E., Marshall, B., Yan, Y., & Sun, L. (2023). Vision-Based UAV Landing with Guaranteed Reliability in Adverse Environment. *Electronics, 12*(4), 967. https://doi.org/10.3390/electronics12040967

Jurado-Rodríguez, D., Muñoz-Salinas, R., Garrido-Jurado, S., & Medina-Carnicer, R. (2023). Planar fiducial markers: A comparative study. *Virtual Reality, 27*(3), 1733–1749. https://doi.org/10.1007/s10055-023-00772-5

Kedron, P., & Frazier, A. E. (2022). Reproducibility and replicability: Opportunities and challenges for geospatial research. *International Journal of Geographical Information Science, 36*(3), 427–437. https://doi.org/10.1080/13658816.2022.2027934

Keipour, A., Pereira, G. A. S., & Scherer, S. (2022). A Visual Servoing Approach for Autonomous UAV Landing on a Moving Vehicle. *Autonomous Robots, 46*, 409–429.

Liu, C., Chen, W., Liu, J., & Wu, H. (2019). A Vision-Based Autonomous Landing System for a Low-Cost Quadrotor Using a Monocular Camera and Fiducial Markers. *Sensors, 19*(20), 4388. https://doi.org/10.3390/s19204388

Llerena Caña, V., et al. (2022). Reducción de error en sistemas de aterrizaje multirrotor basados en visión. [Referencia registrada en el estado del arte del proyecto].

Phadke, A., Medrano, F. A., Kim, H., & Choi, J. (2023). Selection of Simulation Platforms for UAVs Based on Experimental Design. *Drones, 7*(5), 332. https://doi.org/10.3390/drones7050332

Sandino, J., Vanegas, F., Maire, F., Caccetta, P., Sanderson, C., & Gonzalez, F. (2020). UAV Framework for Autonomous Onboard Navigation and People/Object Detection in Cluttered Indoor Environments. *Remote Sensing, 12*(20), 3386. https://doi.org/10.3390/rs12203386

Semerikov, S., et al. (2025). [Referencia registrada en el estado del arte del proyecto sobre aterrizaje autónomo y visión].

Shah, S., Dey, D., Lovett, C., & Kapoor, A. (2017). AirSim: High-Fidelity Visual and Physical Simulation for Autonomous Vehicles. *Field and Service Robotics*. https://doi.org/10.1007/978-3-319-67361-5_40

Xin, B., et al. (2022). [Referencia registrada en el estado del arte del proyecto sobre aterrizaje autónomo de UAV basado en visión].
