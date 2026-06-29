# Phase 06 incident and error-source analysis

## Treatment-level incident summary

| Treatment | n | Success rate | Abort rate | Lost detections mean | Detection rate mean | Mean latency | Max latency observed | Final error max | Landing time max | Horizontal command max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| T0 | 80 | 1.0000 | 0.0000 | 21.8750 | 0.6889 | 119.6310 | 532.6800 | 0.8895 | 29.5310 | 0.0000 |
| T1 | 80 | 1.0000 | 0.0000 | 0.2500 | 0.9978 | 75.8052 | 246.4800 | 0.0473 | 43.4070 | 0.1000 |

## Scenario-treatment summary

| Scenario | Treatment | Lost detections mean | Detection rate mean | Mean latency | Final error max | Landing time max | Visual X sd mean | Visual Y sd mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| S01 | T0 | 12.7000 | 0.8419 | 110.7497 | 0.5002 | 20.8990 | 0.0761 | 0.0191 |
| S01 | T1 | 1.3000 | 0.9890 | 92.8561 | 0.0371 | 29.0460 | 0.0538 | 0.0169 |
| S02 | T0 | 17.3000 | 0.7085 | 118.2675 | 0.4616 | 18.9150 | 0.0242 | 0.0341 |
| S02 | T1 | 0.5000 | 0.9956 | 80.6128 | 0.0269 | 26.8820 | 0.0356 | 0.0636 |
| S03 | T0 | 24.3000 | 0.3843 | 180.3826 | 0.8579 | 15.6200 | 0.0338 | 0.0263 |
| S03 | T1 | 0.0000 | 1.0000 | 84.0427 | 0.0377 | 26.0760 | 0.0755 | 0.1147 |
| S04 | T0 | 28.9000 | 0.3954 | 175.2896 | 0.8420 | 15.6180 | 0.0215 | 0.0217 |
| S04 | T1 | 0.2000 | 0.9979 | 80.0120 | 0.0410 | 24.7610 | 0.0860 | 0.1182 |
| S05 | T0 | 12.9000 | 0.8864 | 89.7160 | 0.3705 | 29.1920 | 0.0353 | 0.0460 |
| S05 | T1 | 0.0000 | 1.0000 | 76.1679 | 0.0473 | 35.5500 | 0.0243 | 0.0387 |
| S06 | T0 | 14.1000 | 0.8843 | 72.6716 | 0.8463 | 29.5310 | 0.0437 | 0.0690 |
| S06 | T1 | 0.0000 | 1.0000 | 57.5771 | 0.0323 | 36.6960 | 0.0253 | 0.0341 |
| S07 | T0 | 30.2000 | 0.7311 | 110.6844 | 0.8895 | 29.1630 | 0.0469 | 0.0610 |
| S07 | T1 | 0.0000 | 1.0000 | 76.6790 | 0.0389 | 43.4070 | 0.0467 | 0.0675 |
| S08 | T0 | 34.6000 | 0.6791 | 99.2862 | 0.7989 | 28.6700 | 0.0465 | 0.0630 |
| S08 | T1 | 0.0000 | 1.0000 | 58.4938 | 0.0331 | 37.7350 | 0.0469 | 0.0741 |

## Extreme runs

| Category | Rank | Scenario | Treatment | Value | Run ID |
|---|---:|---|---|---:|---|
| highest_final_error | 1 | S07 | T0 | 0.8895 | phase05_20260608_130247_e28ac4f0 |
| highest_final_error | 2 | S03 | T0 | 0.8579 | phase05_20260509_000310_08ba7fc5 |
| highest_final_error | 3 | S06 | T0 | 0.8463 | phase05_20260607_233910_4a8cd7ec |
| highest_final_error | 4 | S04 | T0 | 0.8420 | phase05_20260607_201947_00bacbf8 |
| highest_final_error | 5 | S04 | T0 | 0.8312 | phase05_20260607_210540_4e06679b |
| longest_landing_time | 1 | S07 | T1 | 43.4070 | phase05_20260608_131411_c3801822 |
| longest_landing_time | 2 | S07 | T1 | 38.7510 | phase05_20260608_105539_0b6fcf44 |
| longest_landing_time | 3 | S07 | T1 | 38.5120 | phase05_20260608_112944_5eb17392 |
| longest_landing_time | 4 | S07 | T1 | 38.3160 | phase05_20260608_105157_18017f67 |
| longest_landing_time | 5 | S07 | T1 | 38.1760 | phase05_20260608_131743_02ff76bb |
| lowest_detection_rate | 1 | S03 | T0 | 0.0000 | phase05_20260509_000902_46f50524 |
| lowest_detection_rate | 2 | S03 | T0 | 0.0000 | phase05_20260509_010204_ea0ffbac |
| lowest_detection_rate | 3 | S04 | T0 | 0.1800 | phase05_20260607_202802_f1ccaa50 |
| lowest_detection_rate | 4 | S04 | T0 | 0.1852 | phase05_20260509_212437_424a9706 |
| lowest_detection_rate | 5 | S03 | T0 | 0.2059 | phase05_20260509_004647_e3423cd3 |
| highest_lost_detection_count | 1 | S06 | T0 | 45.0000 | phase05_20260607_233910_4a8cd7ec |
| highest_lost_detection_count | 2 | S07 | T0 | 44.0000 | phase05_20260608_113207_9cd80600 |
| highest_lost_detection_count | 3 | S08 | T0 | 44.0000 | phase05_20260608_150148_ca339b4f |
| highest_lost_detection_count | 4 | S08 | T0 | 44.0000 | phase05_20260608_154116_86105482 |
| highest_lost_detection_count | 5 | S04 | T0 | 42.0000 | phase05_20260607_211514_29807371 |
| highest_mean_latency | 1 | S04 | T0 | 312.4915 | phase05_20260509_212437_424a9706 |
| highest_mean_latency | 2 | S03 | T0 | 266.8020 | phase05_20260509_010204_ea0ffbac |
| highest_mean_latency | 3 | S03 | T0 | 235.2427 | phase05_20260509_000902_46f50524 |
| highest_mean_latency | 4 | S04 | T0 | 219.3668 | phase05_20260509_211541_7721a9cb |
| highest_mean_latency | 5 | S04 | T0 | 205.6174 | phase05_20260509_212246_507d9664 |
| highest_max_latency | 1 | S04 | T0 | 532.6800 | phase05_20260509_212437_424a9706 |
| highest_max_latency | 2 | S01 | T0 | 530.7900 | phase05_20260505_171646_b0d3f4a0 |
| highest_max_latency | 3 | S04 | T0 | 513.6200 | phase05_20260509_212246_507d9664 |
| highest_max_latency | 4 | S03 | T0 | 417.5200 | phase05_20260509_010204_ea0ffbac |
| highest_max_latency | 5 | S03 | T0 | 409.8700 | phase05_20260509_005615_8743cfbe |
| highest_horizontal_command | 1 | S03 | T1 | 0.1000 | phase05_20260509_000451_0b969adf |
| highest_horizontal_command | 2 | S03 | T1 | 0.1000 | phase05_20260509_001816_20a45b99 |
| highest_horizontal_command | 3 | S03 | T1 | 0.1000 | phase05_20260509_004244_9f022853 |
| highest_horizontal_command | 4 | S03 | T1 | 0.1000 | phase05_20260509_004447_9d806e29 |
| highest_horizontal_command | 5 | S03 | T1 | 0.1000 | phase05_20260509_005801_2841af18 |
| highest_visual_x_dispersion | 1 | S04 | T1 | 0.1201 | phase05_20260607_203502_6e0b3de1 |
| highest_visual_x_dispersion | 2 | S03 | T1 | 0.1177 | phase05_20260509_010004_a268301d |
| highest_visual_x_dispersion | 3 | S03 | T1 | 0.1155 | phase05_20260509_000701_eb58d52f |
| highest_visual_x_dispersion | 4 | S03 | T1 | 0.1149 | phase05_20260509_004447_9d806e29 |
| highest_visual_x_dispersion | 5 | S03 | T1 | 0.1146 | phase05_20260509_001816_20a45b99 |
| highest_visual_y_dispersion | 1 | S03 | T1 | 0.1767 | phase05_20260509_000451_0b969adf |
| highest_visual_y_dispersion | 2 | S04 | T1 | 0.1751 | phase05_20260607_203218_26efe62a |
| highest_visual_y_dispersion | 3 | S03 | T1 | 0.1727 | phase05_20260509_011302_debefdda |
| highest_visual_y_dispersion | 4 | S03 | T1 | 0.1714 | phase05_20260509_004244_9f022853 |
| highest_visual_y_dispersion | 5 | S03 | T1 | 0.1693 | phase05_20260509_005801_2841af18 |

## Terminal states

| Treatment | Terminal event | Terminal status | Aborted | Count |
|---|---|---|---|---:|
| T0 | land_complete | landing | False | 80 |
| T1 | land_complete | landing | False | 80 |
