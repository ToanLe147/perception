#!/usr/bin/env python

# import os
from flask import Flask, render_template
from web_ui.views import visual, perception


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)
    #
    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    #  Register blueprints
    app.register_blueprint(visual.bp)
    app.register_blueprint(perception.bp)

    @app.route("/")
    def index():
        return render_template("home.html")

    return app
