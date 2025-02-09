from flask import Flask, render_template
from bmz import IatiActivity
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)


def read_iati_activities(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    activities = []

    for activity_element in root.findall(".//iati-activity"):
        activity = IatiActivity()
        activity.from_xml_element(activity_element)
        activities.append(activity)

    return activities


@app.route("/")
def index():
    input_dir = os.path.join("input")
    all_activities = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".xml"):
            xml_path = os.path.join(input_dir, filename)
            iati_activities = read_iati_activities(xml_path)
            all_activities.extend(iati_activities)

    return render_template("index.html", activities=all_activities)


if __name__ == "__main__":
    app.run(debug=True)
