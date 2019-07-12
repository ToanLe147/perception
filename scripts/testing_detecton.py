#!/usr/bin/env python
import numpy as np
import rospy
from std_msgs.msg import String
import os
import tensorflow as tf
import cv2
import pathmagic

# from collections import defaultdict
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# ROS communication
rospy.init_node('testing_detection')
pub = rospy.Publisher('objects_detected', String, queue_size=10)
rate = rospy.Rate(20)

user_command = ""


def callback(msg):
    global user_command
    user_command = msg.data


rospy.Subscriber("observe_table", String, callback)


# Define the video stream
cap = cv2.VideoCapture(0)  # Change only if you have more than one webcams

# What model to download.
# Models can be found here: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
# Model for detection
MODEL_NAME = '/home/led/catkin_ws/src/robot_vision/src/ssd_mobilenet_v1_coco_2017_11_17'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('/home/led/catkin_ws/src/robot_vision/src/models/research/object_detection/data', 'mscoco_label_map.pbtxt')

# Number of classes to detect
NUM_CLASSES = 90

# Load a (frozen) Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Loading test images
PATH_TO_TEST_IMAGES_DIR = '/home/led/catkin_ws/src/robot_vision/src/models/research/object_detection/test_images'
TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR, 'scene_{}.jpg'.format(i)) for i in range(1, 6)]


# Detection
with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        while True:
            # for image in TEST_IMAGE_PATHS:
            # image = TEST_IMAGE_PATHS[1]

            # Read frame from camera
            # ret, image_np = cap.read()
            image = cv2.imread(TEST_IMAGE_PATHS[4])
            image_np = cv2.resize(image, (400, 400))
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Extract image tensor
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Extract detection boxes
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Extract detection scores
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            # Extract detection classes
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            # Extract number of detectionsd
            num_detections = detection_graph.get_tensor_by_name(
                'num_detections:0')
            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})
            # Visualization of the results of a detection.
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

            # Print out results
            if user_command == "ok":
                # Upload result image to web ui
                path = '/home/led/catkin_ws/src/robot_vision/src/web_ui/static/images'
                cv2.imwrite(os.path.join(path, 'observed_scene.jpg'), image_np)

                # Update Ontology
                for i, b in enumerate(boxes[0]):
                    # i: index, b: box
                    if scores[0][i] >= 0.5:
                        x = (b[1] + b[3])/2
                        y = (b[0] + b[2])/2
                        # Crop depth data:
                        object_class = category_index[int(classes[0][i])]['name']
                        if " " in object_class:
                            object_class = object_class.replace(" ", "_")
                        data = "{0}/{1:.1} {2:.1} 0.1".format(object_class, x, y)

                        pub.publish(data)
                        print("Detected a {0} with center {1:.1} {2:.1}.".format(object_class, x, y))
                        rate.sleep()
                # Reset
                user_command = ""

            # Display output
            cv2.imshow('object detection', image_np)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
