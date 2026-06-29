# Incidencias y Riesgos - Fase 05

## KI-0501: T0 puede parecer peor solo por condiciones iniciales distintas

Medida: ejecutar T0 y T1 con el mismo `scenario_id`, mismo offset, misma altura
y mismo `treatment_pair_id`.

## KI-0502: T0 no debe usar vision para corregir

Medida: revisar que `command_forward_m_s=0.0` y `command_right_m_s=0.0` durante
las filas `baseline_descent`.

## KI-0503: Error final depende de pose AirSim del marcador

Medida: pasar siempre `--marker-object-name` al script de tratamiento. Si el
marcador no se encuentra, la corrida puede conservarse pero requiere incidencia.

## KI-0504: Orientacion inicial aun no validada

Estado: mitigado operativamente mediante yaw absoluto; pendiente de confirmar
en una prueba diagnostica T1 antes de reanudar corridas formales.

Medida: el piloto minimo y el primer escenario formal usan `yaw_deg=0.0`. No
activar escenarios con yaw 15 grados hasta validar una forma reproducible de
inicializacion.

Observacion del 2026-05-05:

- La prueba con `run_phase05_yaw_setup.py --relative-yaw-deg 15.0` no alcanzo
  tolerancia.
- El objetivo reportado fue aprox. `22.02 deg`, pero la actitud se mantuvo en
  aprox. `7.02 deg`; el error quedo cerca de `15 deg`, por encima de la
  tolerancia `3 deg`.
- No se debe ejecutar `P05_S02_H2_Y04_YAW15` hasta corregir o reemplazar el
  procedimiento de yaw.

Actualizacion previa:

- Se reemplazo el metodo por defecto del helper por `offboard-yaw-rate`, usando
  setpoints directos MAVLink en modo `OFFBOARD`.
- En ese momento, antes de iniciar S02, se valido con:
  `run_phase05_yaw_setup.py --method offboard-yaw-rate --relative-yaw-deg 15.0`.
- En la validacion manual del 2026-05-05, el metodo `offboard-yaw-rate` alcanzo
  tolerancia: objetivo aprox. `22.54 deg`, yaw final aprox. `19.62 deg`, error
  aprox. `2.92 deg` con tolerancia `3.0 deg`.
- La revision posterior mostro que esta validacion controlaba un cambio relativo
  de orientacion, pero no garantizaba una orientacion inicial absoluta.

Actualizacion del 2026-05-06:

- Al revisar los logs de `P05_S02_H2_Y04_YAW15`, se encontro que
  `planned_yaw_deg=15.0` no implicaba una orientacion absoluta de `15 deg`.
- El helper estaba aplicando `+15 deg` relativo al yaw residual despues de cada
  aterrizaje. Como consecuencia, los precheck T1 de S02 registraron yaw real
  aproximado de `85.45 deg`, `85.96 deg`, `-166.74 deg`, `-90.07 deg`,
  `164.27 deg`, `-118.14 deg`, `115.45 deg` y `85.63 deg` en distintas
  corridas/diagnosticos.
- Esta variabilidad afecta el control del factor "orientacion inicial" y obliga
  a pausar la secuencia formal antes de continuar con escenarios `YAW15`.

Medida:

- Se actualizo `run_phase05_yaw_setup.py` para aceptar `--absolute-yaw-deg`.
- Se actualizo `phase05_generate_run_plan.py` para generar yaw absoluto para
  todos los escenarios, incluidos `YAW0`.
- Se registra la enmienda `P05-A02`: cambio de inicializacion de yaw relativa a
  inicializacion absoluta.
- Antes de continuar la ejecucion formal, validar en simulador que
  `--absolute-yaw-deg 15.0` alcanza tolerancia y que el precheck posterior
  registra yaw real cercano al objetivo.

Validacion manual del 2026-05-06:

- El comando `run_phase05_yaw_setup.py --absolute-yaw-deg 15.0` fue aceptado
  con yaw final aprox. `12.04 deg`, objetivo `15.00 deg` y error `2.96 deg`,
  dentro de la tolerancia `3.0 deg`.
- La validacion de yaw absoluto queda aceptada para continuar con diagnostico
  T1 no formal.
- La telemetria posterior al aterrizaje mostro `mode=HOLD`, baja altitud y
  `armed=True`; antes de cualquier nueva prueba se debe ejecutar desarme y
  confirmar `armed=False` segun `KI-0505`.

## KI-0505: Estado residual de PX4

Medida: ejecutar telemetria previa y, si es necesario,
`run_mavlink_mode_recovery.py`.

Actualizacion del 2026-05-05:

- Tras la validacion de yaw y aterrizaje previo a S02, PX4 quedo en `HOLD`,
  sobre el suelo, pero aun con `armed=True`.
- Se agrego `src/control/run_px4_disarm.py` para forzar un cierre seguro entre
  escenarios cuando la telemetria indique baja altitud y `armed=True`.
- No iniciar un bloque nuevo si la telemetria posterior no confirma
  `armed=False`.

## KI-0506: Marcador 3D puede interferir si se genera antes del despegue

Medida: despegar primero, luego generar el marcador bajo el vehiculo, ejecutar
el tratamiento y limpiar el marcador al final.

## KI-0507: El umbral de 0.80 m no es error final fisico

Medida: documentarlo como umbral piloto de transicion a `LAND`; el error final
se calcula con la pose registrada respecto al marcador.

## KI-0508: Duracion insuficiente para T1 con offset lateral

Estado: observado y mitigado en piloto del 2026-05-05.

En la corrida `phase05_20260505_133149_3b8adca2`, T1 con offset lateral positivo
corrigio el error visual de forma clara: el error lateral normalizado bajo de
aprox. `0.3750` a `0.0079`, no hubo detecciones perdidas y no se produjo abort.
Sin embargo, el lazo visual termino por duracion a una altitud aprox. de
`0.971 m`, por encima del umbral piloto `0.80 m`. Por ello
`landing_threshold_reached=False` y la corrida no debe aceptarse como aterrizaje
formal, aunque el cierre final con `LAND` fue seguro y el error final fue bajo.

Medida:

- repetir la corrida T1 con offset positivo usando `--duration 40`;
- conservar el resto de parametros congelados;
- aceptar la repeticion solo si `landing_threshold_reached=True`,
  `aborted=False` y el cierre queda en `LOITER`, `armed=False`;
- no iniciar el bloque formal de 160 corridas hasta cerrar esta repeticion.

Resolucion:

- La repeticion `phase05_20260505_154421_71272606` uso `--duration 40` y
  alcanzo `landing_threshold_reached=True` a una altitud aprox. de `0.7909 m`.
- Registro 139 muestras visuales, 138 detecciones aceptadas, reduccion del
  error lateral normalizado de aprox. `0.4402` a `0.0286`,
  `landing_success=True`, `aborted=False` y cierre en `LOITER`, `armed=False`.
- Para el piloto aceptado, esta repeticion supersede a
  `phase05_20260505_133149_3b8adca2`.

## KI-0509: Duplicacion de corrida tras repeticion correctiva

Estado: riesgo metodologico mitigado por regla de curacion.

El resumen `phase05_run_summary.csv` contiene tanto la corrida T1 parcial
`phase05_20260505_133149_3b8adca2` como la repeticion aceptada
`phase05_20260505_154421_71272606`, ambas con el mismo escenario,
`treatment_pair_id` y repeticion. Si se usan ambas en analisis comparativo, se
duplicaria artificialmente el tratamiento T1 para el escenario con offset.

Medida:

- conservar ambas corridas como evidencia;
- excluir la corrida parcial de cualquier tabla comparativa formal;
- antes del bloque completo, definir una regla de curacion de datos para marcar
  corridas como `accepted`, `excluded` o `superseded`.

Resolucion:

- La regla quedo declarada en `configs/phase05_experiment_config.json`, seccion
  `curation`.
- El script `src/analysis/phase05_metrics.py` genera `curation_status`,
  `curation_reason` y `superseded_by`.
- La corrida `phase05_20260505_133149_3b8adca2` queda marcada como
  `superseded` por `phase05_20260505_154421_71272606`.

## KI-0510: Perdida transitoria de marcador en T1 con yaw 15 grados

Estado: resuelto operativamente mediante la enmienda `P05-A01`.

En la corrida `phase05_20260505_212727_5fc9e757`, T1 corrigio el error lateral
y cerro con error final bajo (`0.0146 m`), tasa de deteccion aceptada `96.6 %`,
evento terminal `land_complete`, modo final `LOITER` y `armed=False`. No
obstante, la corrida quedo `excluded` porque el lazo visual acumulo `4`
perdidas consecutivas del marcador, superando el limite `3`, a una altitud
visual aprox. de `0.849 m`. Por ello `aborted=True` y
`landing_threshold_reached=False`.

Medida:

- no contar esta corrida como evidencia comparativa formal;
- repetir `Run 22` con los parametros congelados antes de continuar el bloque
  S02;
- mantener el umbral de aterrizaje visual `0.80 m` y el limite de perdidas
  `3` mientras no exista evidencia repetida de falla sistematica;
- si la repeticion vuelve a fallar por el mismo motivo, detener S02 y revisar
  robustez de deteccion ArUco bajo `yaw_deg=15.0` antes de cambiar la
  configuracion experimental.

Actualizacion:

- La repeticion `phase05_20260505_213632_1aeebbe7` volvio a quedar `excluded`
  por `marker_missing_or_controller_abort`.
- El patron fue consistente: error final bajo (`0.0086 m`), tasa de deteccion
  aceptada `96.4 %`, cierre `LOITER`, `armed=False`, pero aborto por `4`
  perdidas consecutivas con limite `3`.
- La altitud visual minima del segundo intento fue aprox. `0.815 m`, apenas por
  encima del umbral `0.80 m`.
- S02 queda pausado antes de `Run 23`; cualquier cambio de tolerancia debe
  probarse primero como diagnostico no formal y luego documentarse como cambio
  metodologico si se adopta para el protocolo.
- La curacion formal excluye automaticamente escenarios cuyo `scenario_id`
  termina en `_DIAG`, de modo que las pruebas diagnosticas no entren como
  corridas aceptadas del diseno formal.

Resolucion diagnostica:

- La prueba no formal `phase05_20260505_215332_c32234b5`, con
  `scenario_id=P05_S02_H2_Y04_YAW15_DIAG`, uso `max_missing_detections=6`.
- El resultado fue tecnicamente exitoso: `landing_success=True`,
  `landing_threshold_reached=True`, `aborted=False`, `lost_detection_count=1`,
  tasa de deteccion aceptada `99.1 %`, altitud visual final aprox. `0.7977 m`,
  error final `0.0073 m`, cierre `LOITER`, `armed=False`.
- La curacion la marco correctamente como `excluded` por sufijo `_DIAG`.
- Se adopta la enmienda metodologica `P05-A01`: actualizar T1 de
  `max_missing_detections=3` a `max_missing_detections=6` antes de repetir
  `Run 22` como corrida formal.

Resolucion formal:

- La repeticion formal `phase05_20260506_220836_6d1110a0`, ejecutada con
  `max_missing_detections=6`, quedo `accepted`.
- Resultado: `landing_success=True`, `landing_threshold_reached=True`,
  `aborted=False`, `lost_detection_count=2`, tasa de deteccion aceptada
  `98.2 %`, altitud visual final aprox. `0.7891 m`, error final `0.0213 m`,
  cierre `LOITER`, `armed=False`.
- El par `P05_S02_H2_Y04_YAW15_R01` queda completo para comparacion formal:
  T0 `phase05_20260505_212244_60e653af` y T1
  `phase05_20260506_220836_6d1110a0`.

### Alcance metodologico de P05-A01

La enmienda `P05-A01` se aplica desde `P05_S02_H2_Y04_YAW15` en adelante. Las
corridas ya aceptadas de `P05_S01_H2_Y04_YAW0` se mantienen dentro del analisis
formal porque no fueron afectadas por abortos asociados a perdida consecutiva
del marcador. El cambio no modifica la ley de control visual, la velocidad
maxima horizontal, la tasa de descenso ni el umbral visual de aterrizaje; solo
amplia la tolerancia ante perdidas transitorias consecutivas del marcador cerca
del umbral. Esta modificacion debera declararse en el analisis final como una
enmienda controlada del protocolo.

## KI-0511: Marcador fiduciario residual entre corridas

Estado: mitigado mediante limpieza preventiva y repeticion formal.

Durante la ejecucion de `Run 27` se observaron visualmente dos marcadores
fiduciarios en escena. Esto sugiere que el marcador de una corrida previa no fue
eliminado correctamente antes de generar el nuevo marcador. Aunque el log de
`Run 27` ya queda excluido por aborto (`marker_missing_or_controller_abort`),
la presencia de dos marcadores rompe la condicion experimental controlada de un
unico blanco por corrida.

Evidencia asociada:

- `Run 26` / `phase05_20260506_222740_a752e2bd` quedo `excluded` por aborto,
  con `landing_threshold_reached=False`, `last_visual_altitude_m=0.9351 m`,
  `lost_detection_count=7` y `max_missing_detections=6`.
- `Run 27` / `phase05_20260506_222948_9cf2352f` quedo `excluded` por aborto
  temprano, con solo `3` detecciones aceptadas, `lost_detection_count=10`,
  `landing_threshold_reached=False`, `last_visual_altitude_m=2.0447 m` y
  `descent_command_count=0`.

Medida:

- repetir los T1 afectados (`Run 26` y `Run 27`) despues de una limpieza
  explicita de marcadores;
- conservar los T0 ya aceptados de R03 y R04, salvo que aparezca evidencia de
  contaminacion en esas corridas;
- actualizar el generador formal para ejecutar
  `clear_landing_markers.py --object-regex ".*phase05.*"` tambien al inicio de
  cada bloque de corrida, antes del despegue;
- si la limpieza inicial reporta objetos residuales, confirmar que el conteo
  queda en cero antes de despegar.

Resolucion:

- La repeticion R03 `phase05_20260506_223941_15b8da6a` quedo `accepted`, con
  `landing_success=True`, `landing_threshold_reached=True`, `aborted=False`,
  `lost_detection_count=0`, tasa de deteccion aceptada `100.0 %`, altitud
  visual final `0.7991 m`, error final `0.0209 m`, cierre `LOITER`,
  `armed=False`.
- La repeticion R04 `phase05_20260506_224144_bda896e4` quedo `accepted`, con
  `landing_success=True`, `landing_threshold_reached=True`, `aborted=False`,
  `lost_detection_count=1`, tasa de deteccion aceptada `99.1 %`, altitud visual
  final `0.7821 m`, error final `0.0151 m`, cierre `LOITER`, `armed=False`.
- Los pares R03 y R04 de `P05_S02_H2_Y04_YAW15` quedan completos usando las
  repeticiones aceptadas. Las corridas excluidas se conservan como evidencia de
  incidencia y no entran a las tablas comparativas formales.

## KI-0512: Perdida terminal recurrente del marcador en S02 T1

Estado: mitigado mediante enmienda `P05-A03`; requiere reanudar S02 con pares
comparables bajo la configuracion actualizada.

Durante el bloque `Run 29` a `Run 34` de
`P05_S02_H2_Y04_YAW15`, los tres T0 de R05-R07 quedaron aceptados, pero los tres
T1 asociados quedaron `excluded` por `marker_missing_or_controller_abort`. A
diferencia de `KI-0511`, no hay evidencia de marcador residual; el patron es
terminal y recurrente bajo `yaw_deg=15.0`.

Evidencia asociada:

- `Run 30` / `phase05_20260506_225359_b159c30b`: T1 R05, `excluded`,
  `missing_detections=7`, `max_missing_detections=6`, altitud visual minima
  `0.8638 m`, error final `0.0421 m`, cierre `LOITER`, `armed=False`.
- `Run 31` / `phase05_20260506_225630_93cc83e3`: T1 R06, `excluded`,
  `missing_detections=7`, `max_missing_detections=6`, altitud visual minima
  `0.9136 m`, error final `0.0414 m`, cierre `LOITER`, `armed=False`.
- `Run 34` / `phase05_20260506_230225_10e6ea83`: T1 R07, `excluded`,
  `missing_detections=7`, `max_missing_detections=6`, altitud visual minima
  `0.8429 m`, error final `0.0295 m`, cierre `LOITER`, `armed=False`.

Observacion tecnica:

- En las tres corridas T1 se redujo el error lateral antes del aborto
  (`reduced_abs_error_x=True`).
- La perdida ocurre despues de iniciar el descenso visual, cerca del umbral
  formal `0.80 m`.
- Al perder el marcador, el controlador entra en modo hover y deja de enviar
  descenso visual; si supera el limite de perdidas consecutivas, marca aborto y
  solicita `LAND`.

Medida inicial:

- No continuar con `Run 35` hasta ejecutar una prueba diagnostica no formal.
- No convertir los T1 excluidos en aceptados por curacion manual.
- Conservar los T0 aceptados de R05-R07 como evidencia formal valida, pero
  mantener incompletos los pares hasta repetir sus T1 bajo un criterio
  metodologico definido.
- Ejecutar una prueba `_DIAG` con mayor tolerancia terminal y umbral de entrega
  visual mas alto para determinar si el problema es el umbral `0.80 m`, la
  tolerancia de perdidas o la visibilidad del marcador cerca del suelo.

Decision posterior previa:

- no continuar con `Run 35` hasta validar primero la enmienda de yaw absoluto
  `P05-A02`;
- repetir un diagnostico T1 de S02 con yaw absoluto antes de decidir si se
  adopta una enmienda posterior para el umbral terminal;
- no convertir los T1 excluidos en aceptados por curacion manual.

Diagnostico del 2026-05-06:

- La prueba no formal `phase05_20260506_231219_1598cbf1`, con
  `scenario_id=P05_S02_H2_Y04_YAW15_DIAG`, uso
  `landing_complete_altitude=0.90` y `max_missing_detections=10`.
- Resultado tecnico: `landing_success=True`, `landing_threshold_reached=True`,
  `aborted=False`, `accepted_detection_rate=100.0 %`,
  `lost_detection_count=0`, altitud visual final `0.8988 m`, error final
  `0.0110 m`, cierre `LOITER`, `armed=False`.
- La curacion la marco correctamente como `excluded` por sufijo `_DIAG`.
- El resultado sugiere que una entrega visual mas alta puede evitar la perdida
  terminal del marcador, pero no se adopta todavia como enmienda formal porque
  durante la misma revision se detecto variabilidad de yaw real en S02
  (`KI-0504`). Primero debe validarse yaw absoluto; luego se decide si hace
  falta una enmienda terminal adicional.

Diagnostico con yaw absoluto del 2026-05-06:

- La prueba no formal `phase05_20260506_233844_cc63ed08`, con
  `scenario_id=P05_S02_H2_Y04_YAW15_ABSYAW_DIAG`, uso yaw absoluto `15.0 deg`,
  `landing_complete_altitude=0.90` y `max_missing_detections=10`.
- La corrida quedo correctamente `excluded` por sufijo `_DIAG`.
- Resultado tecnico: `landing_success=False`, `landing_threshold_reached=False`,
  `aborted=True`, `missing_detections=11`, `max_missing_detections=10`,
  `accepted_detection_rate=89.6 %`, altitud visual final `0.9453 m`, error
  final `0.0226 m`, cierre `LOITER`, `armed=False`.
- La ley visual redujo el error lateral (`final_error_m=0.0226 m`), pero la
  perdida terminal del marcador ocurrio antes de alcanzar el umbral visual
  `0.90 m`.

Decision antes del segundo diagnostico:

- no continuar con `Run 35` todavia;
- no adoptar aun una enmienda formal sobre `landing_complete_altitude`;
- ejecutar una segunda prueba diagnostica no formal con yaw absoluto y umbral
  visual mas alto (`landing_complete_altitude=1.05`) para verificar si la
  entrega a `LAND` antes de la perdida terminal estabiliza S02 T1.

Diagnostico con yaw absoluto y umbral `1.05 m` del 2026-05-08:

- La prueba no formal `phase05_20260508_230559_a6773794`, con
  `scenario_id=P05_S02_H2_Y04_YAW15_ABSYAW_H105_DIAG`, uso yaw absoluto
  `15.0 deg`, `landing_complete_altitude=1.05` y
  `max_missing_detections=10`.
- La corrida quedo correctamente `excluded` por sufijo `_DIAG`.
- Resultado tecnico: `landing_success=True`, `landing_threshold_reached=True`,
  `aborted=False`, `accepted_detection_rate=100.0 %`,
  `lost_detection_count=0`, altitud visual final `1.0408 m`, error final
  `0.0218 m`, latencia media `80.68 ms`, latencia maxima `148.81 ms`, cierre
  `LOITER`, `armed=False`.
- La prueba confirma que entregar a `LAND` antes de la zona de perdida terminal
  evita el aborto sin degradar materialmente la correccion lateral.

Resolucion metodologica:

- se adopta la enmienda `P05-A03`;
- `frozen_t1.landing_complete_altitude_m` cambia de `0.80` a `1.05`;
- aunque el campo historico esta bajo `frozen_t1`, el generador formal aplica
  este umbral terminal tanto a T0 como a T1 para preservar comparabilidad por
  par;
- las corridas diagnosticas se mantienen excluidas de las metricas formales;
- los T1 formales excluidos de R05-R07 no se rescatan por curacion manual;
- si se corrigen R05-R07 bajo `P05-A03`, repetir los pares completos o declarar
  explicitamente cualquier emparejamiento cruzado entre T0 pre-enmienda y T1
  post-enmienda;
- toda comparacion final debe declarar que S01 y las primeras repeticiones de
  S02 se ejecutaron antes de `P05-A03`.

Ejecucion correctiva del 2026-05-08:

- Se repitieron pares completos R05-R07 bajo `P05-A03`.
- Las corridas antiguas R05-R07 quedaron declaradas como `superseded` en
  `curation.superseded_runs`.
- Las seis corridas correctivas quedaron `accepted`.
- Estado posterior de S02: T0 `7/10`, T1 `7/10`, con pares completos R01-R07.
- En las tres T1 correctivas no hubo abortos ni perdidas de marcador
  (`lost_detection_count=0`) y la deteccion aceptada fue `100.0 %`.

Con esta evidencia, la incidencia de perdida terminal recurrente queda mitigada
para continuar R08-R10 bajo la misma configuracion `P05-A03`.

Resolucion final S02:

- R08-R10 se ejecutaron bajo `P05-A03` y quedaron aceptadas.
- `P05_S02_H2_Y04_YAW15` queda completo con T0 `10/10` y T1 `10/10`.
- En las seis T1 ejecutadas bajo `P05-A03` no hubo abortos ni perdidas de
  marcador (`lost_detection_count=0`).
- La incidencia queda cerrada para S02; mantener observacion en escenarios con
  mayor desplazamiento lateral (`offset_y=0.8 m`) o mayor altura inicial.

## KI-0513: Desarme denegado despues de validacion de yaw absoluto

Estado: mitigado mediante reinicio limpio del entorno.

Durante la validacion operativa de yaw absoluto se ejecuto un aterrizaje PX4
manual posterior al ajuste de orientacion. La telemetria quedo en `HOLD` con
baja altitud, pero `armed=True`. Al intentar desarmar, PX4 respondio
`COMMAND_DENIED` y AirSimNH mostro `Disarming denied: not landed`; luego el
entorno AirSimNH se cerro.

Evidencia asociada:

- `run_px4_disarm.py --confirm-send` no logro `armed=False` dentro de `10 s`.
- AirSimNH reporto visualmente `Disarming denied: not landed`.
- Tras reiniciar AirSimNH/PX4, la telemetria
  `phase04_20260506_233451_19ee46f6_px4_telemetry.csv` confirmo
  `mode=HOLD`, `armed=False`, `alt=0.0`.

Medida:

- si `run_px4_disarm.py` devuelve `COMMAND_DENIED` en baja altitud y AirSimNH
  reporta que el vehiculo no esta aterrizado, no repetir indefinidamente el
  desarme;
- pausar la secuencia formal, reiniciar AirSimNH/PX4 y confirmar telemetria
  `armed=False`, `alt=0.0` antes de cualquier despegue nuevo;
- registrar la corrida o validacion afectada como incidencia operativa, no como
  evidencia formal aceptada.

## KI-0514: Cierre de AirSimNH durante corrida formal

Estado: mitigado mediante reinicio del entorno y repeticion del run afectado.

Durante el primer intento de `Run 38`
(`P05_S02_H2_Y04_YAW15`, T1, R09), AirSimNH se cerro. Se reinicio el entorno y
se repitio el bloque operativo. El intento interrumpido no genero una fila
formal en `phase05_run_summary.csv`; por tanto, no se incorporo a la curacion
como `accepted`, `excluded` ni `superseded`.

Evidencia S02 aceptada:

- La repeticion valida de `Run 38` quedo registrada como
  `phase05_20260508_235107_065ebbfe`.
- Resultado: `accepted`, `landing_success=True`,
  `landing_threshold_reached=True`, `aborted=False`,
  `accepted_detection_rate=100.0 %`, `lost_detection_count=0`, error final
  `0.0218 m`, cierre `LOITER`, `armed=False`.

Medida:

- Si AirSimNH se cierra durante una corrida, reiniciar AirSimNH/PX4 y confirmar
  telemetria segura antes de repetir.
- Si el intento fallido genera log parcial, declararlo `excluded` o
  `superseded` segun corresponda.
- Si no genera log formal, registrar la incidencia documentalmente y conservar
  solo la repeticion valida en el resumen curado.

Actualizacion S03:

- Durante el primer intento de `Run 47`
  (`P05_S03_H2_Y08_YAW0`, T1, R04), AirSimNH se cerro y el log quedo sin
  `land_complete`.
- El intento `phase05_20260509_001502_30366ed5` queda declarado como
  `superseded` por `phase05_20260509_001816_20a45b99`.
- La repeticion valida quedo `accepted`, con `landing_success=True`,
  `landing_threshold_reached=True`, `aborted=False`,
  `accepted_detection_rate=100.0 %`, `lost_detection_count=0`, error final
  `0.0221 m`, cierre `LOITER`, `armed=False`.

Actualizacion S04:

- Durante la repeticion correctiva de `Run 67`
  (`P05_S04_H2_Y08_YAW15`, T1, R04), AirSimNH se cerro intempestivamente dos
  veces.
- Esos cierres no generaron filas formales adicionales en
  `phase05_run_summary.csv`.
- Tras reiniciar el entorno y repetir el mismo run, la corrida valida quedo
  aceptada como `phase05_20260509_214330_4ae8d025`.

## KI-0515: Aborto temprano T1 en S03 R03

Estado: cerrado por repeticion correctiva aceptada.

En `P05_S03_H2_Y08_YAW0`, el primer intento T1 de R03 aborto de forma temprana
por perdida de marcador.

Evidencia:

- `Run 46` / `phase05_20260509_001242_70bda245`.
- `curation_status=superseded` por
  `phase05_20260509_003307_468906cb`.
- `abort_reason=marker_missing_or_controller_abort`.
- `accepted_detection_rate=0.0 %`.
- `lost_detection_count=7`.
- `landing_threshold_reached=False`.
- error final registrado `0.7680 m`.
- cierre seguro `LOITER`, `armed=False`.

Repeticion correctiva:

- `Run 46R` / `phase05_20260509_003307_468906cb`.
- `curation_status=accepted`.
- `landing_success=True`.
- `landing_threshold_reached=True`.
- `aborted=False`.
- `accepted_detection_rate=100.0 %`.
- `lost_detection_count=0`.
- error final `0.0091 m`.
- cierre `LOITER`, `armed=False`.

Interpretacion:

- El evento ocurre en el primer bloque del escenario con `offset_y=0.8 m`.
- Como T1 fue aceptado en R01, R02, R03 corregido y R04 del mismo escenario,
  no se adopta una nueva enmienda metodologica.
- S03 queda pareado formalmente hasta R04.

Medida:

- Mantener `phase05_20260509_001242_70bda245` como `superseded` y usar
  `phase05_20260509_003307_468906cb` como fuente valida de T1 R03.
- S03 quedo cerrado con R01-R10 aceptados; continuar con S04 desde `Run 61`
  bajo la misma configuracion `P05-A03`.
- Si reaparece perdida temprana del marcador en S03, pausar y evaluar un
  diagnostico no formal especifico para `offset_y=0.8 m`.

## KI-0516: Aborto temprano T1 en S04 R04

Estado: cerrado por repeticion correctiva aceptada.

En `P05_S04_H2_Y08_YAW15`, el primer intento T1 de R04 aborto al inicio del
lazo visual sin detecciones aceptadas. A diferencia de S03, este escenario
combina `offset_y=0.8 m` con yaw absoluto `15 deg`, por lo que se conserva como
incidencia especifica de S04 hasta contar con la repeticion.

Evidencia:

- `Run 67` / `phase05_20260509_212824_d3037b9b`.
- `curation_status=superseded` por
  `phase05_20260509_214330_4ae8d025`.
- `abort_reason=marker_missing_or_controller_abort`.
- `accepted_detection_rate=0.0 %`.
- `lost_detection_count=7`.
- `landing_threshold_reached=False`.
- error final registrado `0.8253 m`.
- cierre seguro `LOITER`, `armed=False`.

Repeticion correctiva:

- `Run 67R` / `phase05_20260509_214330_4ae8d025`.
- `curation_status=accepted`.
- `landing_success=True`.
- `landing_threshold_reached=True`.
- `aborted=False`.
- `accepted_detection_rate=100.0 %`.
- `lost_detection_count=0`.
- error final `0.0349 m`.
- cierre `LOITER`, `armed=False`.

Interpretacion:

- Los T1 de R01, R02 y R03 del mismo escenario quedaron aceptados con
  `accepted_detection_rate=100.0 %` y `lost_detection_count=0`.
- El T0 R04 quedo aceptado y la repeticion T1 correctiva completo el par R04.
- No se adopta una nueva enmienda metodologica con un unico aborto aislado.

Medida:

- Mantener `phase05_20260509_212824_d3037b9b` como `superseded` y usar
  `phase05_20260509_214330_4ae8d025` como fuente valida de T1 R04.
- Continuar S04 con `Run 69` a `Run 76` bajo la misma configuracion `P05-A03`.
- Si vuelve a abortar por perdida temprana del marcador, pausar S04 y evaluar
  diagnostico no formal especifico para `offset_y=0.8 m` y `yaw=15 deg`.
