#!/usr/bin/env python
# This script is used to test communcation between ontology and ROS
import rospy
from std_msgs.msg import String


def talker():
    # data = {"1": ["bottle/0.23 1.57 3.45"],
    #         "n": ["bottle/3.5 1.5 0.2", "pencil/2.7 -2.5 0.2", "pencil/-1.5 1.5 0.2"]}
    pub = rospy.Publisher('chatter', String, queue_size=10)
    # pub = rospy.Publisher('objects_detected', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(0.2)
    count = 0
    while not rospy.is_shutdown():

        if count % 10 == 0:
            user = "ok"
        else:
            user = "not"

        # user = data["n"]
        hello_str = user
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()
        count += 1


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
