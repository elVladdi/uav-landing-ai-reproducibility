# Manual de Uso - Modulo de Percepcion Visual

## Proposito

Este manual describe como ejecutar el modulo de percepcion visual de Fase 03 para capturar imagenes desde AirSim, detectar una plataforma o marcador de aterrizaje y guardar evidencias reproducibles.

El manual cubre dos entornos:

- `Blocks`: entorno controlado para verificar rapidamente el detector.
- `AirSimNH`: entorno experimental principal validado para la tesis.

## Requisitos previos

- Repositorio ubicado en:

```text
<REPO_ROOT>
```

- Entorno virtual Python 3.10 disponible en `.venv`.
- AirSim o AirSimNH abierto.
- Vehiculo configurado como `Drone1`.
- Camara inferior configurada como `bottom_center`.
- Dependencias instaladas desde `requirements.txt`.

## Activar entorno Python

Desde PowerShell:

```powershell
cd <REPO_ROOT>
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Verificar Python:

```powershell
python --version
```

## Verificar conexion con AirSim

Con el simulador abierto:

```powershell
python src\connection\airsim_client.py
```

Criterio esperado:

```text
Conexion correcta con AirSim
Vehiculo: Drone1
```

Si esta prueba falla, no ejecutar todavia el modulo de percepcion.

## Crear marcador visual

El marcador puede generarse desde Python:

```powershell
python src\perception\spawn_landing_marker.py
```

Para AirSimNH se recomienda crear un marcador grande bajo la posicion actual del UAV:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase03_landing_marker_airsimnh --under-vehicle --z 0 --scale-x 4 --scale-y 4 --scale-z 0.03
```

Confirmar visualmente en la ventana del simulador que la plataforma o marcador aparece en escena.

## Ejecutar percepcion en Blocks

Blocks se usa como prueba controlada del detector.

Crear marcador:

```powershell
python src\perception\spawn_landing_marker.py
```

Ejecutar pipeline:

```powershell
python src\perception\perception_pipeline.py --environment Blocks --scenario-id P03_BLOCKS_MARKER --altitude-m 3
```

Resultado esperado:

```text
Detected: True
Relative error: dx=..., dy=...
```

Validar offline las imagenes generadas:

```powershell
python src\perception\validate_perception.py --input-dir data\raw\phase03_perception\blocks\p03_blocks_marker --environment Blocks --scenario-id P03_BLOCKS_MARKER
```

## Ejecutar percepcion en AirSimNH

AirSimNH es el entorno experimental principal. Con PX4 activo, los comandos AirSim de movimiento pueden no elevar el UAV, porque PX4 gobierna el vehiculo. Para validar percepcion visual se usa `sim_pose`.

Crear marcador:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase03_landing_marker_airsimnh --under-vehicle --z 0 --scale-x 4 --scale-y 4 --scale-z 0.03
```

Ejecutar pipeline:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3 --pose-mode sim_pose --pose-x 0 --pose-y 0
```

Resultado esperado:

```text
Detected: True
Relative error: dx=..., dy=...
```

Validar offline las imagenes generadas:

```powershell
python src\perception\validate_perception.py --input-dir data\raw\phase03_perception\airsimnh\p03_airsimnh_marker --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

## Diagnostico de camaras

Si el marcador se ve en la ventana externa, pero el detector no lo encuentra, capturar vistas de diagnostico:

```powershell
python src\perception\diagnose_camera_views.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --marker-name phase03_landing_marker_airsimnh --object-regex ".*phase03.*marker.*"
```

El diagnostico guarda imagenes por camara y un CSV en:

```text
outputs/figures/phase03_perception/airsimnh/p03_airsimnh_marker/
```

Usar este diagnostico para comprobar:

- si `bottom_center` ve realmente el marcador;
- si otra camara ve el marcador;
- si el UAV esta sobre la plataforma;
- si la API de AirSim devuelve la pose del objeto.

## Salidas generadas

El pipeline en vivo guarda:

```text
data/raw/phase03_perception/<environment>/<scenario_id>/
outputs/figures/phase03_perception/<environment>/<scenario_id>/
```

Archivos principales:

- imagen cruda `.png`;
- imagen anotada `_annotated.png`;
- resultado de deteccion `_detection.json`.

La validacion offline guarda:

```text
data/logs/*_perception_validation.csv
data/processed/phase03_perception/
```

## Interpretacion de resultados

Campos principales:

| Campo | Significado |
| --- | --- |
| `detected` | Indica si el detector acepto un marcador |
| `confidence` | Confianza heuristica basada principalmente en area relativa |
| `center_x`, `center_y` | Centro detectado del marcador en pixeles |
| `error_x_px`, `error_y_px` | Desplazamiento respecto al centro de la imagen |
| `error_x_norm`, `error_y_norm` | Error normalizado |
| `area_px` | Area del contorno detectado |
| `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height` | Caja envolvente |

Interpretacion de error:

- `error_x_px < 0`: marcador hacia la izquierda del centro de imagen.
- `error_x_px > 0`: marcador hacia la derecha del centro de imagen.
- `error_y_px < 0`: marcador hacia arriba del centro de imagen.
- `error_y_px > 0`: marcador hacia abajo del centro de imagen.

## Criterios de corrida valida

Una corrida positiva debe cumplir:

- el marcador es visible en la imagen cruda;
- `detected=True`;
- la caja anotada corresponde a la plataforma, no a hojas/sombras;
- `confidence` es alta;
- se guardan imagen cruda, imagen anotada y JSON;
- si se usa AirSimNH, el resultado se etiqueta con `environment=AirSimNH`.

Una corrida no debe aceptarse como positiva si:

- el marcador no aparece en la imagen;
- la caja verde cae sobre hojas, sombras o manchas;
- `detected=True` aparece con una region visualmente incorrecta;
- el resultado depende de la vista externa y no de `bottom_center`.

## Uso de `sim_pose`

`sim_pose` se usa para colocar temporalmente el UAV en una posicion conveniente de captura:

```powershell
--pose-mode sim_pose --pose-x 0 --pose-y 0 --altitude-m 3
```

Importante:

- sirve para validar percepcion visual;
- no representa control autonomo de vuelo;
- no sustituye comandos PX4 Offboard;
- debe documentarse cuando se use en una corrida.

## Repetibilidad recomendada

Para cerrar una validacion:

1. Ejecutar al menos tres corridas con la misma configuracion.
2. Confirmar `detected=True` en todas.
3. Revisar que `confidence` sea estable.
4. Comparar `error_x_px` y `error_y_px`.
5. Registrar resultados en `04_resultados_validacion.md`.

En la validacion final de Fase 03 se obtuvieron seis corridas positivas comparables en AirSimNH.

## Problemas frecuentes

### El pipeline conecta, pero `Detected: False`

Posibles causas:

- el marcador no esta visible para `bottom_center`;
- el marcador esta fuera de encuadre;
- el color capturado no coincide con los rangos HSV;
- el objeto detectado es demasiado pequeno.

Acciones:

- revisar imagen cruda;
- ejecutar diagnostico de camaras;
- confirmar visualmente el marcador;
- ajustar posicion con `sim_pose`;
- revisar `configs/perception_config.json`.

### La ventana externa muestra el marcador, pero `bottom_center` no

La vista externa no equivale a la camara del UAV. Ejecutar:

```powershell
python src\perception\diagnose_camera_views.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

### Aparecen falsos positivos

Revisar la imagen anotada. Si la caja cae sobre hojas o sombras, no aceptar la corrida como positiva. Ajustar:

- `min_area_px`;
- `min_confidence`;
- rangos HSV;
- condiciones por entorno.

## Cierre

Este manual permite repetir la validacion del modulo de percepcion visual. La Fase 03 valida deteccion y estimacion de posicion relativa en imagen. La integracion con control autonomo del UAV queda fuera de este manual y debe abordarse en una fase posterior.
