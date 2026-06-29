# Entregable Fase 1

## Definición del sistema, delimitación del alcance y protocolo experimental preliminar

## 1. Propósito de la fase

La Fase 1 tiene como propósito **definir con precisión el sistema a desarrollar, delimitar su alcance y dejar establecido el protocolo experimental preliminar con el que será evaluado**. Esto se alinea con el perfil del proyecto, donde la fase 1 corresponde a “Definición del sistema, delimitación del alcance y protocolo experimental”.

---

## 2. Definición del sistema

### 2.1. Definición general

El sistema propuesto es un **agente de inteligencia artificial basado en visión por computador** para el aterrizaje autónomo de un **UAV** (vehículo aéreo no tripulado, por sus siglas en inglés de *Unmanned Aerial Vehicle*) sobre una plataforma señalizada en un entorno controlado de simulación. Su función será detectar visualmente la plataforma, estimar su posición relativa respecto del dron y generar correcciones para la fase final de aproximación y descenso.

![Arquitectura funcional preliminar del agente para aterrizaje autónomo asistido por visión](<Diagrama de arquitectura por componentes V2-1.png>)

*Figura 1. Arquitectura funcional preliminar del agente para aterrizaje autónomo asistido por visión.*

### 2.2. Función principal del sistema

**Recibir la imagen de la cámara del UAV, identificar la plataforma de aterrizaje, estimar el error relativo respecto del objetivo y enviar acciones de corrección al autopiloto durante la fase final del aterrizaje.**

### 2.3. Componentes funcionales

| Componente | Función dentro del sistema | Sustento principal |
|---|---|---|
| Adquisición visual | Capturar la imagen desde la cámara del UAV | Xin et al. (2022) |
| Percepción visual | Detectar la plataforma señalizada o marcador fiduciario | Semerikov et al. (2025) |
| Estimación relativa | Calcular desplazamiento/posición relativa respecto del centro de la plataforma | Adámek et al. (2023) |
| Decisión y corrección | Traducir el error visual en acciones de ajuste | Ge et al. (2023) |
| Interfaz con autopiloto | Enviar comandos al sistema de vuelo en simulación | Jargalsaikhan et al. (2022) |

### 2.4. Vista funcional del sistema

```text
Cámara del UAV
      ↓
Detección de plataforma
      ↓
Estimación de posición relativa
      ↓
Generación de correcciones
      ↓
Envío al autopiloto
      ↓
Aproximación final y aterrizaje
```

### 2.5. Subentregable derivado: arquitectura funcional preliminar del sistema

La arquitectura funcional preliminar del sistema describe cómo se organiza el agente a nivel lógico y cómo fluye la información desde la percepción visual hasta la ejecución de la corrección de aterrizaje. Su finalidad es dejar establecido, antes de la implementación, qué módulos componen el sistema, qué función cumple cada uno y cómo se relacionan entre sí.

#### Tabla. Arquitectura funcional preliminar del sistema

| Módulo | Función principal | Entrada | Salida |
|---|---|---|---|
| Adquisición visual | Capturar la imagen desde la cámara del UAV | Escena simulada | Imagen |
| Percepción visual | Detectar la plataforma señalizada o marcador fiduciario | Imagen | Detección válida / coordenadas visuales |
| Estimación relativa | Calcular posición o error relativo respecto del centro de la plataforma | Detección visual | Error lateral, orientación o posición relativa |
| Decisión y corrección | Traducir el error visual en acciones de ajuste | Error relativo | Comandos o referencias de corrección |
| Interfaz con autopiloto | Enviar correcciones al sistema de vuelo | Comandos de corrección | Acción ejecutada por el UAV |

#### Flujo funcional preliminar

```text
Escena simulada
      ↓
Cámara del UAV
      ↓
Percepción visual
      ↓
Estimación relativa
      ↓
Decisión y corrección
      ↓
Interfaz con autopiloto
      ↓
Aproximación final y aterrizaje
```

#### Síntesis del subentregable

Este subentregable deja definida la estructura lógica mínima del sistema propuesto y establece que el agente no será tratado como un bloque monolítico, sino como una cadena funcional compuesta por percepción, estimación, decisión e integración con el control de vuelo.

---

## 3. Delimitación del alcance

### 3.1. Lo que sí incluye la investigación

| Incluye | Descripción |
|---|---|
| Detección visual de plataforma | Identificación de una plataforma señalizada en simulación |
| Estimación relativa | Cálculo del error o posición respecto del objetivo |
| Corrección de aterrizaje | Generación de acciones de ajuste en aproximación y descenso |
| Integración con autopiloto | Enlace funcional entre agente visual y control de vuelo |
| Evaluación experimental | Comparación cuantitativa entre tratamientos |

### 3.2. Lo que no incluye la investigación

| No incluye | Motivo de exclusión |
|---|---|
| Navegación autónoma global | Excede el problema específico de aterrizaje |
| Planificación completa de misión | No forma parte del alcance del prototipo |
| Evasión de obstáculos | Introduce complejidad no evaluada en esta tesis |
| Aterrizaje en superficies no señalizadas | El estudio se restringe a plataforma conocida |
| Validación en dron físico | El estudio es un piloto experimental en simulación |

### 3.3. Decisiones de delimitación

La investigación se restringe a un entorno controlado de simulación, una única plataforma señalizada y una maniobra específica de aterrizaje. Esta delimitación es coherente con el perfil y con la literatura que recomienda validar primero en simulación cuando se requiere control de variables, repetibilidad y bajo riesgo experimental.

---

## 4. Protocolo experimental preliminar

### 4.1. Tratamientos

| Tratamiento | Descripción |
|---|---|
| **T0** | Descenso automático base sin corrección visual inteligente |
| **T1** | Aterrizaje autónomo con agente de visión por computador |

### 4.2. Factores experimentales preliminares

| Factor | Descripción | Niveles preliminares |
|---|---|---|
| Altura inicial | Distancia vertical inicial respecto de la plataforma | 2 |
| Desplazamiento lateral inicial | Offset horizontal respecto del centro | 2 |
| Orientación inicial | Ángulo inicial del UAV respecto de la plataforma | 2 |

### 4.3. Escenarios preliminares

Con 3 factores y 2 niveles por factor se plantean **8 configuraciones experimentales iniciales**, con al menos **10 repeticiones por tratamiento**, según lo indicado en el perfil.

### 4.4. Variables del estudio

| Tipo de variable | Variable | Operacionalización |
|---|---|---|
| Independiente | Implementación del agente IA visual | T0 = sin agente; T1 = con agente |
| Dependiente | Desempeño del aterrizaje autónomo | Precisión, tiempo, dinámica lateral, actividad correctiva y éxito |

### 4.5. Métricas preliminares

| Dimensión | Métrica | Criterio |
|---|---|---|
| Precisión | Error de posicionamiento final | Menor es mejor |
| Eficiencia temporal | Tiempo total de aterrizaje | Menor es mejor |
| Estabilidad | Desviación lateral durante el descenso | Menor es mejor |
| Éxito | Porcentaje de aterrizajes exitosos | Mayor es mejor |

### 4.6. Condiciones de control

| Condición de control | Estado |
|---|---|
| Modelo de dron | Constante |
| Tamaño y diseño del marcador | Constante |
| Dimensiones de la plataforma | Constante |
| Resolución de cámara | Constante |
| Versión del simulador | Constante |
| Versión del autopiloto | Constante |
| Tiempo máximo por corrida | Constante |
| Criterio de éxito | Constante |

### 4.7. Registro mínimo por corrida

| Campo | Descripción |
|---|---|
| ID de corrida | Identificador único |
| Tratamiento | T0 o T1 |
| Escenario | Combinación de factores iniciales |
| Parámetros iniciales | Altura, desplazamiento, orientación |
| Resultados | Métricas de desempeño |
| Observaciones | Fallos, abortos, incidencias |

### 4.8. Subentregable derivado: definición inicial de T0 y T1

La definición inicial de tratamientos tiene por finalidad precisar desde la Fase 1 cuál será el sistema de referencia y cuál será el sistema experimental, de modo que la comparación posterior no quede ambigua.

#### Tabla. Definición inicial de tratamientos

| Tratamiento | Denominación | Descripción operativa | Rol en el estudio |
|---|---|---|---|
| T0 | Esquema base | Descenso automático sin corrección visual inteligente sobre la plataforma | Referencia de comparación |
| T1 | Sistema propuesto | Aterrizaje autónomo asistido por agente de visión por computador, con detección de plataforma, estimación relativa y correcciones durante la fase final | Tratamiento experimental |

#### Diferencia funcional preliminar entre T0 y T1

| Elemento | T0 | T1 |
|---|---|---|
| Uso de percepción visual | No | Sí |
| Estimación relativa respecto de la plataforma | No | Sí |
| Corrección basada en información visual | No | Sí |
| Integración con lógica inteligente de aterrizaje | No | Sí |
| Función en el análisis | Línea base | Sistema evaluado |

#### Criterio metodológico

La diferencia entre T0 y T1 deberá mantenerse restringida al efecto del agente visual, mientras las demás condiciones experimentales permanezcan constantes. Así, cualquier cambio observado en precisión, tiempo, dinámica lateral, actividad correctiva o tasa de éxito podrá interpretarse de forma más válida como efecto del tratamiento y no como consecuencia de variaciones externas del entorno o de la configuración experimental.

#### Síntesis del subentregable

Este subentregable deja fijado, desde la etapa de definición, que el estudio no evaluará el sistema de forma aislada, sino mediante comparación entre una línea base y un sistema con agente inteligente, lo que da coherencia al protocolo experimental posterior.

---

### 4.9. Trazabilidad inicial con objetivos específicos del perfil

La Fase 1 establece los elementos de diseño que serán desarrollados y verificados en las fases posteriores. La siguiente tabla relaciona cada subentregable con los objetivos específicos del perfil, usando la codificación OE1-OE6 empleada en la matriz de trazabilidad del proyecto.

| Elemento de Fase 1 | Objetivo específico relacionado | Justificación de trazabilidad |
|---|---|---|
| Arquitectura funcional preliminar | OE1 | Define los módulos del agente, sus entradas, salidas y relación con el autopiloto. |
| Delimitación del alcance | OE1/OE4 | Acota el sistema a simulación controlada y prepara un protocolo reproducible. |
| Definición T0/T1 | OE4/OE5 | Establece la comparación entre línea base y sistema asistido para la evaluación posterior. |
| Métricas preliminares | OE5 | Anticipa precisión, tiempo, dinámica lateral, actividad correctiva y éxito como dimensiones de desempeño. |
| Registro mínimo por corrida | OE4/OE6 | Fija los campos necesarios para reproducibilidad, auditoría y análisis de causas de error. |

## 5. Síntesis del entregable

La Fase 1 deja establecido que el estudio desarrollará un sistema de aterrizaje autónomo asistido por visión por computador, restringido a entorno controlado de simulación, con comparación entre un tratamiento base y un tratamiento con agente inteligente. También fija preliminarmente los factores, variables, métricas y condiciones de control que guiarán la experimentación posterior.

---

## Referencias

Adámek, R., Brablc, M., Vávra, P., Dobossy, B., Formánek, M., & Radil, F. (2023). Analytical models for pose estimate variance of planar fiducial markers for mobile robot localisation. *Sensors, 23*(12), 5746. https://doi.org/10.3390/s23125746

Ge, Z., Jiang, J., Pugh, E., Marshall, B., Yan, Y., & Sun, L. (2023). Vision-based UAV landing with guaranteed reliability in adverse environment. *Electronics, 12*(4), 967. https://doi.org/10.3390/electronics12040967

Jargalsaikhan, T., Lee, K., Jun, Y.-K., & Lee, S. (2022). Architectural process for flight control software of unmanned aerial vehicle with module-level portability. *Aerospace, 9*(2), 62. https://doi.org/10.3390/aerospace9020062

Phadke, A., Medrano, F. A., Sekharan, C. N., & Chu, T. (2023). Designing UAV swarm experiments: A simulator selection and experiment design process. *Sensors, 23*(17), 7359. https://doi.org/10.3390/s23177359

Semerikov, S. O., Nechypurenko, P. P., Vakaliuk, T. A., Mintii, I. S., & Kolhatin, A. O. (2025). Vision-based autonomous UAV landing: A comprehensive review of technologies, techniques, and applications. *Journal of Intelligent & Robotic Systems, 111*, Article 115. https://doi.org/10.1007/s10846-025-02314-4

Shah, S., Dey, D., Lovett, C., & Kapoor, A. (2017). AirSim: High-fidelity visual and physical simulation for autonomous vehicles. *arXiv*. https://doi.org/10.48550/arXiv.1705.05065

Xin, L., Tang, Z., Gai, W., & Liu, H. (2022). Vision-based autonomous landing for the UAV: A review. *Aerospace, 9*(11), 634. https://doi.org/10.3390/aerospace9110634
