#!/usr/bin/env python

# This script can detect object then the distance between object and camera.

# import system dependencies
import numpy as np
import rospy
from std_msgs.msg import String
import os
import pathmagic
import pyrealsense2 as rs

# import image processing libs
import tensorflow as tf
import cv2

# import from object detection libs
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# ROS communication
pub = rospy.Publisher('objects_detected', String, queue_size=10)
rospy.init_node('object_detection')
rate = rospy.Rate(10)

# Define the video stream
# cap = cv2.VideoCapture(3)

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


# Detection
with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        while True:

            # Read frame from webcam
            # ret, image_np = cap.read()

            # Read from Realsense and wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            # Align color images and depth images
            align = rs.align(rs.stream.color)
            aligned_frames = align.process(frames)

            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Tell pointcloud object to map to this color frame
            pc.map_to(color_frame)

            # Generate the pointcloud and texture mappings
            points = pc.calculate(depth_frame)

            # Crop depth data:
            depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
            # Get camera intrinsics
            depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data()) * depth_scale
            image_np = np.asanyarray(color_frame.get_data())
            print(image_np.shape)

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            colorizer = rs.colorizer()
            depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())
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

            # Visualization of the results of a detection on color image.
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

            # Visualization of the results of a detection on depth image.
            vis_util.visualize_boxes_and_labels_on_image_array(
                depth_colormap,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

            # Get data scale from the device and convert to meters
            height, width = image_np.shape[:2]

            for i, b in enumerate(boxes[0]):
                # i: index, b: box [ymin, xmin, ymax, xmax]
                if scores[0][i] >= 0.5:
                    # depth_image has size [480, 640]
                    mid_y = min(int((b[0]+b[2])*height*0.5), 480)
                    mid_x = min(int((b[1]+b[3])*width*0.5), 640)

                    # Calculate x, y, z in world coordinates
                    depth_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [mid_y, mid_x], depth_image[mid_y, mid_x])

                    print("Mid: ", mid_x, mid_y, depth_image[mid_y, mid_x], depth_point)
                    # print(depth_image)

                    object_class = category_index[int(classes[0][i])]['name']

                    # print(depth_image)
                    print("Detected a {0} {1} meters away.".format(object_class, depth_point[2]))
                    pub.publish(object_class)
                    rate.sleep()

            # Stack both images horizontally
            images = np.hstack((image_np, depth_colormap))

            # Display output
            cv2.imshow('object detection', images)
            # cv2.imshow('remove_background', test)

            # Press q to quit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
