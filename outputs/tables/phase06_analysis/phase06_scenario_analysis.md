# Phase 06 scenario analysis

## Scenario summary

| Scenario | Height | Offset Y | Yaw | Error T0 | Error T1 | Error reduction | Time T0 | Time T1 | Time delta T0-T1 | Detection gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S01 | 2.0 | 0.4 | 0 | 0.3997 | 0.0205 | 0.3792 | 19.6737 | 26.8151 | -7.1414 | 0.1471 |
| S02 | 2.0 | 0.4 | 15 | 0.3800 | 0.0172 | 0.3629 | 15.1730 | 22.1800 | -7.0070 | 0.2870 |
| S03 | 2.0 | 0.8 | 0 | 0.7850 | 0.0198 | 0.7652 | 13.4011 | 23.8521 | -10.4510 | 0.6157 |
| S04 | 2.0 | 0.8 | 15 | 0.7642 | 0.0265 | 0.7377 | 13.8809 | 23.0627 | -9.1818 | 0.6024 |
| S05 | 3.0 | 0.4 | 0 | 0.3436 | 0.0215 | 0.3220 | 25.6573 | 30.3875 | -4.7302 | 0.1136 |
| S06 | 3.0 | 0.4 | 15 | 0.4756 | 0.0165 | 0.4591 | 25.6391 | 32.8749 | -7.2358 | 0.1157 |
| S07 | 3.0 | 0.8 | 0 | 0.7660 | 0.0224 | 0.7436 | 26.6010 | 36.8115 | -10.2105 | 0.2689 |
| S08 | 3.0 | 0.8 | 15 | 0.7507 | 0.0205 | 0.7302 | 25.0928 | 35.1336 | -10.0408 | 0.3209 |

## Factor summary

| Factor | Level | n pairs | Error reduction | Time delta T0-T1 | Detection gain |
|---|---:|---:|---:|---:|---:|
| height_m | 2.0 | 40 | 0.5612 | -8.4453 | 0.4131 |
| height_m | 3.0 | 40 | 0.5637 | -8.0543 | 0.2048 |
| offset_y_m | 0.4 | 40 | 0.3808 | -6.5286 | 0.1659 |
| offset_y_m | 0.8 | 40 | 0.7442 | -9.9710 | 0.4520 |
| yaw_deg | 0.0 | 40 | 0.5525 | -8.1333 | 0.2863 |
| yaw_deg | 15.0 | 40 | 0.5725 | -8.3664 | 0.3315 |

## Rankings

| Rank type | Rank | Scenario | Value | Interpretation |
|---|---:|---|---:|---|
| largest_error_reduction | 1 | S03 | 0.7652 | Mayor reduccion media de error final con T1. |
| largest_error_reduction | 2 | S07 | 0.7436 | Mayor reduccion media de error final con T1. |
| largest_error_reduction | 3 | S04 | 0.7377 | Mayor reduccion media de error final con T1. |
| smallest_error_reduction | 1 | S05 | 0.3220 | Menor reduccion media de error final con T1. |
| smallest_error_reduction | 2 | S02 | 0.3629 | Menor reduccion media de error final con T1. |
| smallest_error_reduction | 3 | S01 | 0.3792 | Menor reduccion media de error final con T1. |
| largest_time_cost | 1 | S03 | -10.4510 | Mayor incremento temporal de T1 respecto a T0. |
| largest_time_cost | 2 | S07 | -10.2105 | Mayor incremento temporal de T1 respecto a T0. |
| largest_time_cost | 3 | S08 | -10.0408 | Mayor incremento temporal de T1 respecto a T0. |
| smallest_time_cost | 1 | S05 | -4.7302 | Menor incremento temporal de T1 respecto a T0. |
| smallest_time_cost | 2 | S02 | -7.0070 | Menor incremento temporal de T1 respecto a T0. |
| smallest_time_cost | 3 | S01 | -7.1414 | Menor incremento temporal de T1 respecto a T0. |
| largest_detection_gain | 1 | S03 | 0.6157 | Mayor mejora media en tasa de deteccion aceptada. |
| largest_detection_gain | 2 | S04 | 0.6024 | Mayor mejora media en tasa de deteccion aceptada. |
| largest_detection_gain | 3 | S08 | 0.3209 | Mayor mejora media en tasa de deteccion aceptada. |
