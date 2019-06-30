#!/usr/bin/env python

import requests
import rospy
from std_msgs.msg import String
from flask import Flask, request, render_template, make_response, url_for


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
    url = 'http://localhost:3030/Testing/query'
    header = {'content-type': 'application/x-www-form-urlencoded'}
    msg = {"query": user}
    response = requests.post(url, headers=header, data=msg)
    test = response.text
    return test


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug="true")
