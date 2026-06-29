# Manual de arranque del entorno simulado

## Proposito

Este manual describe la secuencia correcta para levantar el entorno simulado del proyecto **UAV Landing AI**, integrando AirSimNH en Windows, PX4 Autopilot SITL en Ubuntu/WSL2 y el cliente Python/MAVSDK desde PowerShell.

El objetivo es que el entorno pueda iniciarse de forma repetible antes de ejecutar pruebas de percepcion visual, control, captura de imagen o logging experimental.

## Secuencia general

![Secuencia de arranque y validacion del entorno simulado](<Secuencia de arranque y validacion del entorno simulado.png>)

*Figura 3. Secuencia resumida para iniciar AirSimNH, PX4 SITL y el cliente Python/MAVSDK hasta confirmar telemetria.*

## Requisitos previos

Antes de iniciar, verificar que:

- AirSimNH esta instalado y disponible en Windows.
- Ubuntu 22.04 funciona en WSL2.
- PX4 Autopilot esta instalado en `~/PX4-Autopilot`.
- El repositorio del proyecto esta en `<REPO_ROOT>`.
- El entorno virtual `.venv` usa Python 3.10.
- El archivo activo de AirSimNH en esta laptop es `<AIRSIM_SETTINGS_PATH>`.
- El cliente PX4/MAVSDK apunta a `PX4_SYSTEM_ADDRESS=udpin://0.0.0.0:14601`.

> Nota: puede existir una copia sincronizada en OneDrive, pero AirSimNH lee el archivo activo desde `<AIRSIM_SETTINGS_PATH>` en esta laptop.

## 1. Abrir AirSimNH en Windows

Ejecutar AirSimNH y esperar a que cargue el escenario. Blocks puede abrirse solo para depuracion visual aislada; no forma parte de la secuencia principal de evidencia experimental con PX4.

Ruta validada en la laptop nueva:

```text
<AIRSIMNH_INSTALL_DIR>\AirSimNH.exe
```

Confirmar que AirSimNH haya cargado la configuracion activa desde:

```text
<AIRSIM_SETTINGS_PATH>
```

Indicadores esperados:

```text
Loaded settings from ...
Asset database ready!
```

<img width="960" height="659" alt="image" src="https://github.com/user-attachments/assets/0e0e2f69-14c3-4720-8645-6ce75f904f41" />

## 2. Abrir Ubuntu 22.04 en WSL2

Abrir la terminal de Ubuntu 22.04 y ubicarse en la carpeta de PX4:

```bash
cd ~/PX4-Autopilot
```

<img width="1241" height="188" alt="image" src="https://github.com/user-attachments/assets/17bd7d84-b8bc-4f2c-a52f-6f3b7cbb46cf" />

## 3. Verificar IPs actuales de WSL2

Las IPs de WSL2 pueden cambiar despues de reiniciar Windows, WSL o la red. Antes de iniciar PX4, verificar la IP del host Windows/WSL y la IP interna de Ubuntu.

En PowerShell, identificar la IP del adaptador WSL en Windows:

```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -match 'vEthernet|WSL' -and $_.IPAddress -notmatch '^169\.254' } | Select-Object InterfaceAlias, IPAddress
```

En Ubuntu/WSL2:

```bash
hostname -I
ip route | awk '/default/ {print $3; exit}'
```

Durante la configuracion de esta laptop se validaron estos valores:

```text
Windows/WSL host: 172.20.64.1
Ubuntu/WSL: 172.20.67.188
```

Estos valores son ejemplos, no constantes. En los comandos siguientes, reemplazar `<WINDOWS_WSL_HOST_IP>` por la IP actual del host Windows/WSL.

## 4. Iniciar PX4 SITL conectado a AirSim

Ejecutar PX4 indicando la IP actual del host Windows/WSL:

```bash
PX4_SIM_HOST_ADDR=<WINDOWS_WSL_HOST_IP> make px4_sitl_default none_iris
```

Ejemplo validado en esta laptop cuando el host Windows/WSL era `172.20.64.1`:

```bash
PX4_SIM_HOST_ADDR=172.20.64.1 make px4_sitl_default none_iris
```

Mensajes esperados:

```text
PX4_SIM_HOSTNAME: <WINDOWS_WSL_HOST_IP>
using TCP on remote host <WINDOWS_WSL_HOST_IP> port 4560
Waiting for simulator to accept connection on TCP port 4560
Simulator connected on TCP port 4560
Ready for takeoff!
```

<img width="1017" height="910" alt="image" src="https://github.com/user-attachments/assets/8c2b2993-b82d-4d28-a2e9-2cd084fe4d1b" />

## 5. Crear el canal MAVLink dedicado para Python/MAVSDK

Cuando PX4 muestre el prompt:

```text
pxh>
```

ejecutar:

```bash
mavlink start -x -u 14600 -r 4000000 -t <WINDOWS_WSL_HOST_IP> -o 14601 -m onboard
```

Ejemplo validado en esta laptop cuando el host Windows/WSL era `172.20.64.1`:

```bash
mavlink start -x -u 14600 -r 4000000 -t 172.20.64.1 -o 14601 -m onboard
```

Resultado esperado:

```text
INFO [mavlink] mode: Onboard, data rate: 4000000 B/s on udp port 14600 remote port 14601
```

<img width="923" height="130" alt="image" src="https://github.com/user-attachments/assets/a73bf91d-b676-4b79-958b-cfcdd1ffa32c" />

## 6. Abrir PowerShell en Windows

Entrar al repositorio:

```powershell
cd <REPO_ROOT>
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Debe aparecer el prefijo:

```text
(.venv)
```

<img width="1229" height="242" alt="image" src="https://github.com/user-attachments/assets/fe6cff01-bfd2-4479-8390-529bd42da945" />

## 7. Validar la conexion Python/MAVSDK con PX4

Ejecutar:

```powershell
.\scripts\check_px4_connection.ps1
```

Salida esperada:

```text
Conectando con PX4 en udpin://0.0.0.0:14601 ...
Conexion correcta con PX4
Health: global_position_ok=True, home_position_ok=True, local_position_ok=True
Armed: False
NED: north=..., east=..., down=..., vn=..., ve=..., vd=...
```

<img width="1103" height="169" alt="image" src="https://github.com/user-attachments/assets/cdd86045-8d58-442c-b537-dbe46228f46d" />

## 8. Criterio de entorno listo

El entorno se considera correctamente levantado cuando se cumplen estas condiciones:

- AirSimNH esta abierto y con el escenario cargado.
- PX4 muestra `Simulator connected on TCP port 4560`.
- PX4 muestra `Ready for takeoff!`.
- La instancia MAVLink dedicada queda activa en el puerto remoto `14601`.
- PowerShell muestra `Conexion correcta con PX4`.
- Se imprime telemetria NED desde el cliente Python.

<img width="1919" height="1017" alt="image" src="https://github.com/user-attachments/assets/9513b4c9-d81d-404f-8702-3f5574f17348" />

## 9. Problemas frecuentes

### PX4 queda esperando en TCP 4560

Sintoma:

```text
Waiting for simulator to accept connection on TCP port 4560
```

Acciones:

- Confirmar que AirSimNH esta abierto.
- Verificar que `settings.json` usa `PX4Multirotor`.
- Revisar que `PX4_SIM_HOST_ADDR` corresponde a la IP actual del host Windows/WSL.
- Reiniciar AirSimNH y luego reiniciar PX4.

### MAVSDK queda esperando conexion

Sintoma:

```text
Conectando con PX4 en udpin://0.0.0.0:14601 ...
```

y no avanza.

Acciones:

- Confirmar que el comando `mavlink start` se ejecuto en PX4.
- Verificar que el puerto remoto sea `14601`.
- Revisar `configs/px4_airsim.env`.
- No usar el puerto `14540` para MAVSDK si AirSim ya lo esta ocupando.
- Confirmar que el parametro `-t` de `mavlink start` usa la IP actual del host Windows/WSL.

Si se usa una IP antigua, por ejemplo `172.25.48.1` cuando la IP actual es `172.20.64.1`, PX4 puede mostrar el canal MAVLink activo pero el cliente Python quedara esperando en `udpin://0.0.0.0:14601`.

Para corregirlo desde el prompt `pxh>` de PX4:

```bash
mavlink stop-all
mavlink start -x -u 14600 -r 4000000 -t <WINDOWS_WSL_HOST_IP> -o 14601 -m onboard
```

### Error de bind en MAVSDK

Sintoma:

```text
bind error
Connection failed: Bind error
```

Acciones:

- Evitar usar `14540` para el cliente Python.
- Usar el canal dedicado `14601`.
- Cerrar procesos anteriores de PowerShell o Python que hayan quedado abiertos.

### PowerShell bloquea Activate.ps1

Sintoma:

```text
No se puede cargar el archivo .\.venv\Scripts\Activate.ps1 porque la ejecucion de scripts esta deshabilitada en este sistema.
```

Accion validada:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Luego activar nuevamente:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Parametro COM_OBL_ACT no encontrado

Sintoma:

```text
Error: parameter name 'COM_OBL_ACT' was not found
```

Acciones:

- Retirar `COM_OBL_ACT` del `settings.json` activo de AirSim.
- Reiniciar AirSimNH.
- Reiniciar PX4.

## 10. Secuencia resumida

```text
1. Abrir AirSimNH en Windows.
2. Abrir Ubuntu 22.04.
3. cd ~/PX4-Autopilot
4. Verificar la IP actual del host Windows/WSL.
5. PX4_SIM_HOST_ADDR=<WINDOWS_WSL_HOST_IP> make px4_sitl_default none_iris
6. Esperar: Simulator connected + Ready for takeoff.
7. En pxh>: mavlink start -x -u 14600 -r 4000000 -t <WINDOWS_WSL_HOST_IP> -o 14601 -m onboard
8. Abrir PowerShell.
9. cd <REPO_ROOT>
10. .\.venv\Scripts\Activate.ps1
11. .\scripts\check_px4_connection.ps1
12. Confirmar: Conexion correcta con PX4.
```

## 11. Nota sobre cambios de IP

Las IPs de WSL2 pueden cambiar despues de reiniciar Windows o WSL.

Si el entorno deja de conectar, verificar nuevamente:

- IP del host Windows/WSL.
- IP de Ubuntu/WSL.
- Valores en `settings.json`.
- Valor usado en `PX4_SIM_HOST_ADDR`.
- Destino `-t` del comando `mavlink start`.

Durante la validacion inicial de Fase 02 se usaron IPs distintas a las actuales. En la laptop nueva se valido `172.20.64.1` como host Windows/WSL y `172.20.67.188` como IP de Ubuntu/WSL. Estos valores son ejemplos, no constantes.

## 12. Resultado esperado de cierre

Al finalizar la secuencia, el entorno queda listo para ejecutar pruebas posteriores de:

- Percepcion visual.
- Captura de imagen.
- Deteccion de marcador o plataforma.
- Lectura de telemetria.
- Control asistido por PX4.
- Registro experimental.

Este manual complementa la ayuda memoria de Fase 02 y debe actualizarse si cambian puertos, IPs, versiones de PX4, ruta activa de AirSim o secuencia de arranque.
