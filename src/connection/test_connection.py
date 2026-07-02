"""Minimal AirSim connectivity smoke test for local simulator setup.

This diagnostic confirms that Python can reach AirSim. It is not part of the
formal T0/T1 evidence chain and does not produce analytical outputs.
"""

import airsim

client = airsim.MultirotorClient()
client.confirmConnection()

print("Conexión correcta con AirSim")
