import json
import cv2
import base64
from ultralytics import YOLO
import numpy as np
from ultralytics.utils.plotting import colors
from .color_classifier.classifier import Classifier as ColorClassifier
from .model_classifier.classifier import Classifier as ModelClassifier

class VehicleDetection:

    def __init__(self, model_path="yolov8n.pt"):
        """
        Initialize the VehicleDetection class.

        Args:
            model_path (str): Path to the YOLO model file.
        """
        # Load the YOLO model
        self.model = YOLO(model_path)
        self.color_classifier = None
        self.model_classifier = None

    def _initialize_classifiers(self):
        if self.color_classifier is None:
            self.color_classifier = ColorClassifier()
        if self.model_classifier is None:
            self.model_classifier = ModelClassifier()

    def _encode_image_base64(self, image):
        """
        Encode an image as base64.

        Args:
            image (numpy.ndarray): The image to be encoded.

        Returns:
            str: Base64-encoded image.
        """
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode()
        return image_base64

    def _decode_image_base64(self, image_base64):
        """
        Decode a base64-encoded image.

        Args:
            image_base64 (str): Base64-encoded image data.

        Returns:
            numpy.ndarray or None: Decoded image as a numpy array or None if decoding fails.
        """
        try:
            image_data = base64.b64decode(image_base64)
            image_np = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_np, flags=cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            return None

    def _increase_brightness(self, image, factor=1.5):
        """
        Increases the brightness of an image by multiplying its pixels by a factor.

        :param image: The input image in numpy array format.
        :param factor: The brightness increase factor. A value greater than 1 will increase brightness.
        :return: The image with increased brightness.
        """
        brightened_image = cv2.convertScaleAbs(image, alpha=factor, beta=0)
        return brightened_image

    def process_image_base64(self, image_base64):
        """
        Process a base64-encoded image to detect vehicles.

        Args:
            image_base64 (str): Base64-encoded input image for processing.

        Returns:
            dict or None: Processed information including detected vehicles' details and the annotated image in base64,
            or an error message if decoding fails.
        """
        image = self._decode_image_base64(image_base64)
        if image is not None:
            return self.process_image(image)
        else:
            return {
                "error": "Failed to decode the base64 image"
            }

    def process_image(self, image):
        """
        Process a single image to detect vehicles.

        Args:
            image (numpy.ndarray): Input image for processing.

        Returns:
            dict: Processed information including detected vehicles' details, the annotated image in base64, and the original image in base64.
        """
        self._initialize_classifiers()
        response = {
            "number_of_vehicles_detected": 0,  # Counter for vehicles detected in this image
            "detected_vehicles": [],  # List of information about detected vehicles
            "annotated_image_base64": None,  # Annotated image as a base64 encoded image
            "original_image_base64": None  # Original image as a base64 encoded image
        }
        # Process a single image and return detection results, an annotated image, and the original image as base64.
        results = self.model(self._increase_brightness(image))
        if results is not None and len(results) > 0:
            # Obtain bounding boxes (xywh format) of detected objects
            boxes = results[0].boxes.xywh.cpu()
            # Extract confidence scores for each detected object
            conf_list = results[0].boxes.conf.cpu()
            # Obtain the class labels (e.g., 'car', 'truck') for detected objects
            clss = results[0].boxes.cls.cpu().tolist()
            # Retrieve the names of the detected objects based on class labels
            names = results[0].names

            for box, cls, conf in zip(boxes, clss, conf_list):
                x, y, w, h = box
                label = str(names[cls])
                # Bounding box plot
                bbox_color = colors(cls, True)

                # Increment the counter
                response["number_of_vehicles_detected"] += 1

                # Extract the frame of the detected vehicle
                vehicle_frame = image[int(y - h / 2):int(y + h / 2), int(x - w / 2):int(x + w / 2)]
                vehicle_frame_base64 = self._encode_image_base64(vehicle_frame)
                color_info = self.color_classifier.predict(vehicle_frame)
                color_info_json = json.dumps(color_info)
                model_info = self.model_classifier.predict(vehicle_frame)
                model_info_json = json.dumps(model_info)

                # Add vehicle information to the response
                response["detected_vehicles"].append({
                    "vehicle_type": label,
                    "detection_confidence": conf.item(),
                    "vehicle_coordinates": {
                        "x": x.item(),
                        "y": y.item(),
                        "width": w.item(),
                        "height": h.item()
                    },
                    "vehicle_frame_base64": vehicle_frame_base64,
                    "color_info": color_info_json,
                    "model_info": model_info_json
                })

            annotated_image = results[0].plot()
            annotated_image_base64 = self._encode_image_base64(annotated_image)
            response["annotated_image_base64"] = annotated_image_base64

        # Encode the original image as base64
        original_image_base64 = self._encode_image_base64(image)
        response["original_image_base64"] = original_image_base64

        return response