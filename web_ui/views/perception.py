#!/usr/bin/env python
from flask import Blueprint, render_template, request
from ontology_manager import ontology
from ROS_communicator import ros_connect


bp = Blueprint('perception', __name__, url_prefix="/perception")
db = ontology()
ros = ros_connect()


@bp.route("")
def move_to_knowleadge_base():
    return render_template("actions.html")


@bp.route("/actions", methods=['POST'])
def actions():
    btn = request.form['btn_object']
    update = [request.form['detectedObject']]
    names = request.form.getlist('handles[]')

    if btn == "Observe":
        ros.observe_btn_pressed()
        ros.UR5_moveto([.2, .1, .5])
        if len(ros.detected_objects) != 0:
            print(ros.detected_objects)
            db.update_ontology(ros.detected_objects, "INSERT")
        # if updated:
        object_list = db.get_name()
        if not names:
            names = object_list
            ros.detected_objects = []

    if btn == "Pick":
        ros.UR5_moveto([.5, .4, .2])

    if update:
        if btn == "Update":
            db.update_ontology(update, "INSERT")
            names = []

        if btn == "Delete":
            db.update_ontology(update, "DELETE")
            names = []

    return render_template("actions.html", names=names)


@bp.route("/actions/<name>", methods=['GET'])
def show_pos(name):
    pos = request.form.getlist('pos[]')
    status = request.form.getlist('status[]')
    names = db.get_name()
    if name in names:
        pos = db.get_info(name)[name]["location"]
        status = db.get_info(name)[name]["status"]
    return render_template("actions.html", names=names, pos=pos, status=status)
