import numpy as np
from PIL import Image
import io
from typing import List
from fastanpr import FastANPR, NumberPlate


async def get_plate_number(image: np.ndarray, x_1l: float, x_2l: float) -> str:
    image_list = [image]
    plates: List[List[NumberPlate]] = await FastANPR().run(image_list)

    x_m = x_1l + (x_2l - x_1l) / 2
    # sort plates by how close they are to the center of the parking spot
    plates[0].sort(key=lambda plate: abs((plate.det_box[0] + plate.det_box[2]) / 2 - x_m))

    return plates[0][0].rec_text


def bytes_to_ndarray(image_data: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_data))
    image_array = np.array(image, dtype=np.uint8)
    return image_array


# def get_bars_x(image: np.ndarray) -> (float, float):
    # # Threshold the image to create a binary mask
    # threshold = 200  # Adjust this value based on the whiteness of the bars
    # binary_mask = np.where(image >= threshold, 1, 0)
    #
    # # Sum the binary mask along the y-axis
    # column_sums = np.sum(binary_mask, axis=0)
    #
    # # Find the x-coordinates of the two peaks
    # peaks = np.argsort(column_sums)[-2:]  # Get the indices of the two highest peaks
    # x1 = peaks[0]
    # x2 = peaks[1]

def get_bars_x(image):
    height, width, _ = image.shape
    left_line_x = int(width * 0.15)
    right_line_x = int(width * 0.85)
    return left_line_x, right_line_x
