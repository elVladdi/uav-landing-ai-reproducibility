# Phase 06 descriptive statistics

## Global treatment summary

| Metric | T0 mean | T0 median | T0 sd | T1 mean | T1 median | T1 sd |
|---|---:|---:|---:|---:|---:|---:|
| Error final (m) | 0.5831 | 0.6835 | 0.1984 | 0.0206 | 0.0211 | 0.0103 |
| Tiempo de aterrizaje (s) | 20.6399 | 21.6295 | 5.8172 | 28.8897 | 28.2915 | 5.8212 |
| Duracion total (s) | 28.1459 | 29.2965 | 5.8111 | 36.3884 | 35.8935 | 5.8516 |
| Tasa de deteccion aceptada | 0.6889 | 0.7482 | 0.2277 | 0.9978 | 1.0000 | 0.0058 |
| Perdidas de deteccion | 21.8750 | 18.5000 | 11.2682 | 0.2500 | 0.0000 | 0.6463 |
| Latencia media (ms) | 119.6310 | 108.8755 | 46.2105 | 75.8052 | 78.2775 | 17.2943 |
| Error visual X medio absoluto | 0.2282 | 0.2291 | 0.1194 | 0.0573 | 0.0573 | 0.0310 |
| Error visual Y medio absoluto | 0.2761 | 0.2762 | 0.1400 | 0.0638 | 0.0554 | 0.0359 |
| Comando horizontal maximo (m/s) | 0.0000 | 0.0000 | 0.0000 | 0.0674 | 0.0649 | 0.0246 |

## Success and abort summary

| Treatment | n | Success count | Success rate | Abort count | Abort rate |
|---|---:|---:|---:|---:|---:|
| T0 | 80 | 80 | 1.0000 | 0 | 0.0000 |
| T1 | 80 | 80 | 1.0000 | 0 | 0.0000 |

## Global paired differences

| Metric | n | Mean | Median | SD | Min | Max | Direction |
|---|---:|---:|---:|---:|---:|---:|---|
| Diferencia error final T0-T1 (m) | 80 | 0.5625 | 0.6602 | 0.1973 | 0.2647 | 0.8568 | T1 lower final error |
| Diferencia tiempo T0-T1 (s) | 80 | -8.2498 | -8.4170 | 2.6649 | -14.8800 | 0.8390 | T1 longer landing time |
| Diferencia deteccion T1-T0 | 80 | 0.3089 | 0.2518 | 0.2286 | 0.0275 | 1.0000 | T1 higher detection rate |

## Scenario coverage

| Scenario | Metric | T0 mean | T1 mean |
|---|---|---:|---:|
| S01 | Error final (m) | 0.3997 | 0.0205 |
| S01 | Tiempo de aterrizaje (s) | 19.6737 | 26.8151 |
| S01 | Tasa de deteccion aceptada | 0.8419 | 0.9890 |
| S02 | Error final (m) | 0.3800 | 0.0172 |
| S02 | Tiempo de aterrizaje (s) | 15.1730 | 22.1800 |
| S02 | Tasa de deteccion aceptada | 0.7085 | 0.9956 |
| S03 | Error final (m) | 0.7850 | 0.0198 |
| S03 | Tiempo de aterrizaje (s) | 13.4011 | 23.8521 |
| S03 | Tasa de deteccion aceptada | 0.3843 | 1.0000 |
| S04 | Error final (m) | 0.7642 | 0.0265 |
| S04 | Tiempo de aterrizaje (s) | 13.8809 | 23.0627 |
| S04 | Tasa de deteccion aceptada | 0.3954 | 0.9979 |
| S05 | Error final (m) | 0.3436 | 0.0215 |
| S05 | Tiempo de aterrizaje (s) | 25.6573 | 30.3875 |
| S05 | Tasa de deteccion aceptada | 0.8864 | 1.0000 |
| S06 | Error final (m) | 0.4756 | 0.0165 |
| S06 | Tiempo de aterrizaje (s) | 25.6391 | 32.8749 |
| S06 | Tasa de deteccion aceptada | 0.8843 | 1.0000 |
| S07 | Error final (m) | 0.7660 | 0.0224 |
| S07 | Tiempo de aterrizaje (s) | 26.6010 | 36.8115 |
| S07 | Tasa de deteccion aceptada | 0.7311 | 1.0000 |
| S08 | Error final (m) | 0.7507 | 0.0205 |
| S08 | Tiempo de aterrizaje (s) | 25.0928 | 35.1336 |
| S08 | Tasa de deteccion aceptada | 0.6791 | 1.0000 |
