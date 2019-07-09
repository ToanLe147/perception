#!/usr/bin/env python

import pygal
from pygal.style import DarkStyle
from flask import Flask, request, render_template
import roslibpy
# import pathmagic

# Test
from ontology_manager import ontology
# from views import visual, perception


db = ontology()
detected_objects = []
# Flask
app = Flask(__name__)
client = roslibpy.Ros(host='localhost', port=9090)
client.run()

talker = roslibpy.Topic(client, '/observe_table', 'std_msgs/String')
ur5_move = roslibpy.Topic(client, '/UR5_command', 'geometry_msgs/Pose')
ur5_move.advertise()
talker.advertise()
listener = roslibpy.Topic(client, '/objects_detected', 'std_msgs/String')
listener.advertise()


def callback(msg):
    global detected_objects
    detected_objects.append(msg['data'])


listener.subscribe(callback)


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/perception")
def move_to_knowleadge_base():
    return render_template("actions.html")


@app.route("/visual")
def move_to_visual():
    names = db.get_name()
    graph = pygal.XY(stroke=False, style=DarkStyle)
    graph.title = 'Object Position'

    for name in names:
        x, y, _ = db.get_info(name)[name]["location"]
        graph.add(name, [{'value': (x, y), 'node': {'r': 6}}])

    graph_data = graph.render_data_uri()
    return render_template("visual.html", graph_data=graph_data)


@app.route("/perception/actions", methods=['POST'])
def actions():
    global detected_objects
    btn = request.form['btn_object']
    update = [request.form['detectedObject']]
    names = request.form.getlist('handles[]')

    if btn == "Observe":
        talker.publish(roslibpy.Message({'data': 'ok'}))
        ur5_move.publish(roslibpy.Message({"position": {"x": 0.2, "y": 0.1, "z": 0.5}}))
        if len(detected_objects) != 0:
            print(detected_objects)
            updated = db.update_ontology(detected_objects, "INSERT")
        # if updated:
        object_list = db.get_name()
        if not names:
            names = object_list
            detected_objects = []

    if btn == "Pick":
        ur5_move.publish(roslibpy.Message({"position": {"x": 0.5, "y": 0.4, "z": 0.2}}))

    if update:
        if btn == "Update":
            db.update_ontology(update, "INSERT")
            names = []

        if btn == "Delete":
            db.update_ontology(update, "DELETE")
            names = []

    return render_template("actions.html", names=names)


@app.route("/perception/actions/<name>", methods=['GET'])
def show_pos(name):
    pos = request.form.getlist('pos[]')
    status = request.form.getlist('status[]')
    names = db.get_name()
    if name in names:
        pos = db.get_info(name)[name]["location"]
        status = db.get_info(name)[name]["status"]
    return render_template("actions.html", names=names, pos=pos, status=status)


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug="true")
