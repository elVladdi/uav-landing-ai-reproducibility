# Matriz de Trazabilidad con el Perfil

## Objetivos específicos

La codificación OE1-OE6 se usa para enlazar esta matriz con la trazabilidad global del repositorio.

| Código | Objetivo del perfil | Evidencia en el proyecto |
| --- | --- | --- |
| OE1 | Diseñar arquitectura funcional del agente | README, docs Fase 01, Fase 02, Fase 03 y Fase 04 |
| OE2 | Implementar percepción visual | `src/perception/`, `configs/perception_config.json`, docs Fase 03 y migración ArUco en Fase 04 |
| OE3 | Integrar agente con autopiloto y simulación | `src/control/run_mavlink_visual_servo_test.py`, `src/control/run_mavlink_direct_hover_test.py`, `src/control/px4_offboard_control.py`, scripts Fase 04 |
| OE4 | Definir protocolo reproducible | `docs/fase04_integracion_autopiloto/03_protocolo_validacion.md` y Fase 05 |
| OE5 | Evaluar error, tiempo, dinámica lateral, actividad correctiva y éxito | Campos de log Fase 04 y fase experimental T0/T1 |
| OE6 | Analizar causas de error | `05_known_issues.md`, resultados por corrida y reglas de curación de datos |

## Variables del perfil

| Variable / indicador | Implementación o preparación |
| --- | --- |
| Tasa de detección válida | `detected`, `accepted_detection`, `confidence` en CSV |
| Identidad del marcador | `detector_method=aruco_fiducial` y `aruco_id=23` en `detection_notes` |
| Latencia visual | `latency_ms` en CSV |
| Correcciones generadas | `command_forward_m_s`, `command_right_m_s`, `command_down_m_s` |
| Error final | Pendiente de fase experimental; preparar medicion final |
| Tiempo total de aterrizaje | `elapsed_seconds` y eventos land/abort |
| Dinámica lateral de aproximación | Serie temporal de error visual, desplazamiento lateral y actividad correctiva |
| Aterrizajes exitosos | `status`, evento final y criterio de zona objetivo |

## Tratamientos

| Tratamiento | Definición en perfil | Estado |
| --- | --- | --- |
| T0 | Descenso base sin corrección visual inteligente | Debe implementarse antes de experimentación |
| T1 | Aterrizaje con agente visual | Piloto validado y repetido en Fase 04; pendiente de fase experimental |

## Control metodológico

Para mantenerse alineado con el perfil:

- ejecutar la integración con autopiloto en AirSimNH, porque allí se validó el
  flujo real PX4 SITL + AirSim + MAVLink/MAVSDK;
- usar una sola plataforma señalizada estable;
- para las pruebas nuevas de agente visual, usar marcador fiduciario ArUco con
  ID fijo;
- mantener resolución de cámara constante;
- registrar versiones de simulador/autopiloto;
- no cambiar ganancias entre corridas comparables;
- usar MAVLink directo con `pymavlink` como ruta activa de setpoints para las
  corridas visuales comparables;
- ejecutar escenarios equivalentes para T0 y T1;
- conservar logs, capturas y notas de fallos por run_id.

## Estado al cierre de Fase 04

La integración agente-autopiloto queda alineada con el perfil: el agente visual
usa ArUco como referencia, calcula comandos limitados, transmite setpoints por
MAVLink directo hacia PX4, registra telemetría/comandos/detección y completa
descensos asistidos en AirSimNH. La evaluacion comparativa T0/T1 corresponde a
la fase experimental siguiente.
