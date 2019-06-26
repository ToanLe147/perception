#!/usr/bin/env python

import requests
import rospy
from std_msgs.msg import String

rospy.init_node("reasoner", anonymous=True)

url = 'http://localhost:3030/Testing/update'
header = {'content-type': 'application/x-www-form-urlencoded'}

objects_list = []


def callback(msg):
    detection = msg.data
    if detection not in objects_list:
        objects_list.append(detection)
        # Prepair message
        prefix = 'PREFIX mrbv21:<http://www.semanticweb.org/led/ontologies/2019/4/mrbv2.owl#> ' + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ' + 'PREFIX owl: <http://www.w3.org/2002/07/owl#> ' + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> '

        insert = 'INSERT Data {' + 'mrbv21:Lecturer3 rdf:type mrbv21:teacher. ' + 'mrbv21:Lecturer3 a owl:NamedIndividual. ' + 'mrbv21:Lecturer3 mrbv21:teaches mrbv21:M601, mrbv21:CS103. ' + 'mrbv21:Lecturer3 mrbv21:firstname ' + detection + '. ' + 'mrbv21:Lecturer3 mrbv21:lastname ' + detection + '. ' + 'mrbv21:Lecturer3 mrbv21:teacherID "111111"^^xsd:int. }'

        msg = {'update': prefix + insert}

        r = requests.post(url=url, headers=header, data=msg)

        rospy.loginfo("Update Ontology: ", response)
    else:
        rospy.loginfo("No new objects: ", detection)


rospy.Subscriber("objects_detected", String, callback)

rospy.spin()
