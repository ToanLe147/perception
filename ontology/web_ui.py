#!/usr/bin/env python

import requests
import rospy
from std_msgs.msg import String
from flask import Flask, request, render_template, make_response


# Flask
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("home.html")


@app.route("/action", methods=['POST'])
def action():
    user = request.form['text']
    if user == "u":
        return "Done"


@app.route("/query", methods=['POST'])
def query():
    user = request.form['text']
    # print(user)
    # url = 'http://localhost:3030/Testing/query'
    # header = {'content-type': 'application/x-www-form-urlencoded'}
    # msg = {"query": user}
    # response = requests.post(url, headers=header, data=msg)
    # test = response.text
    # return test


# Reasoner class
class reasoner():
    def __init__(self):
        self.url = 'http://localhost:3030/Testing/'
        self.header = {'content-type': 'application/x-www-form-urlencoded'}
        self.objects_list = []
        self.object_class = ''
        self.object_location = []
        self.detection = ""
        self.prefix = ('PREFIX brainstorm:<http://www.semanticweb.org/led/ontologies/2019/4/brainstorm.owl#> '
                        + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
                        + 'PREFIX owl: <http://www.w3.org/2002/07/owl#> '
                        + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> '
                        + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> ')

    def get_data(self, msg):
        data = msg.data
        # Handle receiving data to get class and location of object
        self.object_class, coordinates = data.split('/')
        # if " " in name:
        #     self.object_class = name.split(" ")[0]
        self.object_location = [float(i) for i in coordinates.split(" ")]
        # print(self.object_class)

    def update(self):
        # small trick to ger correct name. Modifying later for new model of detection
        if " " in self.object_class:
            self.object_class = self.object_class.split()[0]
        # Prepair message
        insert = ('INSERT Data { '
                  + 'brainstorm:{}_status a owl:NamedIndividual , '.format(self.object_class)
                  + 'brainstorm:informations ; '
                  + 'brainstorm:pickable "1"^^xsd:int; '
                  + 'brainstorm:placeable "0"^^xsd:int. '

                  + 'brainstorm:{}_location a owl:NamedIndividual , '.format(self.object_class)
                  + 'brainstorm:informations ; '
                  + 'brainstorm:x {}; '.format(self.object_location[0])
                  + 'brainstorm:y {}; '.format(self.object_location[1])
                  + 'brainstorm:z {}. '.format(self.object_location[2])

                  + 'brainstorm:{} a owl:NamedIndividual , brainstorm:objects ;'.format(self.object_class)
                  + ' brainstorm:hasLocation brainstorm:{}_location; '.format(self.object_class)
                  + 'brainstorm:hasStatus brainstorm:{}_status.'.format(self.object_class) + '}')

        # send POST request to server
        msg = {'update': self.prefix + insert}
        requests.post(url=self.url+'update', headers=self.header, data=msg)

    def query(self):
        query = ("SELECT ?x ?y ?z ?status " +
                 "WHERE { " +
                 "brainstorm:{}_location brainstorm:x ?x. ".format(self.object_class) +
                 "brainstorm:{}_location brainstorm:y ?y. ".format(self.object_class) +
                 "brainstorm:{}_location brainstorm:z ?z. ".format(self.object_class) +
                 "brainstorm:{}_status brainstorm:pickable ?status.".format(self.object_class) +
                 "}")
        # send POST request to server
        msg = {'query': self.prefix + query}
        r = requests.post(url=self.url+'query', headers=self.header, data=msg)
        response = r.text
        # Handle response - how to handle json type?
        print(response)


def main():
    perception = reasoner()
    app.run(host="localhost", port=8080, debug="true")
    rospy.init_node("reasoner")
    rospy.Subscriber("objects_detected", String, perception.get_data)


if __name__ == '__main__':
    main()
