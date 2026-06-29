# Incidencias y Riesgos Tecnicos

## Proposito

Este documento registra problemas tecnicos encontrados o riesgos previstos durante la Fase 02. Su objetivo es mantener trazabilidad y facilitar la reproduccion del entorno experimental.

## Incidencias encontradas

### KI-001: Compatibilidad de AirSim con versiones de Python superiores a 3.10

**Estado:** controlado.

AirSim puede presentar problemas de instalacion o ejecucion con versiones recientes de Python. Por ello se decidio usar un entorno virtual `.venv` con Python 3.10.

Medidas:

- mantener el proyecto con Python 3.10;
- registrar dependencias en `requirements.txt`;
- activar siempre `.venv` antes de ejecutar scripts.

### KI-002: Error de importacion de modulos locales

**Estado:** corregido.

Durante pruebas iniciales aparecio:

```text
ModuleNotFoundError: No module named 'utils'
```

Causa probable: ejecucion directa de scripts sin que la raiz del proyecto estuviera disponible en `sys.path`.

Medidas:

- los scripts principales agregan la raiz del proyecto a `sys.path`;
- los imports usan rutas desde `src`, por ejemplo `from src.utils.constants import ...`.

### KI-003: Integracion PX4 + AirSim depende de versiones y puertos

**Estado:** controlado.

PX4 + AirSim puede requerir configuraciones especificas de puertos, modo de conexion y version de simulador/autopiloto.

Durante la validacion de Fase 02 se confirmo que AirSimNH inicialmente operaba con control AirSim/SimpleFlight. Luego se configuro `PX4Multirotor`, se ejecuto PX4 SITL en WSL2 y se creo una instancia MAVLink dedicada para MAVSDK.

Medidas propuestas:

- usar `configs/px4_airsim.env` para centralizar variables;
- usar `configs/airsim_px4_settings.example.json` como plantilla;
- validar conexion con `scripts/check_px4_connection.ps1`;
- registrar version de PX4 y AirSim en futuras corridas.

Configuracion validada:

```text
PX4_SIM_HOST_ADDR=172.25.48.1 make px4_sitl_default none_iris
mavlink start -x -u 14600 -r 4000000 -t 172.25.48.1 -o 14601 -m onboard
PX4_SYSTEM_ADDRESS=udpin://0.0.0.0:14601
```

### KI-004: Falta de evidencia de plataforma senalizada visible

**Estado:** pendiente.

Ya existe captura de camara, pero todavia debe confirmarse que la plataforma senalizada aparece en el campo de vision.

Medidas propuestas:

- configurar la plataforma o marcador fiduciario en el escenario;
- capturar nueva imagen desde `bottom_center`;
- guardar evidencia en `data/raw/` o `outputs/figures/`.

### KI-005: Registro experimental todavia incompleto

**Estado:** pendiente.

El CSV actual registra estado basico del UAV, pero aun no incluye todas las variables solicitadas en Fase 02.

Medidas propuestas:

- ampliar `src/logging/run_logger.py`;
- agregar `configs/experiment_config.json`;
- registrar tratamiento, escenario, versiones, resolucion de camara, comando, estado final y observaciones.

## Riesgos tecnicos previstos

| Riesgo | Efecto posible | Medida de control |
| --- | --- | --- |
| Incompatibilidad AirSim/PX4/Windows | Retraso en configuracion | Registrar versiones funcionales |
| Comunicacion inestable con PX4 | Perdida de comandos o telemetria | Validar comandos simples antes del agente |
| Baja tasa de cuadros de camara | Percepcion visual lenta | Registrar FPS y resolucion |
| Latencia elevada | Correcciones tardias durante descenso | Medir tiempo de ciclo |
| Escenario inicial demasiado complejo | Dificulta depuracion | Iniciar en Blocks |
| Falta de trazabilidad | Resultados no auditables | Registrar run_id, parametros y salidas |

## Politica de actualizacion

Cada nueva incidencia debe registrarse con codigo, fecha, descripcion, causa probable, medida aplicada o propuesta y estado.
