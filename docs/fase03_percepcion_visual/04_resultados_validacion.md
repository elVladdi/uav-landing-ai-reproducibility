# Resultados de Validación

## Estado inicial

La estructura de Fase 03 ya permite ejecutar validación offline y en vivo. Las capturas heredadas de Fase 02 muestran terreno desde la cámara inferior, pero no confirman todavía una plataforma o marcador de aterrizaje claramente visible.

El módulo de percepción ya fue ejecutado en dos modos:

- validación offline sobre imágenes existentes en `data/raw/`;
- pipeline en vivo con conexión a AirSim y captura desde `bottom_center`.

En ambos casos el resultado fue `detected=False`, lo cual es coherente con la evidencia visual disponible: las imágenes muestran terreno/vegetación y no una plataforma o marcador visible. Por ello, el primer resultado pendiente sigue siendo capturar nueva evidencia con marcador visible.

Posteriormente se generó un marcador controlado en Blocks mediante `src/perception/spawn_landing_marker.py`, se elevó el UAV a 3 m y se obtuvo la primera detección positiva del módulo de percepción.

## Nota metodológica HSV/color vs ArUco

Los resultados de esta fase deben leerse como validación del pipeline perceptivo inicial basado en HSV/color: captura de cámara, segmentación, centroide, cálculo de error visual, repetibilidad y generación de evidencia. No se elimina la evidencia HSV porque sustenta la evolución técnica del proyecto.

Para control activo y experimentación formal, la tesis adopta ArUco desde Fase 04. Esta transición responde a la necesidad de identidad verificable, trazabilidad por marcador y menor ambigüedad frente a falsos positivos del entorno.

| Criterio | HSV/color en Fase 03 | ArUco desde Fase 04 |
| --- | --- | --- |
| Identidad del marcador | No hay ID codificado; se acepta por color/contorno. | ID verificable mediante diccionario e identificador. |
| Riesgo de falso positivo | Observado en AirSimNH con hojas/sombras o regiones cromáticas similares. | Reducido al exigir `aruco_id=23` y marcador fiduciario válido. |
| Uso en control activo | No se adopta como referencia final de control. | Referencia principal para corrección lateral, abort seguro y descenso asistido. |
| Trazabilidad experimental | Evidencia de centroide, error y confianza. | Evidencia de método, ID, aceptación del marcador y comando asociado. |
| Rol dentro de la tesis | Validación inicial de percepción y repetibilidad visual. | Base perceptiva del lazo cerrado y de la comparación T0/T1. |

## Tabla de resultados

| Fecha | Run ID | Tipo | Imagen | Resultado | Observaciones |
| --- | --- | --- | --- | --- | --- |
| 2026-05-01 | `phase03_20260501_112825_938adc92` | Offline | Capturas heredadas en `data/raw/` | `detected=False`, `confidence=0.000` | Caso negativo válido: no se observa marcador en las imágenes |
| 2026-05-01 | `phase03_20260501_113742_ddf1edb6` | En vivo | `data/raw/phase03_20260501_113742_ddf1edb6_bottom_center.png` | `detected=False`, `confidence=0.000` | AirSim conectó y el pipeline generó evidencia; la escena no contiene marcador visible |
| 2026-05-01 | `phase03_20260501_123327_dbd36c7a` | En vivo | `data/raw/phase03_20260501_123327_dbd36c7a_bottom_center.png` | `detected=False`, `confidence=0.000` | AirSim conectó; la cámara observa una superficie clara uniforme sin marcador visible |
| 2026-05-01 | `phase03_20260501_123407_089860ee` | Offline | Imágenes actualizadas en `data/raw/` | `detected=False`, `confidence=0.000` | Validación offline completa con siete imágenes; todas son casos negativos |
| 2026-05-01 | `phase03_20260501_130751_128cd5d5` | En vivo / Blocks | `data/raw/phase03_perception/blocks/p03_blocks_marker/phase03_20260501_130751_128cd5d5_bottom_center.png` | `detected=True`, `confidence=1.000` | Primera detección positiva controlada. Error relativo: `dx=-4.29 px`, `dy=8.54 px` |
| 2026-05-01 | `phase03_20260501_132849_2737d038` | En vivo / AirSimNH | `data/raw/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_132849_2737d038_bottom_center.png` | Falso positivo preliminar, `confidence=0.046` | La caja detectada corresponde a una hoja/mancha azul, no a la plataforma. No se acepta como validación positiva |
| 2026-05-01 | `phase03_20260501_134258_e6023aeb` / `phase03_20260501_134319_4fbc28a0` | Barrido / AirSimNH | Capturas `pose-x/pose-y` | Falsos positivos | Las cajas detectadas corresponden a sombra/hojas, no a plataforma. El usuario confirma que no se observa marcador rojo en AirSimNH |
| 2026-05-01 | `phase03_20260501_134845_6b35b147` | En vivo / AirSimNH | `data/raw/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_134845_6b35b147_bottom_center.png` | `detected=False` antes de ajuste HSV | La plataforma era visible en cámara, pero AirSimNH estaba usando solo rangos rojos; la cámara representó la plataforma como azul/cian |
| 2026-05-01 | `phase03_20260501_135214_dd9fc625` | Offline / AirSimNH | Carpeta `data/raw/phase03_perception/airsimnh/p03_airsimnh_marker/` | `detected=True`, `confidence=1.000` para `phase03_20260501_134845_6b35b147` | Validación offline positiva con plataforma visible. Error relativo: `dx=-90.80 px`, `dy=-4.18 px` |
| 2026-05-01 | `phase03_20260501_135239_e8ae6aed` | En vivo / AirSimNH | `data/raw/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center.png` | `detected=True`, `confidence=1.000` | Validación positiva en entorno experimental principal con `sim_pose`. Error relativo: `dx=-92.08 px`, `dy=-1.81 px` |
| 2026-05-01 | `phase03_20260501_135617_065613be` a `phase03_20260501_135635_53a2e881` | Repetibilidad / AirSimNH | Cinco capturas adicionales con marcador visible | 5/5 `detected=True`, `confidence=1.000` | Repetibilidad positiva. Sumadas a la primera corrida aceptada: 6/6 detecciones positivas |

## Evidencia generada

### Validación offline

Archivo CSV:

```text
data/logs/phase03_20260501_112825_938adc92_perception_validation.csv
```

Resultados registrados:

- `capture_bottom_center_20260426_185846.png`: `detected=False`, `confidence=0.000`;
- `capture_bottom_center_20260427_202447.png`: `detected=False`, `confidence=0.000`;
- `capture_bottom_center_20260427_204552.png`: `detected=False`, `confidence=0.000`.

Las imagenes anotadas se generaron en:

```text
data/processed/phase03_perception/
```

### Validación en vivo

Primera corrida en vivo:

Archivo JSON:

```text
outputs/figures/phase03_perception/phase03_20260501_113742_ddf1edb6_bottom_center_detection.json
```

Imagen cruda:

```text
data/raw/phase03_20260501_113742_ddf1edb6_bottom_center.png
```

Imagen anotada:

```text
outputs/figures/phase03_perception/phase03_20260501_113742_ddf1edb6_bottom_center_annotated.png
```

Resultado principal:

```text
detected=false
confidence=0.0
notes=No contour matched configured thresholds.
```

La captura en vivo confirma que `perception_pipeline.py` pudo conectarse a AirSim, capturar imagen desde `bottom_center`, ejecutar el detector y guardar evidencia reproducible.

Segunda corrida en vivo:

```text
outputs/figures/phase03_perception/phase03_20260501_123327_dbd36c7a_bottom_center_detection.json
data/raw/phase03_20260501_123327_dbd36c7a_bottom_center.png
outputs/figures/phase03_perception/phase03_20260501_123327_dbd36c7a_bottom_center_annotated.png
```

Resultado principal:

```text
detected=false
confidence=0.0
notes=No contour matched configured thresholds.
```

La segunda captura en vivo muestra una superficie clara uniforme. Esto confirma nuevamente que el pipeline funciona, pero todavia no existe un marcador visible dentro del campo de vision.

### Segunda validación offline

Archivo CSV:

```text
data/logs/phase03_20260501_123407_089860ee_perception_validation.csv
```

Esta corrida proceso siete imagenes de `data/raw/` y todas registraron `detected=False`, `confidence=0.000`. El resultado mantiene la interpretacion de caso negativo: no hay marcador contrastante visible en las capturas disponibles.

### Primera detección positiva controlada en Blocks

Se creo un marcador visual con:

```powershell
python src\perception\spawn_landing_marker.py
```

Luego se ejecuto el pipeline elevando el UAV a 3 m:

```powershell
python src\perception\perception_pipeline.py --environment Blocks --scenario-id P03_BLOCKS_MARKER --altitude-m 3
```

Archivo JSON:

```text
outputs/figures/phase03_perception/blocks/p03_blocks_marker/phase03_20260501_130751_128cd5d5_bottom_center_detection.json
```

Imagen cruda:

```text
data/raw/phase03_perception/blocks/p03_blocks_marker/phase03_20260501_130751_128cd5d5_bottom_center.png
```

Imagen anotada:

```text
outputs/figures/phase03_perception/blocks/p03_blocks_marker/phase03_20260501_130751_128cd5d5_bottom_center_annotated.png
```

Resultado principal:

```text
detected=true
confidence=1.0
center_x=315.709
center_y=248.539
error_x_px=-4.291
error_y_px=8.539
error_x_norm=-0.013
error_y_norm=0.036
area_px=84883.5
```

Interpretacion: el detector identifica correctamente el marcador en una escena controlada de Blocks. El centro detectado queda cerca del centro de la imagen, con error horizontal de -4.29 pixeles y vertical de 8.54 pixeles.

### Validación positiva en AirSimNH

Se recreó el marcador en AirSimNH y se confirmó visualmente su presencia en el entorno. Para posicionar el UAV solo con fines de percepción se usó `sim_pose`, ya que el control de movimiento por API no eleva el vehículo cuando PX4 gobierna la simulación.

Comando de captura:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3 --pose-mode sim_pose --pose-x 0 --pose-y 0
```

Archivo JSON:

```text
outputs/figures/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center_detection.json
```

Imagen cruda:

```text
data/raw/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center.png
```

Imagen anotada:

```text
outputs/figures/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center_annotated.png
```

Resultado principal:

```text
detected=true
confidence=1.0
center_x=227.920
center_y=238.186
error_x_px=-92.080
error_y_px=-1.814
error_x_norm=-0.288
error_y_norm=-0.008
area_px=197464.0
pose_mode=sim_pose
```

Interpretación: el detector identifica correctamente la plataforma en AirSimNH desde la cámara `bottom_center`. La plataforma aparece desplazada hacia la izquierda de la imagen, lo que se refleja en `error_x_px=-92.08`. La detección se acepta como validación visual positiva del módulo de percepción en el entorno experimental principal.

Figura de evidencia visual:

![Validación visual del detector HSV/color en AirSimNH](<Validacion visual del detector en AirSimNH.png>)

*Figura 5. Validación visual del detector HSV/color en AirSimNH mediante comparación entre imagen cruda de `bottom_center` y salida anotada.*

Nota metodológica: `sim_pose` se usa como posicionamiento de escena para validar percepción visual. No representa control autónomo del UAV mediante PX4.

### Repetibilidad en AirSimNH

Se repitió la captura en AirSimNH con el marcador visible y la misma configuración de escena. Las seis corridas aceptadas fueron:

| Run ID | `center_x` | `center_y` | `error_x_px` | `error_y_px` | `confidence` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `phase03_20260501_135239_e8ae6aed` | 227.920 | 238.186 | -92.080 | -1.814 | 1.000 |
| `phase03_20260501_135617_065613be` | 227.496 | 237.741 | -92.504 | -2.259 | 1.000 |
| `phase03_20260501_135623_b046ad67` | 228.104 | 237.622 | -91.896 | -2.378 | 1.000 |
| `phase03_20260501_135627_8b27272c` | 227.429 | 237.849 | -92.571 | -2.151 | 1.000 |
| `phase03_20260501_135630_08bc0886` | 228.007 | 237.610 | -91.993 | -2.390 | 1.000 |
| `phase03_20260501_135635_53a2e881` | 227.880 | 237.551 | -92.120 | -2.449 | 1.000 |

Resumen:

```text
n=6
mean_error_x_px=-92.194
mean_error_y_px=-2.240
confidence_min=1.000
confidence_max=1.000
error_x_range=[-92.571, -91.896]
error_y_range=[-2.449, -1.814]
```

Figura de repetibilidad:

![Diagrama de dispersión de la detección visual HSV/color en AirSimNH](<Diagrama de dispersion V2.png>)

*Figura 6. Dispersión de los errores `error_x_px` y `error_y_px` en seis corridas positivas comparables del detector HSV/color en AirSimNH.*

Interpretación: las corridas repetidas son consistentes. La detección permanece estable, con confianza máxima y variación subpíxel aproximada en los errores medidos. Esto satisface el criterio de repetibilidad visual para el módulo de percepción en AirSimNH.

## Comandos de referencia

```powershell
python src\perception\validate_perception.py
python src\perception\perception_pipeline.py
```

## Evidencias esperadas

- CSV de validacion en `data/logs/`.
- Imagenes anotadas en `data/processed/phase03_perception/`.
- JSON e imagen anotada de corrida en vivo en `outputs/figures/phase03_perception/`.

## Cierre de resultados

Estado actual: infraestructura de percepcion implementada, validada en casos negativos, validada positivamente en Blocks como entorno controlado y validada positivamente en AirSimNH como entorno experimental principal mediante posicionamiento de escena `sim_pose`. La repetibilidad en AirSimNH quedo registrada con seis corridas positivas comparables. La Fase 03 queda tecnicamente validada en percepcion visual; el siguiente paso metodologico es preparar la integracion posterior con control visual, manteniendo claro que `sim_pose` no representa control autonomo PX4.
