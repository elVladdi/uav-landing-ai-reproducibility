# Statistical Analysis Plan

The Phase 06 analysis evaluates paired T0/T1 outcomes.

Primary outcomes:

- Final landing error (`final_error_m`).
- Landing time (`landing_time_s`).
- Lateral/visual dynamics and corrective activity.
- Landing success/failure.

Statistical procedure:

1. Audit dataset completeness and pair coverage.
2. Generate descriptive statistics by treatment and scenario.
3. Test normality of paired differences with Shapiro-Wilk.
4. Use paired t-test when differences are compatible with normality.
5. Use Wilcoxon signed-rank when differences are non-normal.
6. Use exact McNemar/binomial logic for paired categorical success/failure.
7. Interpret p-values with practical effect sizes and simulation scope limits.
