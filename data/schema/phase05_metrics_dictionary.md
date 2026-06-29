# Phase 05 Metrics Dictionary

Primary metrics:

- `final_error_m`: horizontal distance between UAV and marker center at terminal event.
- `landing_time_s`: elapsed time until landing threshold or last visual/control event.
- `landing_success`: accepted landing success state.
- Visual/lateral dynamics: dispersion of normalized visual errors and command activity.

Support metrics:

- `accepted_detection_rate`.
- `lost_detection_count`.
- `latency_ms_mean` and `latency_ms_max`.
- `command_count`.
- `descent_command_count`.
- `max_abs_horizontal_command_m_s`.
