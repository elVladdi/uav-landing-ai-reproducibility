# Método de Detección Visual

## Método inicial

El módulo inicial usa segmentación por color en espacio HSV y selección de contornos con OpenCV. La elección es deliberadamente simple y reproducible para un entorno controlado de simulación. Su propósito fue validar el pipeline visual completo antes de exigir identidad fiduciaria o cerrar el lazo con PX4.

Archivo principal:

```text
src/perception/landing_marker_detector.py
```

Configuración:

```text
configs/perception_config.json
```

## Flujo del algoritmo

1. Recibir una imagen BGR.
2. Aplicar suavizado Gaussiano.
3. Convertir de BGR a HSV.
4. Segmentar los rangos de color configurados del marcador.
5. Aplicar operaciones morfológicas de apertura y cierre.
6. Buscar contornos externos.
7. Filtrar por área mínima, área máxima relativa y circularidad mínima.
8. Seleccionar el contorno de mayor área.
9. Calcular centroide con momentos de imagen.
10. Calcular error respecto al centro de la imagen.

## Resultado de detección

El detector devuelve:

- `detected`: indica si se encontró marcador;
- `center_x`, `center_y`: centroide en píxeles;
- `error_x_px`, `error_y_px`: desplazamiento respecto al centro de imagen;
- `error_x_norm`, `error_y_norm`: desplazamiento normalizado en rango aproximado [-1, 1];
- `area_px`, `area_ratio`: tamaño del marcador detectado;
- `confidence`: indicador heurístico inicial;
- `bbox_x`, `bbox_y`, `bbox_width`, `bbox_height`: caja envolvente;
- `notes`: información adicional del contorno.

## Supuestos

- El marcador tiene color contrastante frente al terreno.
- La configuración contempla rangos por entorno. En Blocks se admiten rojo/naranja y azul/cian porque el marcador puede verse rojo en la vista externa y azul/cian en la imagen capturada. En AirSimNH también se admiten azul/cian, pero con área mínima mucho mayor para evitar falsos positivos por hojas o manchas pequeñas en la vía.
- La cámara `bottom_center` observa la plataforma durante la prueba.
- La iluminación simulada no cambia drásticamente entre corridas.
- La resolución base es 640 x 480.

## Uso de Blocks y AirSimNH

La validación del detector se documenta en dos entornos con roles metodológicos distintos:

- `Blocks`: entorno controlado auxiliar para probar rápidamente el algoritmo, idealmente con fondo claro y marcador rojo/naranja visible.
- `AirSimNH`: entorno experimental principal para generar evidencia alineada con la integración PX4/AirSim/MAVLink validada en Fase 02.

La detección positiva en Blocks no cierra por sí sola la Fase 03. Sirve para confirmar que el detector funciona. La evidencia principal debe repetirse en AirSimNH.

## Transición metodológica hacia ArUco

HSV/color permitió comprobar que el sistema podía capturar imágenes, segmentar un objetivo, calcular centroide, estimar error visual y guardar evidencia reproducible. Sin embargo, el cierre del lazo de control requiere una referencia visual menos ambigua. Por ello, la Fase 04 adopta ArUco como referencia principal para control activo y Fase 05.

| Criterio | HSV/color | ArUco |
| --- | --- | --- |
| Identidad del marcador | No codifica ID. | Codifica diccionario e ID. |
| Riesgo de falso positivo | Sensible a colores similares, sombras o texturas. | Menor si se exige ID esperado. |
| Uso en control activo | Conservado para `dry-run` histórico y pruebas iniciales. | Usado en control lateral, abort seguro y descenso asistido. |
| Trazabilidad experimental | Limitada a contorno, área, centroide y confianza. | Alta: registra `detector_method` y `aruco_id`. |
| Rol dentro de la tesis | Validación inicial del pipeline perceptivo. | Referencia final para integración con autopiloto y experimento T0/T1. |

## Resultado controlado inicial

En Blocks se obtuvo una primera detección positiva con el marcador generado desde Python. La imagen capturada por `bottom_center` mostró el marcador en tonos azul/cian, por lo que se incluyeron rangos HSV adicionales para cubrir esa representación visual.

Resultado de referencia:

```text
run_id=phase03_20260501_130751_128cd5d5
environment=Blocks
scenario_id=P03_BLOCKS_MARKER
detected=true
confidence=1.0
error_x_px=-4.291
error_y_px=8.539
```

En AirSimNH se observaron falsos positivos sobre hojas/sombras con los rangos azul/cian. Después se confirmó que la plataforma roja visible en la ventana externa también aparece azul/cian en `bottom_center`. Por ello, la configuración de AirSimNH mantiene azul/cian, pero exige mayor área mínima y confianza.

## Limitaciones

Este método puede fallar si:

- el marcador no aparece en el campo de visión;
- el color del marcador se parece al terreno;
- hay sombras fuertes o baja iluminación;
- el marcador ocupa un área demasiado pequeña;
- existen objetos del mismo color en la escena.

Estas limitaciones justificaron la migración metodológica a ArUco para Fase 04, sin invalidar la evidencia HSV como validación inicial de Fase 03.
