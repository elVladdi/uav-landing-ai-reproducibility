# Carpeta `data`

Esta carpeta organiza los datos asociados a pruebas tecnicas y corridas experimentales del proyecto **UAV Landing AI**.

## Proposito

Mantener una estructura reproducible para datos crudos, logs de ejecucion y datos procesados derivados de las fases experimentales, especialmente durante la Fase 05 de comparacion T0/T1.

Al cierre formal de Fase 05, los logs crudos completos permanecen fuera de Git
y se conservan localmente o en almacenamiento externo. La evidencia versionada
del experimento formal queda en el resumen curado
`data/logs/phase05_experiments/summary/phase05_run_summary.csv` y en las tablas
finales de `outputs/tables/phase05_experiments/`.

## Contenido esperado

- Datos crudos generados durante corridas experimentales.
- Logs de ejecucion del simulador, percepcion, control y autopiloto.
- Datos procesados para analisis estadistico.
- Archivos livianos de trazabilidad metodologica.

## Politica de versionado

Por defecto, Git solo versiona en esta carpeta:

- `README.md`
- `.gitkeep`

Los datos experimentales completos quedan ignorados por `.gitignore` para evitar subir logs, capturas, videos o archivos binarios pesados.

Si una muestra reducida es indispensable para reproducibilidad, debe incorporarse de forma controlada: documentar su origen, justificarla en el README o documento metodologico correspondiente y agregarla explicitamente con `git add -f`.

## Relacion con la reproducibilidad

Esta carpeta preserva la estructura esperada del experimento sin sobrecargar el repositorio. Los datos completos deben conservarse localmente o en almacenamiento externo, indicando rutas, `run_id`, fecha y, cuando sea posible, checksum o mecanismo de recuperacion.
