# Migracion a Marcador Fiduciario ArUco

## Justificacion

El marcador HSV usado en Fase 03 y en las primeras pruebas de Fase 04 permitio
validar el flujo completo de camara, deteccion, error visual, comando calculado
y logging. Para las pruebas nuevas de control visual se migra a un marcador
fiduciario ArUco porque:

- codifica un ID verificable;
- reduce dependencia de color e iluminacion;
- mejora la reproducibilidad experimental;
- se alinea mejor con el perfil del proyecto, que contempla plataforma marcada
  y deteccion visual formal.

El detector HSV queda conservado como respaldo y como evidencia historica de la
Fase 03. El detector ArUco pasa a ser el detector activo en
`configs/perception_config.json`.

## Configuracion adoptada

```text
Familia: ArUco
Diccionario: DICT_4X4_50
ID esperado: 23
Detector activo: aruco_fiducial
```

Archivos principales:

- `src/perception/fiducial_marker_detector.py`
- `src/perception/detector_factory.py`
- `src/perception/spawn_fiducial_marker.py`
- `configs/perception_config.json`
- `src/control/run_visual_servo_dry_run.py`
- `src/control/run_mavlink_visual_servo_test.py`

## Dependencia

ArUco requiere el modulo `cv2.aruco`, incluido en `opencv-contrib-python`.

Verificacion:

```powershell
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'aruco'))"
```

El segundo valor debe ser `True`.

## Protocolo piloto

Generar textura sin conectar con AirSim:

```powershell
python src\perception\spawn_fiducial_marker.py --generate-only --dictionary-name DICT_4X4_50 --marker-id 23
```

Validacion centrada en AirSimNH:

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_center --under-vehicle --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06C_ARUCO_FIDUCIAL_DRY_RUN
python src\perception\clear_landing_markers.py
python src\control\run_px4_land.py --confirm-send --timeout 45
```

Resultado validado:

```text
Run ID: phase04_20260502_154838_c02260b6
Detecciones aceptadas: 10/10
Detector: aruco_fiducial
ID detectado: 23
Estado: centered=True en todas las muestras
Comandos: cercanos a cero, sin envio a PX4
```

Validacion lateral:

```powershell
python src\perception\clear_landing_markers.py
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_offset_y_pos --under-vehicle --offset-y 0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06D_ARUCO_OFFSET_Y_POS
python src\perception\clear_landing_markers.py
```

Repetir con `--offset-y -0.8` y
`--object-name phase04_aruco_marker_offset_y_neg`. Al terminar ambas corridas,
limpiar el marcador y aterrizar con PX4.

```powershell
python src\perception\spawn_fiducial_marker.py --object-name phase04_aruco_marker_offset_y_neg --under-vehicle --offset-y -0.8 --z 0 --scale-x 2.5 --scale-y 2.5 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_visual_servo_dry_run.py --environment AirSimNH --samples 10 --with-px4 --save-annotated --detector aruco --scenario-id P04_V06D_ARUCO_OFFSET_Y_NEG
python src\perception\clear_landing_markers.py
python src\control\run_px4_land.py --confirm-send --timeout 45
```

Resultado validado:

```text
Run IDs: phase04_20260502_161432_94a82568 / phase04_20260502_162846_45e3e817
Detecciones aceptadas: 10/10 en ambas corridas
Detector: aruco_fiducial
ID detectado: 23
Offset positivo: error_x_norm promedio aprox. +0.418; command_right_m_s promedio aprox. +0.105
Offset negativo: error_x_norm promedio aprox. -0.389; command_right_m_s promedio aprox. -0.097
Estado: signo lateral validado en dry-run, sin envio de comandos PX4
```

## Criterios de aceptacion

- El CSV registra `detector_method=aruco_fiducial`.
- `detection_notes` contiene `aruco_id=23`.
- La imagen anotada muestra centro del marcador y vector de error.
- En marcador centrado, los comandos laterales quedan cerca de cero.
- En marcador desplazado, `command_right_m_s` cambia de signo al invertir
  `--offset-y`.
- El marcador se genera despues del despegue y se elimina antes de aterrizar
  para evitar interferencia con la escena.

## Nota metodologica

Esta migracion no cambia la arquitectura de control. Solo cambia la fuente de
la medicion visual. La salida entregada al controlador conserva los mismos
campos: `error_x_norm`, `error_y_norm`, `confidence` y `detected`.

En la ruta final de Fase 04, esa salida alimenta el controlador visual activo
en `run_mavlink_visual_servo_test.py`, que envia setpoints MAVLink directos a
PX4 mediante `pymavlink`. El script heredado `run_visual_landing_trial.py`
queda como referencia de la propuesta MAVSDK inicial, no como ruta validada.
