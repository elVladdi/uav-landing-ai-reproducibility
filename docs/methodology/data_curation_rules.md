# Data Curation Rules

Formal analysis uses only rows with:

```text
curation_status == accepted
```

Accepted runs must contain complete metadata, a valid T0/T1 treatment, `land_complete`, safe disarmed closure, no abort, `landing_success=True`, and for T1 `landing_threshold_reached=True`.

Runs marked `excluded` or `superseded` remain part of methodological traceability but do not feed means, paired tests or success-rate comparisons.

The authoritative curation rule is stored in `configs/phase05_experiment_config.json` under `curation`.
