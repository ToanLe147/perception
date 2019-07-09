#!/usr/bin/env python

import roslibpy


class ros_connect(object):
    def __init__(self):
        self.client = roslibpy.Ros(host="localhost", port=9090)
        # self.client.run()
        self.detected_objects = []

        self.observe = roslibpy.Topic(self.client, '/observe_table', 'std_msgs/String')
        self.command = roslibpy.Topic(self.client, '/UR5_command', 'geometry_msgs/Pose')
        self.detection = roslibpy.Topic(self.client, '/objects_detected', 'std_msgs/String')

        self.observe.advertise()
        self.command.advertise()
        self.detection.advertise()

    def detection_callback(self, msg):
        self.detected_objects.append(msg['data'])

    def observe_btn_pressed(self):
        self.observe.publish(roslibpy.Message({'data': 'ok'}))

    def UR5_moveto(self, goal):
        msg = {"position":
               {"x": goal[0],
                "y": goal[1],
                "z": goal[2]}}
        self.command.publish(roslibpy.Message(msg))
