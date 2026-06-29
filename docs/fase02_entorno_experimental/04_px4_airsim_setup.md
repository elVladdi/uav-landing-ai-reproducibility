# Configuracion PX4 + AirSim

Este proyecto usa AirSim para el entorno visual/fisico y PX4 Autopilot como
autopiloto. El agente Python se conectara a PX4 mediante MAVSDK/MAVLink y
seguira usando AirSim para camara y datos visuales.

## Arquitectura objetivo

```text
AirSim
  entorno 3D, fisica, camara inferior, plataforma senalizada

PX4
  armado, desarmado, takeoff, land, estabilizacion y Offboard

Python
  vision por computador, decision del agente, comandos MAVSDK, logging
```

## Entorno Python

Mantener Python 3.10 para compatibilidad con AirSim.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si `mavsdk` no instala correctamente en el mismo `.venv`, se recomienda crear
un segundo entorno dedicado para PX4 y documentar esa decision.

## AirSim settings.json

AirSim lee su configuracion desde:

```text
<AIRSIM_SETTINGS_PATH>
```

o, segun la configuracion de OneDrive/Windows:

```text
<AIRSIM_SETTINGS_PATH>
```

Usa `configs/airsim_px4_settings.example.json` como plantilla. Antes de
sobrescribir tu archivo real, guarda una copia de respaldo.

## Prueba de conexion PX4

Con PX4 y AirSim corriendo:

```powershell
.\scripts\check_px4_connection.ps1
```

Tambien puedes ejecutar directamente:

```powershell
python src\connection\px4_client.py
```

La conexion por defecto es:

```text
udpin://0.0.0.0:14601
```

Puedes cambiarla editando:

```text
configs/px4_airsim.env
```

## Orden recomendado de validacion

1. Verificar que tus scripts actuales de AirSim siguen funcionando.
2. Configurar AirSim con `PX4Multirotor`.
3. Iniciar PX4 SITL y AirSim.
4. Ejecutar `scripts/check_px4_connection.ps1`.
5. Registrar telemetria PX4 en CSV.
6. Probar `arm`, `takeoff` y `land` solo en simulacion.
7. Integrar percepcion: camara inferior + marcador ArUco/AprilTag.
8. Implementar tratamiento T0 y T1 para el protocolo experimental.

## Notas de seguridad experimental

El control Offboard debe probarse solamente en simulacion al inicio. PX4 requiere
un flujo continuo de setpoints o senales de vida a mas de 2 Hz para mantener
Offboard activo. Si ese flujo se detiene, PX4 activa el comportamiento failsafe
configurado.
