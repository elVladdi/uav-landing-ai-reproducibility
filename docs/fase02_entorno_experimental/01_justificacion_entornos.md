# Justificación de Entornos: Blocks y AirSimNH

## Propósito

Este documento resume la justificación metodológica para utilizar dos entornos precompilados de AirSim durante el proyecto: **Blocks** y **AirSimNH**. La decisión busca equilibrar control experimental, reproducibilidad, complejidad visual progresiva y valor académico, manteniendo trazabilidad entre las validaciones tempranas y el entorno experimental finalmente consolidado.

## Criterio general

El proyecto requiere un entorno que permita validar un agente de visión por computador para aterrizaje autónomo sobre una plataforma señalizada. Por ello, la selección del simulador debe considerar control de variables, cámaras simuladas, registro de estados y comandos, repetibilidad de corridas, compatibilidad con control externo y complejidad visual progresiva.

AirSim es pertinente porque fue diseñado como una plataforma de simulación visual y física para vehículos autónomos, con soporte para vehículos multirrotor, sensores simulados, cámaras, API de control y comunicación con componentes externos.

## Uso de Blocks

Blocks fue considerado inicialmente como entorno controlado para validaciones tempranas. Su función metodológica fue permitir pruebas de baja complejidad visual y geométrica, útiles para depurar captura de cámara, segmentación, generación de evidencia y lógica básica de registro antes de pasar a una integración completa con autopiloto.

Ventajas:

- reduce factores externos que podrían afectar la detección visual;
- facilita la repetibilidad de las corridas;
- permite aislar fallos iniciales de percepción antes de introducir PX4;
- simplifica la depuración de cámara, segmentación y registro;
- favorece la validez interna del experimento.

En el estado actual del proyecto, Blocks no se trata como entorno principal de la evidencia final. Queda como antecedente metodológico y como entorno auxiliar de depuración.

## Uso de AirSimNH

AirSimNH quedó consolidado como entorno experimental principal desde la integración real con PX4 SITL, AirSim y MAVLink/MAVSDK. En este entorno se validó la conexión AirSimNH-PX4, la telemetría por el canal UDP 14601, las pruebas de autopiloto, la ruta MAVLink directa con `pymavlink`, el control visual con ArUco y los ensayos piloto que sustentan la transición hacia la Fase 05.

Ventajas:

- permite ejecutar el flujo real AirSimNH + PX4 SITL + agente Python;
- incorpora cámaras, telemetría y autopiloto en una arquitectura trazable;
- aporta evidencia operacional de control visual, abort seguro y descenso asistido;
- sostiene la comparación experimental T0/T1 de Fase 05 bajo una configuración ya validada.

## Estrategia experimental progresiva

La evolución metodológica del proyecto se organiza en dos momentos:

1. **Blocks**: validación controlada inicial, baja complejidad visual y mayor facilidad de depuración.
2. **AirSimNH**: entorno experimental principal consolidado para integración PX4, MAVLink/MAVSDK, percepción ArUco y control visual.

Esta estrategia permite documentar la maduración del sistema: Blocks sirvió para aislar validaciones tempranas y AirSimNH quedó como base de la evidencia final porque allí se integraron simulador, autopiloto, telemetría, percepción y control.

### Figura de soporte

![Estrategia experimental progresiva entre Blocks y AirSimNH](<Estrategia experimental progresiva-Blocks y AirSimNH.png>)

*Figura 2. Comparación metodológica entre Blocks como entorno auxiliar de validación temprana y AirSimNH como entorno experimental principal consolidado.*

**Nota de actualización metodológica:** durante el avance posterior del proyecto,
la integración experimental real con PX4 SITL, AirSim y MAVSDK quedó consolidada
en AirSimNH mediante el canal UDP 14601. Por ello, a partir de la Fase 04,
AirSimNH se adopta como entorno principal para las pruebas de autopiloto,
Offboard y control visual. Blocks se conserva como antecedente metodológico y
entorno auxiliar para depuración o validación visual controlada, sin reemplazar
la evidencia principal de integración con autopiloto.

## Relación con los tratamientos

- `T0`: descenso o aterrizaje base sin corrección visual inteligente.
- `T1`: aterrizaje autónomo asistido por agente de visión por computador.

La comparación experimental formal T0/T1 debe ejecutarse sobre la configuración consolidada en AirSimNH, porque allí se validó el flujo real con PX4 SITL y MAVLink directo. Blocks puede emplearse únicamente como apoyo diagnóstico si se requiere reproducir o depurar componentes aislados.

## Referencias base

- Dimmig et al. (2025): criterios de simuladores para robots aéreos.
- Phadke et al. (2023): selección estructurada de simulador y diseño experimental.
- Shah et al. (2017): AirSim como simulador visual y físico de alta fidelidad.
- Kedron y Frazier (2022): reproducibilidad, trazabilidad y documentación del entorno computacional.
