# Carpeta `data/logs`

Esta carpeta contiene logs de ejecucion asociados a validaciones tecnicas, pruebas piloto y corridas experimentales.

## Proposito

Organizar bitacoras que permitan auditar el comportamiento del sistema durante las fases de integracion y experimentacion.

## Contenido esperado

Ejemplos de logs locales:

- conexion PX4/AirSim;
- MAVLink o MAVSDK;
- percepcion visual;
- controlador o agente;
- eventos de aborto seguro;
- errores relevantes;
- bitacoras por `run_id`.

## Politica de versionado

Por defecto, esta carpeta solo publica en Git:

- `README.md`
- `.gitkeep`

Los logs completos se ignoran porque pueden crecer rapidamente y porque se regeneran durante cada corrida.

Cuando un log reducido sea evidencia indispensable para tesis, articulo o depuracion reproducible, debe agregarse como excepcion con `git add -f` y registrarse junto con su `run_id`, escenario, tratamiento y fecha.

## Relacion con la reproducibilidad

Los logs permiten reconstruir incidencias, validar condiciones de ejecucion y justificar exclusiones de corridas. En Fase 05 deben vincularse siempre con `run_id`, tratamiento aplicado y escenario experimental.

Para el cierre formal de Fase 05, el repositorio versiona el resumen curado
`data/logs/phase05_experiments/summary/phase05_run_summary.csv`. Los CSV crudos
por corrida permanecen fuera de Git, pero deben conservarse como evidencia
auditable.
