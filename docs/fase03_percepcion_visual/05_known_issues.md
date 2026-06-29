# Incidencias y Riesgos - Fase 03

## KI-0301: Marcador no visible en capturas disponibles

**Estado:** pendiente.

Las imagenes disponibles en `data/raw/` incluyen capturas heredadas de Fase 02 y una captura en vivo de Fase 03. Todas muestran terreno/vegetacion desde la camara inferior, pero no una plataforma o marcador de aterrizaje claramente visible.

Evidencia asociada:

- `data/logs/phase03_20260501_112825_938adc92_perception_validation.csv`;
- `data/raw/phase03_20260501_113742_ddf1edb6_bottom_center.png`;
- `outputs/figures/phase03_perception/phase03_20260501_113742_ddf1edb6_bottom_center_detection.json`.
- `data/raw/phase03_20260501_123327_dbd36c7a_bottom_center.png`;
- `outputs/figures/phase03_perception/phase03_20260501_123327_dbd36c7a_bottom_center_detection.json`;
- `data/logs/phase03_20260501_123407_089860ee_perception_validation.csv`.

Resultado observado:

```text
detected=false
confidence=0.0
```

Interpretacion: el resultado negativo es coherente con la escena capturada y no indica, por si solo, un fallo del detector.

Nota de avance: la segunda captura en vivo muestra una superficie clara uniforme. Esto mejora la limpieza visual respecto al terreno, pero aun no incorpora un marcador contrastante detectable.

Medidas:

- preparar marcador contrastante en el escenario;
- capturar nuevas imagenes desde `bottom_center`;
- actualizar `04_resultados_validacion.md` con evidencia.

## KI-0305: Pipeline en vivo conectado, validacion positiva pendiente en AirSimNH

**Estado:** parcialmente controlado.

`src/perception/perception_pipeline.py` ya logro conectarse a AirSim, capturar imagen, ejecutar deteccion y guardar JSON/imagen anotada. La primera validacion positiva se obtuvo en Blocks con el marcador generado por `src/perception/spawn_landing_marker.py`.

Evidencia positiva:

```text
outputs/figures/phase03_perception/blocks/p03_blocks_marker/phase03_20260501_130751_128cd5d5_bottom_center_detection.json
```

Resultado:

```text
detected=true
confidence=1.0
error_x_px=-4.291
error_y_px=8.539
```

Pendiente: repetir la validacion positiva en AirSimNH, que es el entorno experimental principal de la metodologia.

Medidas:

- usar el mismo marcador o equivalente en AirSimNH;
- ubicar el UAV por encima del marcador;
- ejecutar `python src\perception\perception_pipeline.py --environment AirSimNH --scenario-id P03_AIRSIMNH_MARKER --altitude-m 3`;
- repetir `python src\perception\validate_perception.py` sobre la carpeta de AirSimNH.

## KI-0302: Dependencia de umbrales HSV

**Estado:** controlado inicialmente.

El detector inicial depende de rangos HSV configurables. Si el color del marcador o la iluminacion cambian, puede requerir calibracion.

Durante la prueba en Blocks se observo que el marcador se veia rojo en la ventana externa, pero azul/cian en la imagen capturada por `bottom_center`. Se amplio `configs/perception_config.json` para incluir rangos rojo/naranja y azul/cian.

Medidas:

- ajustar `configs/perception_config.json`;
- registrar los parametros usados en cada corrida;
- conservar imagenes anotadas para auditoria visual.

## KI-0303: Falsos positivos por objetos del mismo color

**Estado:** observado y controlado inicialmente.

Objetos o texturas con color parecido al marcador pueden producir detecciones falsas.

Durante la prueba en AirSimNH `phase03_20260501_132849_2737d038`, el detector marco `detected=True` con `confidence=0.046`, pero la imagen anotada mostro que la caja correspondia a una hoja/mancha azul en la via, no a la plataforma. Por tanto, esa corrida no debe aceptarse como validacion positiva.

Durante el barrido con `pose-x/pose-y`, tambien aparecieron detecciones sobre sombra/hojas (`phase03_20260501_134258_e6023aeb` y `phase03_20260501_134319_4fbc28a0`). El usuario confirmo que visualmente no observa marcador rojo en AirSimNH durante esta etapa.

Medidas:

- usar marcador de alto contraste;
- filtrar por area minima y maxima;
- exigir confianza minima;
- evaluar restricciones de forma;
- considerar ArUco si el entorno visual resulta ambiguo.

Medida aplicada:

- `configs/perception_config.json` aumento `min_area_px` a `1000`;
- se agrego `min_confidence=0.05`;
- `src/perception/landing_marker_detector.py` rechaza contornos por debajo de la confianza minima.
- se agregaron overrides por entorno: AirSimNH acepta rangos rojo y azul/cian, pero usa area minima y confianza mas estrictas para no aceptar hojas pequenas.

## KI-0306: Marcador no visible en AirSimNH

**Estado:** controlado parcialmente.

Aunque el marcador fue generado correctamente en Blocks, en AirSimNH no se confirma visualmente la presencia de una plataforma roja durante las ultimas pruebas. La API tambien devuelve `nan` al consultar `simGetObjectPose` para `phase03_landing_marker_under_uav`, por lo que no hay una pose confiable del marcador desde AirSim.

Actualizacion: se recreo el marcador como `phase03_landing_marker_airsimnh`, se confirmo visualmente su presencia y se obtuvo deteccion positiva con `phase03_20260501_135239_e8ae6aed`.

Medidas:

- recrear el marcador en AirSimNH y confirmar visualmente que permanece en escena;
- evitar aceptar detecciones sobre hojas/sombras como validacion positiva;
- repetir `perception_pipeline.py` solo cuando el marcador rojo sea visible;
- si la API no permite controlar el objeto de forma confiable, considerar colocar manualmente un marcador estable en el escenario o usar un entorno AirSimNH modificado.

Pendiente:

- mantener esta distincion en fases posteriores: la deteccion visual esta validada, pero el control autonomo PX4 queda pendiente para una fase posterior.

## KI-0304: Percepcion sin control de aterrizaje

**Estado:** por diseno.

Fase 03 estima posicion relativa en imagen, pero no genera comandos de control autonomo. La integracion con control debe abordarse en una fase posterior.
