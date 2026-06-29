# Regla de Curacion de Datos

## Objetivo

Evitar que el analisis formal T0/T1 incluya corridas incompletas, duplicadas o
repetidas por correccion operativa. Los logs crudos no se borran; la curacion
solo define que filas son validas para comparacion.

## Estados

- `accepted`: corrida valida para tablas, graficos y analisis estadistico.
- `excluded`: corrida conservada como incidencia, pero fuera de metricas
  comparativas.
- `superseded`: corrida reemplazada por una repeticion correctiva aceptada.

## Fuente de verdad

La regla queda declarada en `configs/phase05_experiment_config.json`, seccion
`curation`, y se aplica al regenerar:

```powershell
python src\analysis\phase05_metrics.py
```

El archivo resultante es:

```text
data/logs/phase05_experiments/summary/phase05_run_summary.csv
```

## Reglas de aceptacion automatica

Una corrida pasa a `accepted` si cumple:

- `phase=fase05`;
- `treatment` en `T0` o `T1`;
- metadatos completos: `scenario_id`, `experiment_id`,
  `treatment_pair_id`, `repetition`;
- evento terminal `land_complete`;
- cierre con vehiculo desarmado;
- sin aborto;
- `landing_success=True`;
- en `T1`, `landing_threshold_reached=True`;
- en `T0`, comandos horizontales dentro de tolerancia
  `max_t0_horizontal_command_m_s=0.001`.

## Supersesion

Cuando una corrida se repite para corregir una condicion metodologica, la
corrida anterior debe declararse en `curation.superseded_runs` con:

- `run_id`;
- `superseded_by`;
- `reason`.

Caso piloto ya registrado:

- `phase05_20260505_133149_3b8adca2` queda `superseded`;
- `phase05_20260505_154421_71272606` queda como repeticion T1 aceptada.

## Duplicados no resueltos

Si existen dos corridas `accepted` con la misma clave:

```text
experiment_id + scenario_id + treatment + treatment_pair_id + repetition
```

ambas se marcan como `excluded` hasta que una se declare `superseded`. Esta
regla evita duplicar artificialmente un tratamiento dentro del mismo par
experimental.

Caso registrado en S07 R08 T0: `Run 136` genero tres CSV completos para la
misma clave formal. Se conserva como corrida aceptada el ultimo intento
completo, `phase05_20260608_122434_ac873b0b`; los intentos
`phase05_20260608_121619_f18597c3` y
`phase05_20260608_121826_222fe0bc` quedan declarados como `superseded` en
`curation.superseded_runs`.

## Enmiendas metodológicas

La enmienda `P05-A01` actualiza el parámetro
`frozen_t1.max_missing_detections` de `3` a `6` a partir del escenario
`P05_S02_H2_Y04_YAW15`. La modificación se adopta después de dos corridas T1
formales excluidas por pérdida transitoria del marcador cerca del umbral visual
y una corrida diagnóstica no formal exitosa con `scenario_id` terminado en
`_DIAG`.

Las corridas diagnósticas no se incorporan al análisis comparativo, ya que la
curación excluye automáticamente los escenarios con sufijo `_DIAG`. Las corridas
aceptadas de `P05_S01_H2_Y04_YAW0` se conservan porque no presentaron abortos
por pérdida de marcador y porque la enmienda solo modifica la tolerancia ante
pérdidas consecutivas, no la ley de corrección lateral, la tasa de descenso ni
el umbral visual de aterrizaje.

La enmienda `P05-A02` actualiza la inicialización de yaw formal de modo
relativo a modo absoluto. Esta enmienda no modifica la regla de curación, pero
sí afecta la interpretación metodológica de los escenarios con orientación
inicial controlada. Las corridas diagnósticas usadas para validar yaw absoluto
deben conservar sufijo `_DIAG` hasta que el procedimiento quede validado para
continuar la secuencia formal.

El diagnostico `P05_S02_H2_Y04_YAW15_ABSYAW_DIAG` confirmo que una corrida
puede reducir el error lateral y aun asi quedar excluida si no alcanza
`landing_threshold_reached=True`. Por tanto, las pruebas con umbrales
terminales alternativos tambien deben conservar sufijo `_DIAG` y no deben
contabilizarse como evidencia formal hasta que exista una enmienda documentada
en la configuracion congelada.

La enmienda `P05-A03` actualiza `frozen_t1.landing_complete_altitude_m` de
`0.80` a `1.05` a partir del diagnostico
`P05_S02_H2_Y04_YAW15_ABSYAW_H105_DIAG`, que alcanzo el umbral visual sin
aborto, con deteccion aceptada `100.0 %` y sin perdidas de marcador. Esta
enmienda no cambia la regla automatica de curacion: una corrida T1 formal sigue
requiriendo `landing_threshold_reached=True`, `landing_success=True`,
`aborted=False` y cierre desarmado. Las corridas `_DIAG` que sustentan la
enmienda permanecen excluidas de metricas comparativas.

Para preservar comparabilidad, los pares formales ejecutados despues de
`P05-A03` deben usar el mismo umbral terminal en T0 y T1. Si una repeticion se
corrige mezclando un T0 pre-enmienda con un T1 post-enmienda, esa decision debe
registrarse como incidencia antes de usarla en analisis pareado.

Como aplicacion de esta regla, los intentos antiguos R05-R07 de
`P05_S02_H2_Y04_YAW15` fueron reemplazados por pares completos bajo `P05-A03`.
Los `run_id` antiguos quedaron en `curation.superseded_runs` y las corridas
correctivas aceptadas son la fuente valida para el analisis pareado R05-R07.

Cuando un intento genera CSV parcial por cierre del simulador y luego se repite
el mismo run, el intento parcial debe declararse `superseded` por la repeticion
aceptada. Caso registrado: `phase05_20260509_001502_30366ed5` supersedido por
`phase05_20260509_001816_20a45b99`.

Cuando un intento T1 aborta de forma aislada por perdida temprana del marcador y
se repite el mismo run sin modificar la configuracion formal, el intento
abortado debe declararse `superseded` por la repeticion aceptada. Caso
registrado: `phase05_20260509_001242_70bda245` supersedido por
`phase05_20260509_003307_468906cb`. El mismo criterio se aplica a S04:
`phase05_20260509_212824_d3037b9b` queda supersedido por
`phase05_20260509_214330_4ae8d025`.

## Uso en analisis

Las tablas y graficos formales deben filtrar:

```text
curation_status == accepted
```

Las corridas `excluded` y `superseded` pueden citarse en incidencias, control de
calidad o discusion metodologica, pero no deben alimentar medias, pruebas
estadisticas ni tasas de exito comparativas.
