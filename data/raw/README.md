# Carpeta `data/raw`

Esta carpeta contiene datos crudos generados durante pruebas tecnicas y corridas experimentales.

## Proposito

Almacenar evidencia primaria no procesada antes de cualquier limpieza, filtrado, agregacion o analisis estadistico.

## Contenido esperado

Ejemplos de archivos que pueden ubicarse localmente aqui:

- registros originales exportados por scripts de corrida;
- capturas crudas seleccionadas;
- datos de entrada generados por AirSim;
- datos iniciales de percepcion visual;
- archivos originales por `run_id`.

## Politica de versionado

Por defecto, esta carpeta solo publica en Git:

- `README.md`
- `.gitkeep`

No se versionan datos crudos masivos, secuencias completas de imagenes, videos, dumps del simulador ni capturas generadas automaticamente.

Si una captura o archivo crudo pequeno fuera necesario para reproducir un ejemplo minimo, debe agregarse como excepcion documentada con `git add -f` y citarse desde el documento que lo use.

## Relacion con Fase 05

Tras el cierre formal de Fase 05, los datos crudos T0/T1 deben conservarse
localmente o en almacenamiento externo. La trazabilidad debe mantenerse mediante
`run_id`, escenario, tratamiento, fecha de ejecucion y ruta de evidencia.

No deben borrarse ni sobrescribirse logs crudos asociados a corridas formales,
incluyendo registros `accepted`, `excluded` o `superseded`.
