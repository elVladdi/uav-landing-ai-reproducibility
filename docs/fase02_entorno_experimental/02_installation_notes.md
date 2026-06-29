# Notas de Instalacion y Configuracion

## Proposito

Este documento registra los pasos de instalacion y configuracion usados en la Fase 02 para preparar el entorno experimental del proyecto `uav-landing-ai`.

## Ruta del proyecto

```text
<REPO_ROOT>
```

## Entorno Python

Se utiliza un entorno virtual local `.venv` con Python 3.10 debido a la compatibilidad de AirSim con esta version.

```powershell
cd <REPO_ROOT>
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Dependencias principales:

- `airsim==1.8.1`
- `numpy`
- `opencv-python`
- `mavsdk`
- `python-dotenv`

## Configuracion de AirSim

AirSim lee su configuracion desde el archivo `settings.json`, ubicado normalmente en una de estas rutas:

```text
<AIRSIM_SETTINGS_PATH>
<AIRSIM_SETTINGS_PATH>
```

El vehiculo del proyecto es `Drone1`. La camara principal para aterrizaje es `bottom_center`, orientada hacia abajo.

## Configuracion PX4 + AirSim

La plantilla inicial para AirSim con PX4 esta en:

```text
configs/airsim_px4_settings.example.json
```

Las variables de conexion PX4 estan en:

```text
configs/px4_airsim.env
```

Conexion MAVSDK por defecto:

```text
PX4_SYSTEM_ADDRESS=udpin://0.0.0.0:14601
```

## Validacion inicial AirSim

Con AirSim abierto:

```powershell
python src\connection\airsim_client.py
python src\control\command_test.py
python src\perception\camera_test.py
python src\logging\run_logger.py
```

## Validacion inicial PX4

Con PX4 y AirSim ejecutandose:

```powershell
.\scripts\check_px4_connection.ps1
```

La salida esperada debe confirmar conexion con PX4 y mostrar health, estado de armado y posicion/velocidad NED.

## Sistema de coordenadas

AirSim utiliza coordenadas NED:

- `X`: hacia adelante.
- `Y`: hacia la derecha.
- `Z`: hacia abajo.

Por ello, una altura positiva sobre el suelo se representa con `Z` negativo. Por ejemplo:

```text
altura 5 m -> z = -5.0
```

## Evidencia producida

La Fase 02 ya cuenta con evidencia inicial:

- imagen capturada en `data/raw/`;
- log de estado en `data/logs/`;
- documentacion PX4 + AirSim en `docs/configuracion_px4_airsim.docx`;
- configuraciones iniciales en `configs/`.
