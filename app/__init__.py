from flask import Flask, render_template
from bmz import IatiActivity
import os
import xml.etree.ElementTree as ET


def read_iati_activities(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    activities = []

    for activity_element in root.findall(".//iati-activity"):
        activity = IatiActivity()
        activity.from_xml_element(activity_element)
        activities.append(activity)

    return activities


def create_app():
    app = Flask(__name__)

    input_dir = os.path.join("input")
    all_activities = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".xml"):
            xml_path = os.path.join(input_dir, filename)
            iati_activities = read_iati_activities(xml_path)
            all_activities.extend(iati_activities)

    all_activities.sort(key=lambda x: x.total_transaction_value, reverse=True)

    @app.route("/")
    def index():
        return render_template("index.html", activities=all_activities)

    return app
