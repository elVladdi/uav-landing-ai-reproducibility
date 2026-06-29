# Execution Protocol

The full experimental rerun requires AirSimNH, PX4 SITL and the public configuration snapshot. The original formal execution advanced in small blocks rather than running all 160 trials at once.

High-level sequence per run:

1. Clear residual `phase05` markers.
2. Take off to the planned initial height.
3. Apply absolute yaw setup.
4. Spawn the ArUco marker under the vehicle with the planned offset.
5. Execute `T0` or `T1`.
6. Clear marker.
7. Verify PX4 telemetry and safe terminal state.
8. Regenerate Phase 05 summary/report after each block.

For the detailed historical protocol, see `docs/fase05_experimentacion_t0_t1/11_protocolo_ejecucion_formal.md`.
