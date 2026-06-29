# Fase 03 - Objetivo y Alcance

## Propósito

La Fase 03 implementa y valida el módulo de percepción visual del proyecto UAV Landing AI. El objetivo es detectar una plataforma o marcador de aterrizaje en imágenes capturadas desde AirSim, estimar su posición relativa en la imagen y dejar evidencia reproducible de las pruebas.

## Alcance

Esta fase cubre:

- captura de imágenes desde la cámara inferior `bottom_center`;
- detección visual de una plataforma o marcador con OpenCV;
- estimación del centro del marcador en píxeles;
- cálculo del error relativo respecto al centro de la imagen;
- generación de imágenes anotadas;
- registro CSV/JSON de resultados de detección;
- protocolo inicial de validación offline y en vivo.

Esta fase no cubre todavia:

- control autónomo completo de aterrizaje;
- generación de comandos Offboard hacia PX4 a partir de la detección;
- evaluación final de desempeño T0/T1;
- estimación métrica 3D completa de la plataforma en coordenadas mundo.

## Nota metodológica sobre HSV/color y ArUco

El detector HSV/color de Fase 03 fue una etapa inicial válida para comprobar captura desde `bottom_center`, segmentación, cálculo de centroide, error visual, repetibilidad y generación de evidencia anotada. Esa evidencia no se elimina ni se reinterpreta como fallida: cumple el rol de validación perceptiva inicial.

Para el cierre del lazo de control y la experimentación formal, el proyecto adoptó marcador fiduciario ArUco. La decisión responde a la necesidad de contar con identidad verificable del marcador, trazabilidad por ID, menor ambigüedad frente a falsos positivos cromáticos y compatibilidad con la integración PX4/MAVLink directo validada en Fase 04.

| Criterio | HSV/color | ArUco |
| --- | --- | --- |
| Identidad del marcador | No codifica identidad; depende de color y contorno. | Codifica diccionario e ID verificable (`DICT_4X4_50`, ID `23`). |
| Riesgo de falso positivo | Mayor ante texturas, hojas, sombras o regiones cromáticas similares. | Menor, al requerir patrón fiduciario válido e ID esperado. |
| Uso en control activo | Adecuado para `dry-run` y validación inicial; no se adopta como referencia final. | Adoptado para control activo, abort seguro y descenso asistido. |
| Trazabilidad experimental | Registra detección y centroide, pero sin identidad semántica del objetivo. | Registra `detector_method=aruco_fiducial` y `aruco_id=23`. |
| Rol dentro de la tesis | Etapa inicial de percepción y evidencia de funcionamiento del pipeline visual. | Referencia final para integración de control y comparación T0/T1. |

## Entradas

- Imágenes RGB/BGR de AirSim desde `bottom_center`.
- Configuración de cámara en `configs/experiment_config.json`.
- Parámetros de detección en `configs/perception_config.json`.

## Salidas

- Imagen cruda guardada en `data/raw/`.
- Imagen anotada en `data/processed/phase03_perception/` o `outputs/figures/phase03_perception/`.
- CSV de validación en `data/logs/`.
- JSON de corrida en vivo en `outputs/figures/phase03_perception/`.

## Criterio general de cierre

La fase se considera validada cuando el detector identifica el marcador en imágenes representativas, entrega posición relativa, genera evidencia visual anotada y deja registros reproducibles para al menos tres corridas comparables.
