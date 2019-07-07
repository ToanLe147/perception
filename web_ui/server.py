#!/usr/bin/env python

import requests
import json
import pygal
from pygal.style import DarkStyle
from flask import Flask, request, render_template


# Flask
app = Flask(__name__)

ontology_server = 'http://localhost:3030/Testing/'
header = {'content-type': 'application/x-www-form-urlencoded'}
prefix = ('PREFIX brainstorm:<http://www.semanticweb.org/led/ontologies/2019/4/brainstorm.owl#> '
          + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> '
          + 'PREFIX owl: <http://www.w3.org/2002/07/owl#> '
          + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> '
          + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> ')


def update_ontology(detected_object, type):
    # type is DELETE or INSERT
    name, raw_string = detected_object.split("/")
    location = raw_string.split(" ")
    # Prepair message
    insert = (' Data { '
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
    msg = {'update': prefix + type + insert}
    requests.post(url=ontology_server+'update', headers=header, data=msg)
    print("Updated Ontology")


def get_info(name):
    query = ("SELECT ?x ?y ?z ?status " +
             "WHERE { " +
             "brainstorm:{}_location brainstorm:x ?x. ".format(name) +
             "brainstorm:{}_location brainstorm:y ?y. ".format(name) +
             "brainstorm:{}_location brainstorm:z ?z. ".format(name) +
             "brainstorm:{}_status brainstorm:pickable ?status.".format(name) +
             "}")
    # send POST request to server
    msg = {'query': prefix + query}
    r = requests.post(url=ontology_server+'query', headers=header, data=msg)
    # Handle response as json type
    res = json.loads(r.content)
    location = [
        float(res["results"]["bindings"][0]["x"]["value"]),
        float(res["results"]["bindings"][0]["y"]["value"]),
        float(res["results"]["bindings"][0]["z"]["value"])]
    status = float(res["results"]["bindings"][0]["status"]["value"])
    return {name: {"location": location, "status": status}}


def get_name():
    object_list = []
    query = ("SELECT ?name " +
             "WHERE {?name a  owl:NamedIndividual , brainstorm:objects .}")
    msg = {'query': prefix + query}
    r = requests.post(url=ontology_server+'query', headers=header, data=msg)
    res = json.loads(r.content)
    for i in res["results"]["bindings"]:
        _, name = i["name"]["value"].split("#")
        object_list.append(name)
    return object_list


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/perception")
def move_to_knowleadge_base():
    return render_template("actions.html")


@app.route("/visual")
def move_to_visual():
    names = get_name()
    graph = pygal.XY(stroke=False, style=DarkStyle)
    graph.title = 'Object Position'

    for name in names:
        x, y, _ = get_info(name)[name]["location"]
        graph.add(name, [{'value': (x, y), 'node': {'r': 6}}])

    graph_data = graph.render_data_uri()
    return render_template("visual.html", graph_data=graph_data)


@app.route("/perception/actions", methods=['POST'])
def actions():
    btn = request.form['btn_object']
    update = request.form['detectedObject']
    names = request.form.getlist('handles[]')
    object_list = get_name()

    if btn == "Observe":
        if not names:
            names = object_list

    if update:
        if btn == "Update":
            update_ontology(update, "INSERT")
            names = []

        if btn == "Delete":
            update_ontology(update, "DELETE")
            names = []

    return render_template("actions.html", names=names)


@app.route("/perception/actions/<name>", methods=['GET'])
def show_pos(name):
    pos = request.form.getlist('pos[]')
    status = request.form.getlist('status[]')
    print(pos, status)
    names = get_name()
    if name in names:
        pos = get_info(name)[name]["location"]
        status = get_info(name)[name]["status"]
    return render_template("actions.html", names=names, pos=pos, status=status)


if __name__ == '__main__':
    app.run(host=os.environ['ROS_IP'], port=8080, debug="true")
    # app.run(host="localhost", port=8080, debug="true")
