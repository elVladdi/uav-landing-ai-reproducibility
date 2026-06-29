# Trazabilidad Global de Fases y Objetivos

## Objetivo del documento

Este documento consolida la relación entre fases, entregables, objetivos específicos del perfil y evidencias del repositorio. Usa la codificación OE1-OE6 documentada en `docs/fase04_integracion_autopiloto/08_matriz_trazabilidad_perfil.md` y la actualiza con el cierre analítico de Fase 06.

## Objetivos específicos del perfil

| Código | Objetivo específico |
| --- | --- |
| OE1 | Diseñar arquitectura funcional del agente. |
| OE2 | Implementar percepción visual. |
| OE3 | Integrar agente con autopiloto y simulación. |
| OE4 | Definir protocolo reproducible. |
| OE5 | Evaluar error, tiempo, dinámica lateral, actividad correctiva y éxito. |
| OE6 | Analizar causas de error. |

## Matriz global de trazabilidad

| Fase | Entregable/documento principal | Objetivo específico relacionado | Evidencia en repositorio | Estado |
| --- | --- | --- | --- | --- |
| Fase 01 | `docs/fase01_definicion_del_sistema_delimitacion_del_alcance/entregable_fase1_consolidado.md` | OE1, OE4, OE5, OE6 | Arquitectura funcional preliminar, delimitación del alcance, definición `T0/T1`, métricas preliminares y registro mínimo por corrida. | Cerrada como definición metodológica inicial. |
| Fase 02 | `docs/fase02_entorno_experimental/05_environment_validation.md` y `docs/fase02_entorno_experimental/09_manual_arranque_entorno_simulado.md` | OE3, OE4 | AirSimNH, PX4 SITL, Windows + Ubuntu/WSL2, Python 3.10, `bottom_center`, `Drone1`, UDP 14601 y conexión Python/MAVSDK. | Cerrada como entorno experimental base; AirSimNH queda como entorno principal actual. |
| Fase 03 | `docs/fase03_percepcion_visual/04_resultados_validacion.md` | OE2, OE4 | Validaciones HSV/color en Blocks y AirSimNH, imágenes anotadas, CSV/JSON, repetibilidad de seis corridas positivas en AirSimNH. | Cerrada como validación perceptiva inicial; ArUco se adopta para control desde Fase 04. |
| Fase 04 | `docs/fase04_integracion_autopiloto/04_resultados_validacion.md` y `docs/fase04_integracion_autopiloto/08_matriz_trazabilidad_perfil.md` | OE2, OE3, OE4, OE5, OE6 | Telemetría PX4, takeoff/land, MAVLink directo Offboard, hover, dry-run ArUco, signo lateral, corrección lateral activa, abort seguro y descenso asistido. | Cerrada técnicamente con tres corridas positivas comparables de descenso asistido. |
| Fase 05 | `docs/fase05_experimentacion_t0_t1/02_diseno_experimental_t0_t1.md` y `docs/fase05_experimentacion_t0_t1/13_avance_ejecucion_formal.md` | OE4, OE5, OE6 | Protocolo `T0/T1`, configuración congelada, diccionario de datos, reglas de curación, plan de análisis, tablas finales y cierre de corridas formales. | Cerrada formalmente; `S01`-`S08` completos con `T0 10/10`, `T1 10/10`, `160/160` corridas aceptadas y `80` pares completos. |
| Fase 06 | `docs/fase06_analisis_resultados/09_conclusiones_fase06.md` y `docs/fase06_analisis_resultados/10_ayuda_memoria_fase06.md` | OE4, OE5, OE6 | Auditoría del dataset, estadística descriptiva, pruebas de hipótesis, tamaños de efecto, análisis por escenario, análisis de incidencias, discusión, limitaciones y conclusiones. | Cerrada analíticamente; evidencia final lista para tesis, artículo o informe académico. |

## Relación metodológica entre fases

Fase 01 define el sistema, el alcance, los tratamientos y las métricas. Fase 02 consolida AirSimNH con PX4 SITL y MAVLink/MAVSDK como entorno experimental principal. Fase 03 valida el pipeline de percepción visual con HSV/color y deja evidencia reproducible. Fase 04 migra la referencia perceptiva a ArUco para cerrar el lazo con MAVLink directo, validar control lateral, abort seguro y descenso asistido.

Fase 05 toma esa configuración congelada para comparar `T0` y `T1` sin alterar los supuestos técnicos ya validados. Fase 06 toma el dataset aceptado de Fase 05 y lo convierte en evidencia analítica: audita consistencia, resume métricas, contrasta hipótesis, interpreta diferencias por escenario, identifica fuentes de error y delimita el alcance de las conclusiones.

## Lectura sintética de la trazabilidad

- OE1 queda principalmente cubierto por Fase 01.
- OE2 queda cubierto por Fase 03 y reforzado en Fase 04.
- OE3 queda cubierto por Fase 02 y Fase 04.
- OE4 atraviesa Fase 01 a Fase 06 porque exige protocolo, configuración, curación, scripts y evidencia reproducible.
- OE5 se materializa experimentalmente en Fase 05 y se evalúa estadísticamente en Fase 06.
- OE6 se aborda mediante el análisis de incidencias, fuentes de error, limitaciones y discusión de Fase 06.

Con esta estructura, la cadena metodológica queda completa: definición del sistema, preparación del entorno, validación perceptiva, integración con autopiloto, ejecución experimental y análisis final de resultados.
