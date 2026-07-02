"""Minimal AirSim multirotor-state diagnostic for local simulator setup.

The printed position, orientation, and velocity are useful for checking AirSim
connectivity, but they are not curated Phase 05 data.
"""

import airsim

client = airsim.MultirotorClient()
client.confirmConnection()

state = client.getMultirotorState(vehicle_name="Drone1")

position = state.kinematics_estimated.position
orientation = state.kinematics_estimated.orientation
velocity = state.kinematics_estimated.linear_velocity

print("Posición:")
print("x:", position.x_val)
print("y:", position.y_val)
print("z:", position.z_val)

print("\nOrientación:")
print("w:", orientation.w_val)
print("x:", orientation.x_val)
print("y:", orientation.y_val)
print("z:", orientation.z_val)

print("\nVelocidad:")
print("vx:", velocity.x_val)
print("vy:", velocity.y_val)
print("vz:", velocity.z_val)
