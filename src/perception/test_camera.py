import airsim
import cv2
import numpy as np
import os

client = airsim.MultirotorClient()
client.confirmConnection()

responses = client.simGetImages([
    airsim.ImageRequest(
        "bottom_center",
        airsim.ImageType.Scene,
        False,
        False
    )
])

response = responses[0]

if response.height == 0 or response.width == 0:
    raise RuntimeError("No se recibió imagen válida desde AirSim")

img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
img = img1d.reshape(response.height, response.width, 3)

os.makedirs("outputs", exist_ok=True)
cv2.imwrite("outputs/captura_bottom_center.png", img)

print("Imagen guardada en outputs/captura_bottom_center.png")
print("Resolución:", response.width, "x", response.height)