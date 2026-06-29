# Phase 06 hypothesis tests

- scipy available: `True`
- alpha: `0.05`

## Continuous paired outcomes

| Hypothesis | Metric | n | Normality | Selected test | Statistic | p-value | Decision |
|---|---|---:|---|---|---:|---:|---|
| HE1 | final_error_m_delta_t0_minus_t1 | 80 | Shapiro-Wilk (p=7.66472e-08) | Wilcoxon signed-rank | 3240 | 3.92476e-15 | reject_H0 |
| HE2 | landing_time_s_delta_t0_minus_t1 | 80 | Shapiro-Wilk (p=0.157444) | paired t-test | -27.6887 | 2.01596e-42 | reject_H0 |
| HE3 | visual_dispersion_norm_delta_t0_minus_t1 | 78 | Shapiro-Wilk (p=1.26775e-05) | Wilcoxon signed-rank | 1097 | 0.0271772 | reject_H0 |
| HE3 | command_count_delta_t1_minus_t0 | 80 | Shapiro-Wilk (p=0.565142) | paired t-test | 27.1885 | 7.4351e-42 | reject_H0 |
| HE3 | max_abs_horizontal_command_m_s_delta_t1_minus_t0 | 80 | Shapiro-Wilk (p=6.42363e-06) | Wilcoxon signed-rank | 0 | 7.39174e-15 | reject_H0 |

## Effect size summary

| Hypothesis | Metric | Mean difference | Median difference | Cohen dz | Percent change mean | Direction |
|---|---|---:|---:|---:|---:|---|
| HE1 | final_error_m_delta_t0_minus_t1 | 0.562492 | 0.660237 | 2.85113 | 0.964637 | T1 reduce el error final frente a T0 |
| HE2 | landing_time_s_delta_t0_minus_t1 | -8.24981 | -8.417 | -3.09569 | -0.399703 | T1 modifica el tiempo de aterrizaje frente a T0 |
| HE3 | visual_dispersion_norm_delta_t0_minus_t1 | -0.0226746 | -0.00869731 | -0.399055 | -0.352955 | T1 modifica la dinamica lateral frente a T0 mediante dispersion visual/lateral |
| HE3 | command_count_delta_t1_minus_t0 | 46.6625 | 45.5 | 3.03976 | 0.54568 | T1 modifica la actividad correctiva frente a T0 mediante conteo de comandos |
| HE3 | max_abs_horizontal_command_m_s_delta_t1_minus_t0 | 0.0674045 | 0.0649284 | 2.74316 |  | T1 modifica la intensidad correctiva lateral frente a T0 |

## Categorical outcome

| Hypothesis | Outcome | n pairs | T0 success/T1 success | T0 success/T1 failure | T0 failure/T1 success | T0 failure/T1 failure | Test | p-value | Decision |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| HE4 | landing_success | 80 | 80 | 0 | 0 | 0 | McNemar exact binomial | 1 | fail_to_reject_H0 |
