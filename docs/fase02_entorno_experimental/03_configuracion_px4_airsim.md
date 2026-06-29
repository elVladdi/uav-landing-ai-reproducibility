# Configuración de PX4 Autopilot con AirSim

Guía técnica para el proyecto **UAV Landing AI**.

**Proyecto:** Agente de inteligencia artificial basado en visión por computador para aterrizaje autónomo de UAV.
**Autor:** Vladimir Molleapasa Gutierrez
**Repositorio:** `<REPO_ROOT>`
**Objetivo:** documentar la configuración inicial de PX4 + AirSim y su integración con Python/MAVSDK.
**Alcance:** configuración de simulación. No cubre pruebas en hardware real ni vuelo físico.
**Fecha:** abril de 2026.

## Indice

1. Propósito y contexto
2. Arquitectura PX4 + AirSim + Python
3. Prerrequisitos
4. Archivos agregados al repositorio
5. Configuración de AirSim
6. Configuración de PX4 y MAVSDK
7. Validación de conexión
8. Flujo de pruebas recomendado
9. Troubleshooting
10. Relación con el diseño experimental

## 1. Propósito y contexto

El proyecto busca implementar un agente de inteligencia artificial basado en visión por computador para ejecutar el aterrizaje autónomo de un UAV sobre una plataforma señalizada en un entorno controlado de simulación.

En esta etapa, AirSimNH queda como entorno visual y físico principal para la integración con PX4, mientras que PX4 Autopilot se incorpora como autopiloto para aportar una capa de control más cercana a sistemas UAV reales. Blocks se mantiene únicamente como antecedente de validación temprana y entorno auxiliar de depuración.

La integración propuesta evita reemplazar los scripts actuales de AirSim. En su lugar, agrega una capa separada de comunicación con PX4 mediante MAVSDK/MAVLink, de forma que el proyecto pueda evolucionar progresivamente desde pruebas de simulación básicas hacia maniobras autónomas con Offboard.

## 2. Arquitectura PX4 + AirSim + Python

- **AirSimNH:** entorno 3D, física, sensores simulados, cámara inferior y plataforma de aterrizaje señalizada.
- **PX4 Autopilot:** armado, desarmado, estabilización, despegue, aterrizaje, failsafe y modo Offboard.
- **Python Agent:** captura de imagen, detección ArUco/AprilTag, decisión de corrección, envío de comandos y logging experimental.
- **MAVSDK/MAVLink:** canal de comunicación entre Python y PX4 para telemetría y comandos de alto nivel.

```text
AirSimNH -> mundo 3D, cámara, sensores y física
PX4     -> autopiloto y control de vuelo
Python  -> visión por computador, agente IA, logging y métricas

Python Agent -> MAVSDK/MAVLink -> PX4 -> AirSim
```

### Figura de arquitectura

![Arquitectura del entorno experimental PX4 + AirSim + Python](<Arquitectura del entorno experimental.png>)

*Figura 4. Arquitectura funcional del entorno experimental con AirSimNH, PX4, MAVSDK/MAVLink y el agente Python.*

## 3. Prerrequisitos

- **Sistema operativo:** Windows con AirSim ejecutandose de forma nativa. WSL2 puede usarse para compilar o ejecutar PX4 SITL si se requiere.
- **Python:** Python 3.10 dentro de `.venv`, por compatibilidad con AirSim.
- **AirSim:** instalacion funcional ya validada con los scripts actuales del proyecto.
- **PX4:** PX4 Autopilot configurado para SITL o HIL segun el tipo de prueba.
- **QGroundControl:** recomendado para inspeccionar conexión, parámetros y estado del vehículo.
- **Dependencias Python:** `airsim`, `numpy`, `opencv-python`, `mavsdk` y `python-dotenv`.

### Decision tecnica

Se mantiene Python 3.10 porque AirSim puede presentar incompatibilidades con versiones superiores. MAVSDK se instala inicialmente en el mismo entorno; si hubiera conflicto, se documentara un segundo entorno dedicado para PX4.

## 4. Archivos agregados al repositorio

- `requirements.txt`: dependencias base para AirSim, OpenCV y PX4/MAVSDK.
- `configs/px4_airsim.env`: variables de conexión, timeout y parámetros iniciales de prueba.
- `configs/airsim_px4_settings.example.json`: plantilla de `settings.json` para AirSim con `PX4Multirotor`.
- `src/connection/px4_client.py`: cliente Python/MAVSDK para validar conexión y leer telemetría PX4.
- `scripts/check_px4_connection.ps1`: script PowerShell que ejecuta la prueba con el `.venv` del proyecto.
- `docs/px4_airsim_setup.md`: resumen técnico en Markdown de la integración.

## 5. Configuración de AirSim

AirSim utiliza un archivo `settings.json` ubicado normalmente en la carpeta `Documents/AirSim` del usuario. Para integrar PX4, el vehículo debe declararse como `PX4Multirotor` y exponer los puertos necesarios para comunicación MAVLink.

Pasos recomendados:

1. Guardar una copia de respaldo del `settings.json` actual de AirSim.
2. Abrir la plantilla `configs/airsim_px4_settings.example.json`.
3. Copiar su contenido al `settings.json` real de AirSim, ajustando rutas o parametros si fuera necesario.
4. Verificar que el nombre del vehículo sea `Drone1` y que la cámara inferior sea `bottom_center`.
5. Iniciar AirSim y confirmar que el escenario carga sin errores.

Rutas habituales:

```text
<AIRSIM_SETTINGS_PATH>
<AIRSIM_SETTINGS_PATH>
```

### Parametros clave del `settings.json`

- `VehicleType: PX4Multirotor`: indica que AirSim usara PX4 como autopiloto del multirrotor.
- `UseTcp: true`: AirSim espera comunicación TCP con PX4 en el puerto configurado.
- `TcpPort: 4560`: puerto usado por la conexión simulador-PX4.
- `ControlPortLocal: 14540`: puerto local usado por clientes SDK, como MAVSDK Python.
- `LockStep: true`: sincroniza simulador y autopiloto para mayor estabilidad temporal.
- `COM_OBL_ACT: 1`: suaviza la salida de Offboard, haciendo que el dron tienda a hover en lugar de aterrizar de inmediato.

> Nota: durante la validación real de Fase 02 se retiró `COM_OBL_ACT` porque la versión usada de PX4 lo reportó como parámetro desconocido.

## 6. Configuración de PX4 y MAVSDK

PX4 puede ejecutarse en modo SITL o integrarse con AirSim como simulador externo. En esta primera fase del proyecto, la meta no es ejecutar aterrizaje autónomo completo, sino comprobar que Python puede conectarse con PX4 y leer telemetría.

Instalar dependencias Python:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Variables de conexión iniciales:

```env
PX4_SYSTEM_ADDRESS=udp://:14540
PX4_CONNECTION_TIMEOUT_SECONDS=30
VEHICLE_NAME=Drone1
BOTTOM_CAMERA_NAME=bottom_center
PX4_TEST_ALTITUDE_M=3.0
```

Configuración validada al cierre de Fase 02:

```env
PX4_SYSTEM_ADDRESS=udpin://0.0.0.0:14601
PX4_CONNECTION_TIMEOUT_SECONDS=5
```

## 7. Validación de conexión

La validación inicial se realiza con el script `check_px4_connection.ps1`. Este script carga las variables desde `configs/px4_airsim.env` y ejecuta `src/connection/px4_client.py` con el Python del `.venv` si existe.

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\check_px4_connection.ps1
```

La salida esperada debe indicar conexión correcta con PX4, estado de health, estado de armado y una muestra de posición/velocidad en coordenadas NED.

## 8. Flujo de pruebas recomendado

1. Confirmar que los scripts actuales de AirSim siguen funcionando: `command_test.py`, `camera_test.py` y `run_logger.py`.
2. Configurar AirSim con `PX4Multirotor` y validar que el simulador inicia sin errores.
3. Conectar Python con PX4 usando MAVSDK y registrar telemetría básica.
4. Implementar prueba controlada de arm, takeoff, hover y land solo en simulación.
5. Integrar percepción visual con OpenCV y marcador fiduciario.
6. Implementar tratamientos `T0` y `T1` del protocolo experimental.

## 9. Troubleshooting

- **MAVSDK no conecta:** verificar que PX4 este corriendo, que el puerto coincida y que no haya firewall bloqueando UDP.
- **AirSim no carga el dron:** revisar que `settings.json` sea JSON valido y que `VehicleType` sea `PX4Multirotor`.
- **Python no encuentra `airsim`:** activar `.venv` y confirmar que se usa Python 3.10.
- **El dron se comporta inestable:** verificar `LockStep`, parámetros PX4, punto inicial del vehículo y configuración del barómetro.
- **Offboard se desactiva:** PX4 requiere flujo continuo de setpoints o senal de vida a mas de 2 Hz.
- **QGroundControl no muestra estado correcto:** revisar puertos MAVLink, parametros de PX4 y orden de arranque entre AirSim y PX4.

## 10. Relación con el diseño experimental

La configuración PX4 + AirSim soporta el diseño experimental definido en el perfil del proyecto. AirSim permite repetir escenarios controlados de altura, desplazamiento lateral y orientación inicial, mientras PX4 permite ejecutar maniobras con un autopiloto abierto y documentable.

- **T0:** descenso o aterrizaje base sin corrección visual inteligente.
- **T1:** aterrizaje autónomo con agente de visión por computador.
- **Métricas:** error final de posicionamiento, tiempo de aterrizaje, dinámica lateral de aproximación, actividad correctiva y tasa de éxito.
- **Datos por corrida:** imágenes, telemetría, estimación relativa, comandos emitidos y resultado final.

## Referencias tecnicas

- PX4 Autopilot. AirSim Simulation. <https://docs.px4.io/main/en/sim_airsim/index>
- Microsoft AirSim. PX4 Setup for AirSim. <https://microsoft.github.io/AirSimExtensions/px4_setup/>
- Microsoft AirSim. PX4 in SITL. <https://microsoft.github.io/AirSimExtensions/px4_sitl/>
- PX4 Autopilot. Offboard Mode. <https://docs.px4.io/main/en/flight_modes/offboard>

## Advertencia

AirSim con PX4 puede depender de versiones especificas y su soporte actual es comunitario. Por ello, cada corrida experimental debe registrar versiones de AirSim, PX4, Python y dependencias instaladas.
