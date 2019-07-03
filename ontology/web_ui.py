#!/usr/bin/env python

import requests
import json
import rospy
from flask import Flask, request, render_template, url_for


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
    # type: DELETE or INSERT
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
    return name


def get_position(name):
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


@app.route("/update", methods=['POST'])
def update():
    user = request.form['detectedObject']
    res = "Nothing"
    if request.form['btn_object'] == "Update":
        res = update_ontology(user, "INSERT")
    if request.form['btn_object'] == "Delete":
        res = update_ontology(user, "DELETE")
    return render_template("home.html", object=res)


@app.route("/query", methods=['POST'])
def query():
    user = request.form['inputQuery']
    load = get_position(user)
    return str(load)


@app.route("/observe", methods=['POST'])
def Observe():
    names = request.form.getlist('handles[]')
    object_list = get_name()
    if not names:
        names = object_list
    return render_template('home.html', names=names)


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug="true")
