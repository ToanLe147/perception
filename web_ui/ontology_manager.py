#!/usr/bin/env python
import requests
import json


class ontology():
    def __init__(self):
        self.detected_objects = []
        self.ontology_server = 'http://localhost:3030/Testing/'
        self.header = {'content-type': 'application/x-www-form-urlencoded'}
        self.prefix = ('PREFIX brainstorm:<http://www.semanticweb.org/led/ontologies/2019/4/brainstorm.owl#> '
                       + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> '
                       + 'PREFIX owl: <http://www.w3.org/2002/07/owl#> '
                       + 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> '
                       + 'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> ')

    def update_ontology(self, objects, type):
        for detected_object in objects:
            # type is DELETE or INSERT
            name, raw_string = detected_object.split("/")
            location = raw_string.split(" ")
            if name not in self.detected_objects:
                self.detected_objects.append(name)
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
                msg = {'update': self.prefix + type + insert}
                requests.post(url=self.ontology_server+'update', headers=self.header, data=msg)
        return True

    def get_info(self, name):
        query = ("SELECT ?x ?y ?z ?status " +
                 "WHERE { " +
                 "brainstorm:{}_location brainstorm:x ?x. ".format(name) +
                 "brainstorm:{}_location brainstorm:y ?y. ".format(name) +
                 "brainstorm:{}_location brainstorm:z ?z. ".format(name) +
                 "brainstorm:{}_status brainstorm:pickable ?status.".format(name) +
                 "}")
        # send POST request to server
        msg = {'query': self.prefix + query}
        r = requests.post(url=self.ontology_server+'query', headers=self.header, data=msg)
        # Handle response as json type
        res = json.loads(r.content)
        location = [
            float(res["results"]["bindings"][0]["x"]["value"]),
            float(res["results"]["bindings"][0]["y"]["value"]),
            float(res["results"]["bindings"][0]["z"]["value"])]
        status = float(res["results"]["bindings"][0]["status"]["value"])
        return {name: {"location": location, "status": status}}

    def get_name(self):
        query = ("SELECT ?name " +
                 "WHERE {?name a  owl:NamedIndividual , brainstorm:objects .}")
        msg = {'query': self.prefix + query}
        r = requests.post(url=self.ontology_server+'query', headers=self.header, data=msg)
        res = json.loads(r.content)
        for i in res["results"]["bindings"]:
            _, name = i["name"]["value"].split("#")
            if name not in self.detected_objects:
                self.detected_objects.append(name)
        return self.detected_objects
