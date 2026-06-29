# Experimental Design T0/T1

The experiment compares two treatments under equivalent initial conditions.

- `T0`: baseline descent without intelligent visual lateral correction. Passive perception can be logged, but visual error is not used to command lateral motion.
- `T1`: visually assisted landing using ArUco detection, normalized visual error, bounded lateral correction and MAVLink direct velocity setpoints.

The formal design uses eight scenarios from a 2 x 2 x 2 factor grid:

| Factor | Levels |
|---|---|
| Initial height | 2.0 m, 3.0 m |
| Lateral offset Y | 0.4 m, 0.8 m |
| Initial yaw | 0 deg, 15 deg |

Each scenario contains 10 repetitions per treatment, for 160 accepted formal runs and 80 paired T0/T1 comparisons.

The authoritative configuration snapshot is `configs/phase05_experiment_config.json`.
