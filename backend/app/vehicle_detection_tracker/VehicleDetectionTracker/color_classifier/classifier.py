# Copyright © 2019 by Spectrico
# Licensed under the MIT License
import os

import cv2
import numpy as np
import tensorflow as tf

# In VehicleDetectionTracker/color_classifier/config.py
model_file = "/vehicle_detection_tracker/VehicleDetectionTracker/" + "data/model-weights-spectrico-car-colors-mobilenet-224x224-052EAC82.pb"
label_file = "/vehicle_detection_tracker/VehicleDetectionTracker/" + "data/color_labels.txt"
input_layer = "input_1"
output_layer = "softmax/Softmax"
classifier_input_size = (224, 224)


def print_directory_tree(directory, level=0):
    # Get the list of files and directories in the current directory
    entries = os.listdir(directory)

    # Sort the entries alphabetically
    entries.sort()

    # Iterate over each entry
    for entry in entries:
        # Get the full path of the entry
        path = os.path.join(directory, entry)

        # Print the entry with appropriate indentation
        print("|   " * level + "+-- " + entry)

        # If the entry is a directory, recursively print its contents
        if os.path.isdir(path):
            print_directory_tree(path, level + 1)

def load_graph(model_file):
    # print out file tree to debug
    graph_def = tf.compat.v1.GraphDef()
    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")
    return graph

def load_labels(label_file):
    label = []
    with open(label_file, "r", encoding='cp1251') as ins:
        for line in ins:
            label.append(line.rstrip())
    return label

def resizeAndPad(img, size, padColor=0):
    h, w = img.shape[:2]
    sh, sw = size
    # interpolation method
    if h > sh or w > sw:
        # shrinking image
        interp = cv2.INTER_AREA
    else:
        # stretching image
        interp = cv2.INTER_CUBIC
    # aspect ratio of image
    aspect = w / h
    # compute scaling and pad sizing
    if aspect > 1:
        # horizontal image
        new_w = sw
        new_h = np.round(new_w / aspect).astype(int)
        pad_vert = (sh - new_h) / 2
        pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
        pad_left, pad_right = 0, 0
    elif aspect < 1:
        # vertical image
        new_h = sh
        new_w = np.round(new_h * aspect).astype(int)
        pad_horz = (sw - new_w) / 2
        pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
        pad_top, pad_bot = 0, 0
    else:
        # square image
        new_h, new_w = sh, sw
        pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0
    # set pad color
    if len(img.shape) == 3 and not isinstance(padColor, (list, tuple, np.ndarray)):
        # color image but only one color provided
        padColor = [padColor] * 3
    # scale and pad
    scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
    scaled_img = cv2.copyMakeBorder(scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=padColor)
    return scaled_img

class Classifier:
    def __init__(self):
        # uncomment the next 3 lines if you want to use CPU instead of GPU
        # import os
        # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        # os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        self.graph = load_graph(model_file)
        self.labels = load_labels(label_file)
        input_name = input_layer
        output_name = output_layer
        self.input_operation = self.graph.get_operation_by_name(input_name)
        self.output_operation = self.graph.get_operation_by_name(output_name)

    def predict(self, img):
        img = img[:, :, ::-1]
        img = resizeAndPad(img, classifier_input_size)
        # Add a forth dimension since Tensorflow expects a list of images
        img = np.expand_dims(img, axis=0)
        # Scale the input image to the range used in the trained network
        img = img.astype(np.float32)
        img /= 127.5
        img -= 1.
        with tf.compat.v1.Session(graph=self.graph) as sess:
            results = sess.run(self.output_operation.outputs[0], {self.input_operation.outputs[0]: img})
        results = np.squeeze(results)
        top = 3
        top_indices = results.argsort()[-top:][::-1]
        classes = []
        for ix in top_indices:
            classes.append({"color": self.labels[ix], "prob": str(results[ix])})
        return classes