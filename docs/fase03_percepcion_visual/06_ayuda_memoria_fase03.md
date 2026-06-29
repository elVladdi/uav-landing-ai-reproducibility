# Ayuda Memoria - Fase 03 Percepcion Visual

## Proposito

Este documento resume el proceso tecnico seguido durante la Fase 03: implementacion y validacion del modulo de percepcion visual. Su objetivo es conservar la trazabilidad de decisiones, problemas encontrados, ajustes realizados y evidencias generadas.

La fase partio del entorno validado en Fase 02: AirSim, PX4 SITL en WSL2, AirSimNH, camara `bottom_center` y conexion Python/MAVSDK. En Fase 03 se implemento un detector visual para identificar una plataforma o marcador de aterrizaje en imagenes de AirSim y estimar su posicion relativa en la imagen.

## Punto de partida

Al inicio de la fase ya existian:

- `src/connection/airsim_client.py`: conexion reutilizable con AirSim.
- `src/perception/camera_test.py`: captura simple desde `bottom_center`.
- `src/logging/run_logger.py`: base de logging de estado.
- `configs/experiment_config.json`: parametros de camara, rutas, escenarios y tratamientos.
- `data/raw/`: capturas heredadas de Fase 02.

Las imagenes iniciales mostraban terreno o superficies sin marcador visible. Por tanto, los primeros resultados negativos fueron coherentes y sirvieron como casos base.

## Estructura implementada

Durante la fase se agregaron los siguientes elementos:

```text
configs/perception_config.json
src/perception/landing_marker_detector.py
src/perception/perception_pipeline.py
src/perception/validate_perception.py
src/perception/spawn_landing_marker.py
src/perception/diagnose_camera_views.py
docs/fase03_percepcion_visual/
```

El detector principal quedo en `src/perception/landing_marker_detector.py`. Usa segmentacion HSV, operaciones morfologicas, busqueda de contornos y calculo de centroide. El resultado incluye:

- `detected`;
- `center_x`, `center_y`;
- `error_x_px`, `error_y_px`;
- `error_x_norm`, `error_y_norm`;
- `area_px`, `area_ratio`;
- `confidence`;
- `bbox`;
- notas de diagnostico.

## Validacion inicial negativa

Primero se ejecuto la validacion offline sobre capturas heredadas:

```powershell
python src\perception\validate_perception.py
```

Resultado:

```text
detected=False
confidence=0.000
```

Tambien se ejecuto el pipeline en vivo:

```powershell
python src\perception\perception_pipeline.py
```

Las capturas mostraban terreno o una superficie clara sin marcador visible. Esto confirmo que el pipeline de conexion, captura y logging funcionaba, pero todavia no habia evidencia positiva del marcador.

## Uso de Blocks como entorno controlado

Se decidio usar Blocks como entorno controlado para depurar el detector antes de repetir en AirSimNH. Blocks ofrece una escena mas simple y menos ambigua.

Para crear un marcador se agrego:

```powershell
python src\perception\spawn_landing_marker.py
```

Luego se ejecuto el pipeline con trazabilidad de entorno:

```powershell
python src\perception\perception_pipeline.py --environment Blocks --scenario-id P03_BLOCKS_MARKER --altitude-m 3
```

Resultado positivo controlado:

```text
run_id=phase03_20260501_130751_128cd5d5
environment=Blocks
scenario_id=P03_BLOCKS_MARKER
detected=true
confidence=1.0
error_x_px=-4.291
error_y_px=8.539
```

Observacion importante: aunque el marcador se veia rojo en la ventana externa, la camara `bottom_center` lo capturaba en tonos azul/cian. Por ello se ampliaron los rangos HSV.

## Transicion a AirSimNH

AirSimNH era el entorno experimental principal definido desde Fase 02. Al pasar a AirSimNH aparecieron varios problemas:

1. el marcador no siempre era visible desde la camara inferior;
2. `takeoffAsync` y `moveToPositionAsync` no elevaban el UAV de forma confiable porque PX4 gobierna el vehiculo;
3. las hojas o manchas azul/cian de la via generaban falsos positivos;
4. `simGetObjectPose` devolvia `nan` para algunos nombres de marcador.

Para diagnosticar las camaras se agrego:

```powershell
python src\perception\diagnose_camera_views.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

Este script guarda imagenes de varias camaras y un CSV de poses en:

```text
outputs/figures/phase03_perception/airsimnh/p03_airsimnh_marker/
```

## Uso de `sim_pose`

En AirSimNH con PX4, la elevacion por comandos API no fue suficiente para posicionar el UAV sobre el marcador. Para validar percepcion visual se agrego `--pose-mode sim_pose`, que usa `simSetVehiclePose`.

Comando usado:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3 --pose-mode sim_pose --pose-x 0 --pose-y 0
```

Nota metodologica: `sim_pose` se usa solo para posicionamiento de escena y validacion visual. No representa control autonomo con PX4.

## Falsos positivos y ajustes

Se observaron falsos positivos en AirSimNH:

```text
phase03_20260501_132849_2737d038
phase03_20260501_134258_e6023aeb
phase03_20260501_134319_4fbc28a0
```

Las cajas detectadas correspondian a hojas, sombras o manchas de color, no a la plataforma. Por ello se ajusto la configuracion:

- `min_area_px`;
- `min_confidence`;
- rangos HSV por entorno.

Finalmente se definieron overrides por entorno en `configs/perception_config.json`:

- Blocks: acepta rojo/naranja y azul/cian.
- AirSimNH: acepta rojo/naranja y azul/cian, pero con area minima y confianza mas estrictas.

Este ajuste permite detectar la plataforma grande y rechazar hojas pequenas.

## Validacion positiva en AirSimNH

Se recreo el marcador en AirSimNH:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase03_landing_marker_airsimnh --under-vehicle --z 0 --scale-x 4 --scale-y 4 --scale-z 0.03
```

Luego se confirmo visualmente la presencia del marcador rojo en la escena. La camara `bottom_center` lo represento en azul/cian, por lo que se ajustaron los rangos HSV de AirSimNH para aceptar esa representacion con filtros estrictos.

Corrida positiva principal:

```text
run_id=phase03_20260501_135239_e8ae6aed
environment=AirSimNH
scenario_id=P03_AIRSIMNH_MARKER
detected=true
confidence=1.0
center_x=227.920
center_y=238.186
error_x_px=-92.080
error_y_px=-1.814
pose_mode=sim_pose
```

Evidencias:

```text
data/raw/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center.png
outputs/figures/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center_annotated.png
outputs/figures/phase03_perception/airsimnh/p03_airsimnh_marker/phase03_20260501_135239_e8ae6aed_bottom_center_detection.json
```

## Repetibilidad

Se repitio la captura en AirSimNH con la misma configuracion. Se obtuvieron seis corridas positivas comparables:

```text
phase03_20260501_135239_e8ae6aed
phase03_20260501_135617_065613be
phase03_20260501_135623_b046ad67
phase03_20260501_135627_8b27272c
phase03_20260501_135630_08bc0886
phase03_20260501_135635_53a2e881
```

Resumen:

```text
n=6
detected=true en 6/6 corridas
confidence=1.000 en 6/6 corridas
mean_error_x_px=-92.194
mean_error_y_px=-2.240
error_x_range=[-92.571, -91.896]
error_y_range=[-2.449, -1.814]
```

Interpretacion: la deteccion es estable y repetible en AirSimNH para la configuracion de escena validada.

## Comandos principales

Validacion offline:

```powershell
python src\perception\validate_perception.py --input-dir data\raw\phase03_perception\airsimnh\p03_airsimnh_marker --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

Crear marcador:

```powershell
python src\perception\spawn_landing_marker.py --object-name phase03_landing_marker_airsimnh --under-vehicle --z 0 --scale-x 4 --scale-y 4 --scale-z 0.03
```

Pipeline en AirSimNH:

```powershell
python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3 --pose-mode sim_pose --pose-x 0 --pose-y 0
```

Diagnostico de camaras:

```powershell
python src\perception\diagnose_camera_views.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER
```

## Estado final de Fase 03

La Fase 03 queda tecnicamente validada en percepcion visual:

- el detector fue implementado;
- el pipeline offline funciona;
- el pipeline en vivo funciona;
- Blocks fue validado como entorno controlado;
- AirSimNH fue validado como entorno experimental principal;
- se generaron imagenes crudas, anotadas, JSON y CSV;
- se registro repetibilidad con seis corridas positivas.

## Limites y siguiente fase

La fase valida percepcion visual, no control autonomo. El uso de `sim_pose` fue una herramienta de posicionamiento de escena para evaluar la camara y el detector. La generacion de comandos de control para corregir la posicion del UAV y aterrizar sobre la plataforma debe abordarse en una fase posterior.

Siguiente paso metodologico:

- integrar la salida del detector con una logica de control visual;
- registrar correcciones laterales;
- comparar posteriormente `T0` contra `T1`;
- mantener separada la evidencia de percepcion de la evidencia de control autonomo.
