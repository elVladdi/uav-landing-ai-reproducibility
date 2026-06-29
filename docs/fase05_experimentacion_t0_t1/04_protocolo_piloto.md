# Protocolo Piloto Minimo

## Preparacion comun

Ejecutar desde PowerShell con AirSimNH y PX4 SITL activos:

```powershell
cd <REPO_ROOT>
.\.venv\Scripts\Activate.ps1
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\clear_landing_markers.py --object-regex ".*phase05.*"
```

Si PX4 aparece en `OFFBOARD` o `LAND` estando en tierra y desarmado:

```powershell
python src\control\run_mavlink_mode_recovery.py --confirm-send
python src\control\run_px4_telemetry_check.py --duration 5
```

## Piloto 1: escenario centrado

### T0 centrado

```powershell
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase05_pilot_center_t0 --under-vehicle --z 0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_phase05_t0_baseline_descent.py --confirm-send --duration 25 --detector aruco --save-annotated --descent-rate 0.08 --landing-complete-altitude 0.80 --scenario-id P05_PILOT_CENTER_H2_YAW0 --marker-object-name phase05_pilot_center_t0 --treatment-pair-id P05_PAIR_PILOT_CENTER_R01 --repetition 1 --planned-initial-height-m 2.0 --planned-offset-x-m 0.0 --planned-offset-y-m 0.0 --planned-yaw-deg 0.0
python src\perception\clear_landing_markers.py --object-regex ".*phase05.*"
python src\control\run_px4_telemetry_check.py --duration 5
```

### T1 centrado

```powershell
python src\control\run_px4_takeoff_land_test.py --confirm-send --takeoff-altitude 2.0 --samples-after-takeoff 8 --no-land-after
python src\perception\spawn_fiducial_marker.py --object-name phase05_pilot_center_t1 --under-vehicle --z 0 --scale-x 1.2 --scale-y 1.2 --scale-z 0.01 --dictionary-name DICT_4X4_50 --marker-id 23 --texture-size-px 2048 --marker-size-ratio 0.72
python src\control\run_phase05_t1_visual_descent.py --confirm-send --duration 25 --detector aruco --save-annotated --max-horizontal-speed 0.10 --max-missing-detections 3 --enable-descent --descent-rate 0.08 --centered-cycles-required 5 --landing-complete-altitude 0.80 --scenario-id P05_PILOT_CENTER_H2_YAW0 --marker-object-name phase05_pilot_center_t1 --treatment-pair-id P05_PAIR_PILOT_CENTER_R01 --repetition 1 --planned-initial-height-m 2.0 --planned-offset-x-m 0.0 --planned-offset-y-m 0.0 --planned-yaw-deg 0.0
python src\perception\clear_landing_markers.py --object-regex ".*phase05.*"
python src\control\run_px4_telemetry_check.py --duration 5
```

## Piloto 2: desplazamiento lateral positivo

Repetir el mismo flujo, cambiando el marcador y los metadatos:

- T0: `phase05_pilot_ypos_t0`, `--offset-y 0.8`,
  `--scenario-id P05_PILOT_OFFSET_Y_POS_H2_YAW0`,
  `--treatment-pair-id P05_PAIR_PILOT_YPOS_R01`,
  `--planned-offset-y-m 0.8`.
- T1: `phase05_pilot_ypos_t1`, los mismos metadatos del escenario.

Nota posterior al piloto del 2026-05-05: la corrida T1 con offset positivo
necesito mas tiempo para alcanzar el umbral `landing_complete_altitude=0.80`.
La repeticion con `--duration 40` quedo validada con el run
`phase05_20260505_154421_71272606`. Para escenarios con desplazamiento lateral,
usar `--duration 40` como punto de partida del protocolo formal salvo que una
calibracion posterior justifique otro valor.

## Cierre del piloto

Despues de las cuatro corridas:

```powershell
python src\analysis\phase05_metrics.py
```

El resumen queda en:

```text
data/logs/phase05_experiments/summary/phase05_run_summary.csv
```
