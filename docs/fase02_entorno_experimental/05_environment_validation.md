# Validación del Entorno Experimental

## Propósito

Este documento resume las pruebas de validación funcional del entorno experimental de Fase 02. Su objetivo es comprobar que los componentes mínimos funcionan antes de avanzar hacia la implementación del módulo de percepción visual.

## Configuración final consolidada

La configuración congelada al cierre de Fase 02 queda definida como base metodológica para Fase 03, Fase 04 y la experimentación T0/T1 de Fase 05. Blocks se conserva como entorno auxiliar de depuración, mientras que AirSimNH queda como entorno experimental principal por ser el escenario donde se consolidó la integración real con PX4 SITL y MAVLink/MAVSDK.

| Elemento | Configuración consolidada | Rol metodológico |
| --- | --- | --- |
| Simulador | AirSimNH | Entorno experimental principal actual |
| Autopiloto | PX4 SITL | Control de vuelo y modos PX4 en simulación |
| Sistema operativo | Windows + Ubuntu/WSL2 | AirSimNH en Windows y PX4 SITL en WSL2 |
| Python | 3.10 | Compatibilidad con AirSim y entorno `.venv` |
| Cámara | `bottom_center` | Captura inferior para percepción visual |
| Canal MAVLink | UDP 14601 | Canal dedicado para cliente Python/MAVSDK |
| Vehículo | `Drone1` | UAV simulado usado por AirSim |
| Ruta de control activa | MAVLink directo / `pymavlink` | Setpoints visuales activos validados desde Fase 04 |
| Ruta auxiliar | MAVSDK | Diagnóstico, telemetría y acciones de alto nivel |
| Entorno auxiliar | Blocks | Depuración o validaciones tempranas, no evidencia final principal |

## Evidencia operativa validada

| Código | Prueba | Estado actual | Evidencia esperada |
| --- | --- | --- | --- |
| V01 | Ejecución del simulador | Validado con AirSimNH | Captura del entorno AirSim |
| V02 | Carga del UAV | Validado con AirSimNH | Captura o log de conexión |
| V03 | Lectura de cámara | Validado | Imagen en `data/raw/` |
| V04 | Lectura de estado | Validado | CSV en `data/logs/` |
| V05 | Comunicación con autopiloto PX4 | Validado con PX4 SITL + AirSimNH + MAVSDK | Salida de `check_px4_connection.ps1` |
| V06 | Comando básico | Validado con AirSim SimpleFlight | Registro o salida de `command_test.py` |
| V07 | Registro de corrida | Validado de forma inicial | CSV con `run_id` |
| V08 | Repetibilidad básica | Validado de forma inicial | Tres logs comparables |

## Manual operativo de validación

Los siguientes comandos se conservan como manual de arranque y verificación mínima. La secuencia completa de AirSimNH, PX4 SITL y canal MAVLink dedicado se documenta en `09_manual_arranque_entorno_simulado.md`.

### Conexión con AirSim

```powershell
python src\connection\airsim_client.py
```

Criterio de aceptación: AirSim responde a `confirmConnection`, el vehículo `Drone1` existe y se obtiene estado inicial del multirrotor.

### Comando básico de vuelo

```powershell
python src\control\command_test.py
```

Criterio de aceptación: habilita control por API, arma el UAV, despega, asciende a altura configurada, mantiene vuelo, aterriza, desarma y libera control API.

### Captura de cámara

```powershell
python src\perception\camera_test.py
```

Criterio de aceptación: recibe una imagen válida desde `bottom_center`, guarda archivo `.png` en `data/raw/` y reporta resolución.

Evidencia actual:

```text
data/raw/capture_bottom_center_20260426_185846.png
data/raw/capture_bottom_center_20260427_202447.png
data/raw/capture_bottom_center_20260427_204552.png
```

### Registro de estado

```powershell
python src\logging\run_logger.py
```

Criterio de aceptacion: genera `run_id`, registra timestamp, posicion, orientacion y velocidad, y guarda CSV en `data/logs/`.

Evidencia actual:

```text
data/logs/phase02_20260426_190010_2a17c083_state_log.csv
data/logs/phase02_20260427_202456_2e06f11f_state_log.csv
data/logs/phase02_20260427_204559_74c74615_state_log.csv
```

### Conexión PX4

```powershell
.\scripts\check_px4_connection.ps1
```

Criterio de aceptación: MAVSDK detecta PX4, imprime health, estado de armado y posición/velocidad NED.

Estado:

```text
Validado. AirSimNH se conecta a PX4 SITL por TCP 4560 y el cliente Python/MAVSDK se conecta por un canal MAVLink dedicado en UDP 14601.
```

Salida esperada confirmada:

```text
Conexión correcta con PX4
Health: global_position_ok=True, home_position_ok=True, local_position_ok=True
Armed: False
NED: north=..., east=..., down=..., vn=..., ve=..., vd=...
```

## Configuración metodológica de logging

### Variables registradas actualmente

- `run_id`
- `sample_idx`
- `timestamp`
- `vehicle_name`
- `position_x`, `position_y`, `position_z`
- `orientation_w`, `orientation_x`, `orientation_y`, `orientation_z`
- `velocity_x`, `velocity_y`, `velocity_z`
- `landed_state`

### Variables pendientes de incorporar

- `treatment`
- `scenario_id`
- `simulator_version`
- `autopilot_version`
- `camera_resolution`
- `command_type`
- `command_value`
- `status`
- `notes`

## Estado de cierre de Fase 02

La fase puede cerrarse como entorno experimental base validado con AirSimNH, PX4 SITL y MAVSDK. El cierre se sustenta en conexión AirSim, carga del UAV, captura de cámara, lectura de estado, comando básico, logging, repetibilidad inicial y conexión funcional con PX4 Autopilot.

Pendientes trasladables a la siguiente fase:

1. evidencia explícita de plataforma señalizada visible en cámara;
2. ampliación del registro experimental con todos los campos de `configs/experiment_config.json`.

## Incidencias trasladadas

Las incidencias técnicas de instalación, puertos, WSL2, rutas activas de `settings.json` y parámetros PX4 se mantienen en `06_known_issues.md` y `08_ayuda_memoria_fase02.md`. En este documento solo se conserva la configuración final consolidada y la evidencia operativa de cierre para evitar duplicar la bitácora de incidencias.
