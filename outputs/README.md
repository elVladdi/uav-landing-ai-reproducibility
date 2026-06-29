# Carpeta `outputs`

Esta carpeta organiza salidas generadas a partir del procesamiento tecnico y experimental del proyecto.

## Proposito

Separar resultados derivados del analisis, como figuras, tablas y reportes, de los datos crudos y procesados.

## Contenido esperado

- figuras finales o seleccionadas;
- tablas comparativas;
- reportes derivados;
- graficos para tesis o articulo;
- salidas analiticas reproducibles.

## Politica de versionado

Por defecto, Git solo versiona:

- `README.md`
- `.gitkeep`

Las salidas generadas quedan ignoradas para evitar que el repositorio acumule archivos pesados o redundantes.

Cuando una salida final sea imprescindible para reproducibilidad o lectura academica, debe versionarse como excepcion controlada con `git add -f`, citando el script, datos de origen y criterio de seleccion.

## Relacion con la reproducibilidad

Esta carpeta debe contener resultados derivados y trazables a partir de datos o scripts del repositorio. No debe incluir resultados manuales no verificables ni metricas inventadas.

Para Fase 05, las salidas finales versionadas se concentran en
`outputs/tables/phase05_experiments/` y se regeneran desde el resumen curado
con `src/analysis/phase05_metrics.py` y
`src/analysis/phase05_formal_report.py`.
