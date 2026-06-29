# Carpeta `outputs/figures`

Esta carpeta contiene figuras academicas o tecnicas generadas a partir del desarrollo del proyecto.

## Proposito

Organizar figuras utilizadas en documentacion, tesis o articulo cientifico.

## Contenido esperado

Ejemplos locales:

- diagramas de arquitectura;
- diagramas de flujo;
- graficos de error;
- graficos de comparacion T0/T1;
- figuras de validacion visual;
- visualizaciones de trayectoria o metricas.

## Politica de versionado

El `.gitignore` del repositorio ignora imagenes globalmente. Por defecto, esta carpeta solo publica:

- `README.md`
- `.gitkeep`

Las figuras generadas masivamente no deben versionarse. Si una imagen es necesaria para que un README o documento metodologico sea comprensible y reproducible, puede incluirse como excepcion controlada con `git add -f`.

## Criterios para una excepcion de imagen

Una imagen puede versionarse solo si cumple todo lo siguiente:

- representa una evidencia final o minima, no una captura intermedia;
- esta referenciada desde un README o documento de fase;
- tiene origen trazable: script, `run_id`, datos o procedimiento;
- tiene tamano razonable para Git;
- no duplica informacion disponible en tablas o texto.

## Relacion con la reproducibilidad

Las figuras deben derivarse de scripts, datos o documentacion verificable. No sustituyen los datos experimentales originales ni deben usarse para afirmar resultados no ejecutados.

Las figuras de resultados de Fase 05 deben derivarse de las tablas curadas
versionadas en `outputs/tables/phase05_experiments/`, correspondientes al
cierre formal de `160/160` corridas aceptadas y `80` pares T0/T1.
