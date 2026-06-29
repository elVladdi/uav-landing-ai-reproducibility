# Phase 05 Run Summary Schema

Each row represents one summarized run.

Key fields:

- `run_id`: unique run identifier.
- `source_file`: original raw CSV path relative to the project.
- `phase`: expected value `fase05`.
- `treatment`: `T0` or `T1`.
- `scenario_id`: formal scenario identifier.
- `treatment_pair_id`: paired T0/T1 comparison key.
- `repetition`: repetition number within scenario.
- `curation_status`: `accepted`, `excluded` or `superseded`.
- `final_error_m`: horizontal final landing error.
- `landing_time_s`: time to landing threshold.
- `accepted_detection_rate`: accepted visual detections divided by visual samples.
- `landing_success`: terminal success flag.
