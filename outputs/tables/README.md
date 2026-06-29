# Carpeta `outputs/tables`

Esta carpeta contiene tablas derivadas del analisis tecnico o experimental.

## Proposito

Almacenar resultados tabulares livianos y verificables para tesis, articulo o documentacion del repositorio.

## Contenido esperado

Ejemplos locales:

- resumen de metricas por corrida;
- comparacion T0/T1;
- tablas de exito/fallo;
- resultados estadisticos;
- tablas de analisis de errores;
- tablas en formato `.csv` o `.md`.

## Politica de versionado

Por defecto, esta carpeta solo publica:

- `README.md`
- `.gitkeep`

Las tablas generadas automaticamente quedan ignoradas. Una tabla final puede versionarse como excepcion con `git add -f` si es liviana, estable, reproducible desde scripts y necesaria para sustentar una conclusion.

## Relacion con Fase 05

Al cierre formal de Fase 05, esta carpeta conserva las tablas finales de
comparacion entre T0 y T1, incluyendo error final, tiempo de aterrizaje,
estabilidad, tasa de exito y diferencias pareadas.

Las tablas versionadas de `phase05_experiments/` documentan `160/160` corridas
formales aceptadas, `80` pares T0/T1 y `16/16` celdas escenario/tratamiento
completas. Deben mantenerse reproducibles desde:

```powershell
python src\analysis\phase05_metrics.py
python src\analysis\phase05_formal_report.py
```
