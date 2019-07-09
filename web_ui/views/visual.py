from flask import Blueprint, render_template
from ontology_manager import ontology
import pygal
from pygal.style import DarkStyle


db = ontology()

bp = Blueprint('visual', __name__)


@bp.route("/visual")
def move_to_visual():
    names = db.get_name()
    graph = pygal.XY(stroke=False, style=DarkStyle)
    graph.title = 'Object Position'

    for name in names:
        x, y, _ = db.get_info(name)[name]["location"]
        graph.add(name, [{'value': (x, y), 'node': {'r': 6}}])

    graph_data = graph.render_data_uri()
    return render_template("visual.html", graph_data=graph_data)
