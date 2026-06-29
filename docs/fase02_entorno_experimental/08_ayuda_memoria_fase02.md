# Ayuda memoria de Fase 02

## Datos generales

**Proyecto:** UAV Landing AI  
**Fase:** Fase 02 - Configuracion y validacion del entorno experimental  
**Objetivo de la fase:** dejar operativo, documentado y verificable el entorno base de simulacion antes de avanzar al desarrollo del modulo de percepcion visual y control autonomo.

## Proposito de este documento

Este documento registra, en forma de ayuda memoria, las actividades realizadas durante la Fase 02, los problemas encontrados, las decisiones tecnicas tomadas y la configuracion final validada para integrar AirSim, PX4 Autopilot y el cliente Python mediante MAVSDK/MAVLink.

La finalidad es conservar trazabilidad tecnica para poder reproducir el entorno, justificar las decisiones de configuracion y cerrar la fase con evidencia suficiente.

## Punto de partida

El proyecto ya contaba con una estructura inicial en Python para validar AirSim directamente:

- conexion con AirSim;
- comando basico de despegue, vuelo estacionario y aterrizaje;
- captura de imagen desde camara simulada;
- registro basico de estado del UAV;
- entorno virtual `.venv` basado en Python 3.10.

Se mantuvo Python 3.10 porque AirSim presenta incompatibilidades o problemas de instalacion con versiones superiores. Esta decision permitio ejecutar las pruebas iniciales sin romper la compatibilidad con el cliente Python de AirSim.

## Validaciones iniciales con AirSim

Antes de integrar PX4, se verifico el funcionamiento del simulador y de los scripts base:

```powershell
python src\control\command_test.py
python src\perception\camera_test.py
python src\logging\run_logger.py
```

Resultados observados:

- AirSim respondio correctamente a la conexion desde Python.
- El UAV pudo despegar, mantenerse en vuelo, aterrizar y liberar el control API.
- Se capturaron imagenes en `data/raw/`.
- Se generaron logs CSV en `data/logs/`.

Durante esta etapa aparecio el error:

```text
ModuleNotFoundError: No module named 'utils'
```

La causa fue la ejecucion directa de scripts sin que la raiz del proyecto estuviera correctamente disponible en `sys.path`. Se corrigio ajustando los imports y la ruta base del proyecto.

## Documentacion y estructura creada

Para hacer trazable la Fase 02 se agregaron documentos y archivos de configuracion:

- `README.md`: vision general del proyecto, instalacion, ejecucion y estado de la fase.
- `docs/installation_notes.md`: notas de instalacion y configuracion.
- `docs/environment_validation.md`: matriz de validacion del entorno.
- `docs/known_issues.md`: incidencias y riesgos tecnicos.
- `docs/justificacion_entornos.md`: justificacion metodologica de los entornos.
- `docs/px4_airsim_setup.md`: guia tecnica de PX4 + AirSim.
- `configs/experiment_config.json`: configuracion base para experimentos.
- `configs/px4_airsim.env`: variables de conexion MAVSDK/PX4.
- `configs/airsim_px4_settings.example.json`: plantilla de configuracion de AirSim para PX4.

## Instalacion de Ubuntu y PX4

Para ejecutar PX4 SITL se uso Ubuntu 22.04 en WSL2. Durante el proceso aparecio un problema importante: la terminal de Ubuntu abria, pero quedaba en pantalla negra sin permitir escribir comandos.

La incidencia se resolvio reinstalando la distribucion WSL:

```powershell
wsl --shutdown
wsl --unregister Ubuntu-22.04
wsl --install -d Ubuntu-22.04
```

Luego se creo el usuario Linux `vladimir` y se continuo con la instalacion de PX4 Autopilot en:

```bash
~/PX4-Autopilot
```

Se ejecutaron las dependencias de PX4 y se verifico que el objetivo SITL estuviera disponible.

## Descubrimiento de la ruta activa de AirSim

Un punto critico fue identificar que AirSim no estaba leyendo la configuracion desde la ruta clasica:

```text
<AIRSIM_SETTINGS_PATH>
```

AirSim estaba cargando la configuracion activa desde:

```text
<AIRSIM_SETTINGS_PATH>
```

Este hallazgo fue importante porque cualquier cambio realizado en la ruta equivocada no tenia efecto en el simulador.

## Cambio de AirSim a PX4Multirotor

Inicialmente AirSim funcionaba con SimpleFlight. Para integrarlo con PX4 se actualizo `settings.json` a `PX4Multirotor`, conservando la configuracion de camaras y adaptando los parametros de red para WSL2.

Los elementos principales de la configuracion validada fueron:

```json
{
  "VehicleType": "PX4Multirotor",
  "UseTcp": true,
  "TcpPort": 4560,
  "ControlPortLocal": 14540,
  "ControlPortRemote": 14580,
  "LocalHostIp": "172.25.48.1",
  "ControlIp": "172.25.54.40",
  "QgcHostIp": "172.25.48.1",
  "LogViewerHostIp": "172.25.48.1",
  "LockStep": true,
  "ClockType": "SteppableClock"
}
```

En esta configuracion:

- `172.25.48.1` correspondio al adaptador Windows/WSL.
- `172.25.54.40` correspondio a la IP de Ubuntu en WSL2.
- `TcpPort` 4560 permitio la conexion AirSim <-> PX4.

## Incidencias durante PX4 + AirSim

### PX4 esperando al simulador

Al iniciar PX4 con:

```bash
make px4_sitl_default none_iris
```

PX4 quedaba esperando:

```text
Waiting for simulator to accept connection on TCP port 4560
```

La causa fue que PX4 estaba intentando comunicarse con el simulador en una direccion que no correspondia al host de Windows. Se corrigio iniciando PX4 con la IP del host Windows/WSL:

```bash
PX4_SIM_HOST_ADDR=172.25.48.1 make px4_sitl_default none_iris
```

### Parametro obsoleto COM_OBL_ACT

AirSim reporto:

```text
Error: parameter name 'COM_OBL_ACT' was not found
```

Esto indico que el parametro ya no existia o no era compatible con la version de PX4 usada. Se retiro de la configuracion de AirSim para evitar errores repetitivos.

### Advertencias de preflight

Durante el arranque aparecieron advertencias como:

```text
Preflight Fail: ekf2 missing data
Preflight Fail: system power unavailable
Preflight Fail: heading estimate invalid
Preflight Fail: GPS fix too low
```

Estas advertencias fueron transitorias o propias del arranque inicial del sistema simulado. El criterio relevante fue que PX4 terminara mostrando:

```text
Ready for takeoff!
```

### Reglas de firewall

Para evitar bloqueos de red en Windows se habilitaron reglas para los puertos usados por PX4/AirSim/MAVLink:

```powershell
netsh advfirewall firewall add rule name="UAV PX4 MAVSDK UDP 14540" dir=in action=allow protocol=UDP localport=14540
netsh advfirewall firewall add rule name="UAV PX4 MAVLink UDP 14550" dir=in action=allow protocol=UDP localport=14550
netsh advfirewall firewall add rule name="UAV PX4 MAVLink UDP 14580" dir=in action=allow protocol=UDP localport=14580
netsh advfirewall firewall add rule name="UAV PX4 AirSim TCP 4560" dir=in action=allow protocol=TCP localport=4560
```

### Conflicto de puerto 14540

El cliente MAVSDK en Windows no podia conectarse correctamente cuando intentaba escuchar en el mismo puerto usado por AirSim. Se observaron errores como:

```text
bind error: No error
Connection failed: Bind error
```

La solucion fue no reutilizar el puerto 14540 para el cliente Python y crear un canal MAVLink dedicado.

### Mensaje MAVLink only on localhost

PX4 mostro:

```text
MAVLink only on localhost (set param MAV_{i}_BROADCAST = 1 to enable network)
```

Se habilito broadcast en las instancias MAVLink principales:

```bash
param set MAV_1_BROADCAST 1
param set MAV_0_BROADCAST 1
param save
```

Sin embargo, la solucion final mas limpia fue crear una instancia MAVLink dedicada para el cliente Python.

## Configuracion final validada

Con AirSim abierto en Windows, se inicio PX4 desde Ubuntu/WSL con:

```bash
cd ~/PX4-Autopilot
PX4_SIM_HOST_ADDR=172.25.48.1 make px4_sitl_default none_iris
```

Cuando PX4 mostro el prompt `pxh>`, se creo una instancia MAVLink exclusiva para MAVSDK:

```bash
mavlink start -x -u 14600 -r 4000000 -t 172.25.48.1 -o 14601 -m onboard
```

El proyecto Python quedo configurado para escuchar en:

```env
PX4_SYSTEM_ADDRESS=udpin://0.0.0.0:14601
PX4_CONNECTION_TIMEOUT_SECONDS=5
```

## Validacion final

Desde PowerShell, con el entorno virtual activo:

```powershell
cd <REPO_ROOT>
.\.venv\Scripts\Activate.ps1
.\scripts\check_px4_connection.ps1
```

La salida final confirmada fue:

```text
Conectando con PX4 en udpin://0.0.0.0:14601 ...
Conexion correcta con PX4
Health: global_position_ok=True, home_position_ok=True, local_position_ok=True
Armed: False
NED: north=-0.000, east=-0.001, down=-0.002, vn=-0.002, ve=-0.003, vd=-0.002
```

Esta salida valida que:

- PX4 SITL esta ejecutandose correctamente en Ubuntu/WSL.
- AirSim esta conectado a PX4 por TCP 4560.
- El cliente Python se conecta a PX4 mediante MAVSDK.
- La telemetria basica de posicion y velocidad esta disponible.

## Estado de cierre de la Fase 02

La Fase 02 queda cerrada como entorno experimental base validado. Se comprobo:

- ejecucion del simulador AirSim;
- carga del UAV;
- captura de imagen;
- lectura de estado;
- comando basico de vuelo con AirSim;
- logging inicial;
- instalacion de Ubuntu/WSL;
- compilacion y ejecucion de PX4 SITL;
- conexion AirSim + PX4;
- conexion Python/MAVSDK + PX4 por canal dedicado.

## Lecciones aprendidas

- En WSL2, las IP de Windows y Ubuntu deben tratarse explicitamente; no basta con asumir `localhost`.
- AirSim puede leer `settings.json` desde una ruta de OneDrive, por lo que la ruta activa debe confirmarse visualmente en el simulador.
- No conviene reutilizar el puerto 14540 para MAVSDK si AirSim ya lo ocupa.
- Un canal MAVLink dedicado reduce conflictos y deja mas clara la arquitectura.
- Las advertencias de preflight deben analizarse, pero el criterio operativo para esta fase fue alcanzar `Ready for takeoff!` y confirmar telemetria desde Python.
- La documentacion de incidencias es parte del resultado tecnico, porque permite reproducir el entorno sin repetir el mismo proceso de prueba y error.

## Pendientes fuera del cierre de Fase 02

Los siguientes puntos pueden abordarse al iniciar la siguiente etapa metodologica:

- incorporar la plataforma senalizada visible en camara;
- ampliar el logger con variables experimentales completas;
- automatizar el arranque de la instancia MAVLink dedicada;
- registrar versiones exactas de PX4, AirSim y Windows/WSL en cada corrida.
