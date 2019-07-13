#!/usr/bin/env python
import numpy as np
import rospy
from std_msgs.msg import String
import os
import tensorflow as tf
import cv2
import pyrealsense2 as rs
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
# cap = cv2.VideoCapture(0)  # Change only if you have more than one webcams

# Configure depth and color streams from Realsense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Pointcloud persistency in case of dropped frames
pc = rs.pointcloud()
points = rs.points()

# Start streaming
profile = pipeline.start(config)

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
TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR, 'scene_{}.jpg'.format(i)) for i in range(1, 8)]


# Detection
with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        while True:
            # Read frame from camera
            # ret, image_np = cap.read()
            image = cv2.imread(TEST_IMAGE_PATHS[5])
            width = int(image.shape[1] * 0.2)
            height = int(image.shape[0] * 0.2)
            dim = (width, height)
            image_np = cv2.resize(image, dim)

            ##=============== REALSENSE ======================
            # # Read from Realsense and wait for a coherent pair of frames: depth and color
            # frames = pipeline.wait_for_frames()
            # # Align color images and depth images
            # align = rs.align(rs.stream.color)
            # aligned_frames = align.process(frames)
            #
            # depth_frame = aligned_frames.get_depth_frame()
            # color_frame = aligned_frames.get_color_frame()
            # if not depth_frame or not color_frame:
            #     continue
            #
            # # Tell pointcloud object to map to this color frame
            # pc.map_to(color_frame)
            #
            # # Generate the pointcloud and texture mappings
            # points = pc.calculate(depth_frame)
            #
            # # Crop depth data:
            # depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
            # # Get camera intrinsics
            # depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
            #
            # # Convert images to numpy arrays
            # depth_image = np.asanyarray(depth_frame.get_data()) * depth_scale
            # image_np = np.asanyarray(color_frame.get_data())
            #
            # # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            # colorizer = rs.colorizer()
            # depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())
            ##=====================================

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
                    # i: index, b: box [%top, %left, %bottom, %right]
                    if scores[0][i] >= 0.5:
                        x = (b[1] + b[3])/2
                        y = (b[0] + b[2])/2

                        ##============ REALSENSE ==============
                        # using depth data for GPD no need in implementation of perception.
                        ##=====================================

                        # Crop depth data:
                        object_class = category_index[int(classes[0][i])]['name']
                        if " " in object_class:
                            object_class = object_class.replace(" ", "_")
                        data = "{0}/{1:.2} {2:.2} 0.15/{3:.3} {4:.3} {5:.3} {6:.3}".format(object_class, x, y, b[0], b[1], b[2], b[3])

                        pub.publish(data)
                        print("Detected a {0} with center {1:.1} {2:.1}.".format(object_class, x, y))
                        rate.sleep()
                # Reset
                user_command = ""

            # Display output
            cv2.imshow('object detection', image_np)
            # cv2.imshow('depth detection', depth_image)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
