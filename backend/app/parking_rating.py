import math

import numpy as np
from scipy.interpolate import interp1d, PchipInterpolator

from vehicle_detection_tracker.VehicleDetectionTracker.VehicleDetectionTracker import VehicleDetection


# calculates the rating of a single parking job based on how well it is between the lines
def get_image_info(image: np.ndarray, x_1l: float, x_2l: float):
    vehicle_detection = VehicleDetection()
    frame_data = vehicle_detection.process_image(image)
    # remove "vehicle_frame_base64" from frame_data["detected_vehicles"]
    for vehicle in frame_data["detected_vehicles"]:
        vehicle.pop("vehicle_frame_base64", None)
    print(frame_data["detected_vehicles"])
    if frame_data["number_of_vehicles_detected"] < 1:
        return -1

    # filter by closeness to the center of the parking spot
    vehicles = frame_data["detected_vehicles"]
    vehicles.sort(key=lambda vehicle: abs(vehicle["vehicle_coordinates"]["x"] - (x_1l + (x_2l - x_1l) / 2)))

    vehicle = vehicles[0]
    print(vehicle)
    coords = vehicle["vehicle_coordinates"]
    x_c = coords["x"]

    x_m = x_1l + (x_2l - x_1l) / 2  # x_m is the middle of the parking spot
    error = abs(x_m - x_c)
    score = (1 - error / ((x_2l - x_1l) / 2)) * 10  # normalize the error to be between 0 and 10

    # Given data points
    x_points = [0, 8, 9.81, 10]
    y_points = [0, 4.14, 9.81, 10]

    # Create the PCHIP interpolator
    interpolator = PchipInterpolator(x_points, y_points)
    score: float = interpolator(score).item()

    # print for debugging
    print(f"x_m: {x_m}")
    print(f"x_c: {x_c}")
    print(f"error: {error}")

    # create dict with score and annotated image
    return {
        "score": score,
        "annotated_image_base64": frame_data["annotated_image_base64"]
    }