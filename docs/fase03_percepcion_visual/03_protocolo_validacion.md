# Protocolo de Validacion de Percepcion

## Preparacion

1. Abrir el entorno AirSim correspondiente a la prueba:
   - `Blocks` para depuracion controlada del detector;
   - `AirSimNH` para la evidencia experimental principal.
2. Confirmar que el UAV `Drone1` esta cargado.
3. Confirmar que la camara `bottom_center` esta configurada.
4. Colocar o habilitar una plataforma o marcador visible para la camara inferior.
5. Activar el entorno virtual Python 3.10.

```powershell
cd <REPO_ROOT>
.\.venv\Scripts\Activate.ps1
```

## Secuencia metodologica recomendada

La validacion debe avanzar en dos niveles:

| Nivel | Entorno | Proposito | Criterio |
| --- | --- | --- | --- |
| 1 | Blocks | Probar el detector en una escena simple con fondo claro | Obtener al menos un `detected=True` con marcador visible |
| 2 | AirSimNH | Repetir la deteccion en el entorno experimental principal | Obtener deteccion positiva y evidencia comparable |

Blocks se usa como prueba controlada del algoritmo. AirSimNH se mantiene como entorno principal porque fue el entorno validado en Fase 02 junto con PX4 SITL y MAVSDK.

## Validacion offline

La validacion offline procesa imagenes ya guardadas en `data/raw/`.

Puede indicarse el directorio, entorno y escenario:

```powershell
python src\perception\validate_perception.py --input-dir data\raw --environment Blocks --scenario-id P03_BLOCKS_MARKER
```

Evidencias esperadas:

- CSV en `data/logs/`;
- imagenes anotadas en `data/processed/phase03_perception/`;
- salida por consola con `detected` y `confidence`.

## Validacion en vivo

La validacion en vivo captura una imagen desde AirSim, ejecuta deteccion y guarda evidencias.

Para Blocks, primero se puede intentar crear un marcador rojo directamente desde Python:

```powershell
python src\perception\spawn_landing_marker.py
```

Si el marcador no queda dentro del campo de vision, repetir ajustando posicion o escala:

```powershell
python src\perception\spawn_landing_marker.py --x 0 --y 0 --z 0 --scale-x 3 --scale-y 3 --scale-z 0.03
```

En AirSimNH, si la vista externa muestra el marcador pero `bottom_center` ve otra zona, crear un marcador usando la posicion X/Y actual del UAV:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase03_landing_marker_under_uav --under-vehicle --z 0 --scale-x 3 --scale-y 3 --scale-z 0.03
```

Luego ejecutar:

```powershell
python src\perception\perception_pipeline.py --environment Blocks --scenario-id P03_BLOCKS_MARKER
```

Si el marcador aparece en la vista externa pero la camara `bottom_center` no lo detecta, elevar el UAV antes de capturar:

```powershell
python src\perception\perception_pipeline.py --environment Blocks --scenario-id P03_BLOCKS_MARKER --altitude-m 3
```

En AirSimNH con PX4, los comandos de movimiento por API pueden no elevar el UAV porque PX4 controla el vehiculo. Para diagnostico de percepcion, usar `simSetVehiclePose` mediante `--pose-mode sim_pose`:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3 --pose-mode sim_pose
```

Este modo solo debe usarse como posicionamiento de escena para validar percepcion visual; no representa una maniobra autonoma de control.

Si la plataforma queda fuera del encuadre, se pueden probar coordenadas NED explicitas:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3 --pose-mode sim_pose --pose-x 0 --pose-y 0
```

Repetir variando `--pose-x` y `--pose-y` hasta centrar el marcador.

Si se desea aterrizar automaticamente despues de la captura:

```powershell
python src\perception\perception_pipeline.py --environment Blocks --scenario-id P03_BLOCKS_MARKER --altitude-m 3 --land-after-capture
```

Si la vista externa muestra el marcador pero `bottom_center` captura otra zona, ejecutar diagnostico de camaras:

```powershell
python src\perception\diagnose_camera_views.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

El diagnostico guarda imagenes por camara y un CSV con poses en:

```text
outputs/figures/phase03_perception/<environment>/<scenario_id>/
```

Para AirSimNH:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

Evidencias esperadas:

- imagen cruda en `data/raw/`;
- imagen anotada en `outputs/figures/phase03_perception/`;
- JSON de resultado en `outputs/figures/phase03_perception/`;
- salida por consola con centro y error relativo si hay deteccion.

Las salidas en vivo se organizan por entorno y escenario:

```text
data/raw/phase03_perception/<environment>/<scenario_id>/
outputs/figures/phase03_perception/<environment>/<scenario_id>/
```

## Pruebas minimas

| Codigo | Prueba | Criterio de aceptacion |
| --- | --- | --- |
| P03-V01 | Captura con marcador visible | Al menos una imagen muestra claramente la plataforma o marcador |
| P03-V02 | Deteccion positiva offline | Imagen con marcador devuelve `detected=True` |
| P03-V03 | Deteccion negativa | Imagen sin marcador devuelve `detected=False` o confianza baja |
| P03-V04 | Error relativo | Se registran `error_x_px`, `error_y_px`, `error_x_norm`, `error_y_norm` |
| P03-V05 | Evidencia anotada | Se genera imagen con centro de camara, centro detectado y caja envolvente |
| P03-V06 | Repetibilidad | Tres corridas comparables generan resultados trazables |

## Registro recomendado

Cada corrida debe registrar:

- `run_id`;
- fecha y hora;
- imagen de entrada;
- imagen anotada;
- camara;
- entorno;
- escenario;
- resolucion;
- metodo de deteccion;
- parametros relevantes;
- resultado de deteccion;
- posicion relativa;
- observaciones.
