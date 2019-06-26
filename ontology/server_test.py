#!/usr/bin/env python

import requests
import rospy
from std_msgs.msg import String

rospy.init_node("reasoner", anonymous=True)

url = 'http://localhost:3030/Testing/'
header = {'content-type': 'application/x-www-form-urlencoded'}

objects_list = []
detection = ""
prefix = ('PREFIX brainstorm:<http://www.semanticweb.org/led/ontologies/2019/4/brainstorm.owl#> '
          + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> '
          + 'PREFIX owl: <http://www.w3.org/2002/07/owl#> '
          + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> '
          + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> ')


def Update(name, location):
    # small trick to ger correct name. Modifying later for new model of detection
    if " " in name:
        name = name.split()[0]
    # Prepair message
    insert = ('INSERT Data { '
              + 'brainstorm:{}_status a owl:NamedIndividual , '.format(name)
              + 'brainstorm:informations ; '
              + 'brainstorm:pickable "1"^^xsd:int; '
              + 'brainstorm:placeable "0"^^xsd:int. '

              + 'brainstorm:{}_location a owl:NamedIndividual , '.format(name)
              + 'brainstorm:informations ; '
              + 'brainstorm:x {}; '.format(location[0])
              + 'brainstorm:y {}; '.format(location[1])
              + 'brainstorm:z {}. '.format(location[2])

              + 'brainstorm:{} a owl:NamedIndividual , brainstorm:objects ;'.format(name)
              + ' brainstorm:hasLocation brainstorm:{}_location; '.format(name)
              + 'brainstorm:hasStatus brainstorm:{}_status.'.format(name)
              + '}'
              )

    # send POST request to server
    msg = {'update': prefix + insert}
    requests.post(url=url+'update', headers=header, data=msg)


def Query(name):

    query = ("SELECT ?x ?y ?z ?status " +
             "WHERE { " +
             "brainstorm:{}_location brainstorm:x ?x. ".format(name) +
             "brainstorm:{}_location brainstorm:y ?y. ".format(name) +
             "brainstorm:{}_location brainstorm:z ?z. ".format(name) +
             "brainstorm:{}_status brainstorm:pickable ?status.".format(name) +
             "}")
    # send POST request to server
    msg = {'query': prefix + query}
    r = requests.post(url=url+'query', headers=header, data=msg)
    response = r.text
    # Handle response - how to handle json type?
    print(response)


def callback(msg):
    data = msg.data
    # Handle receiving data to get class and location of object
    name, coordinates = data.split('/')
    x, y, z = coordinates.split(" ")
    # Update the ontology
    if name not in objects_list:
        location = [float(x), float(y), float(z)]
        objects_list.append(name)
        Update(name, location)
        # rospy.loginfo("Update Ontology: " + detection)
    else:
        user = input("Pick 1 {}: ".format(objects_list))
        Query(user)
        # rospy.loginfo("No new objects")
        print(objects_list)


rospy.Subscriber("objects_detected", String, callback)

rospy.spin()
