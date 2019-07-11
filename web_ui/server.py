#!/usr/bin/env python

import os
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
    if msg['data'] not in detected_objects:
        detected_objects.append(msg['data'])


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
    listener.subscribe(callback)
    global detected_objects
    btn = request.form['btn_object']
    names = request.form.getlist('handles[]')

    if btn == "Observe":
        talker.publish(roslibpy.Message({'data': 'ok'}))
        print(detected_objects)

    # if btn == "Pick":
    #     ur5_move.publish(roslibpy.Message({"position": {"x": 0.5, "y": 0.4, "z": 0.2}}))

    if btn == "Update":
        print(detected_objects)
        db.update_ontology(detected_objects, "INSERT")
        names = db.get_name()
        print(names)

    return render_template("actions.html", names=names)


@app.route("/perception/actions/<name>", methods=['GET', 'POST'])
def show_pos(name):
    pos = request.form.getlist('pos[]')
    status = request.form.getlist('status[]')
    names = db.get_name()
    pos = db.get_info(name)[name]["location"]
    status = db.get_info(name)[name]["status"]
    if request.method == 'POST':
        btn = request.form['btn_object']
        if btn == "Pick":
            ur5_move.publish(roslibpy.Message({"position": {"x": pos[0], "y": pos[1], "z": pos[2]}}))
    return render_template("actions.html", names=names, pos=pos, status=status)


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug="true")
