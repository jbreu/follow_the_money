from flask import Flask, render_template, request
from bmz import IatiActivity
from kleineAnfrage208838 import read_kleine_anfrage208838_activities
from kleineAnfrage2003843 import read_kleine_anfrage2003843_activities
from demokratieleben1 import read_demokratieleben1_activities
import os
import xml.etree.ElementTree as ET
from .database import (
    init_db,
    batch_insert_activities,
    get_filtered_activities,
    get_metadata,
    get_activity_transactions,
    get_sources,
)
from dotenv import load_dotenv


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
    load_dotenv()
    app = Flask(__name__)

    # Add this to ensure proper UTF-8 handling
    app.config["JSON_AS_ASCII"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///activities.db?charset=utf8"

    # Initialize database only if it doesn't exist
    db_path = os.path.join(os.path.dirname(__file__), "activities.db")

    if not os.path.exists(db_path):
        init_db()
        # Initialize database and load data
        input_dir = os.path.join("input")

        # Load PDF data from input directory
        pdf_dir = os.path.join("input")
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, filename)
                activities = []

                if "2008838" in filename:
                    activities = read_kleine_anfrage208838_activities(pdf_path)
                    for activity in activities:
                        activity.source_id = "bundestag_2008838"

                if "2003843" in filename:
                    activities = read_kleine_anfrage2003843_activities(pdf_path)
                    for activity in activities:
                        activity.source_id = "bundestag_2003843"

                if "demokratie-leben1" in filename:
                    activities += read_demokratieleben1_activities(pdf_path)
                    for activity in activities:
                        activity.source_id = "demokratie_leben_1"

                batch_insert_activities(activities)

        # Load XML data into SQLite using batch inserts
        for filename in os.listdir(input_dir):
            if filename.endswith(".xml"):
                xml_path = os.path.join(input_dir, filename)
                activities = read_iati_activities(xml_path)

                source_id = None
                if "bmz-iati-export" in filename:
                    source_id = "bmz_iati"
                elif "Ressorts_R" in filename:
                    source_id = "bmz_ressorts_r"
                elif "Ressorts_C" in filename:
                    source_id = "bmz_ressorts_c"

                for activity in activities:
                    activity.source_id = source_id

                batch_insert_activities(activities)

    @app.route("/")
    def index():
        filtered_activities = [
            dict(a)
            for a in get_filtered_activities(
                year=request.args.get("year"),
                organization=request.args.get("organization"),
                min_value=request.args.get("min_value"),
                max_value=request.args.get("max_value"),
                country=request.args.get("country"),
                search=request.args.get("search"),
                recipient_organization=request.args.get("recipient_organization"),
            )
        ]

        # Limit to 100 filtered activities before adding transactions
        for activity in filtered_activities[:100]:
            activity["transactions"] = [
                dict(t) for t in get_activity_transactions(activity["iati_identifier"])
            ]

        metadata = get_metadata()

        return render_template(
            "index.html",
            activities=filtered_activities,
            available_years=metadata["years"],
            available_organizations=metadata["organizations"],
            available_countries=metadata["countries"],
            available_recipient_organizations=metadata["recipient_organizations"],
            base_url=os.getenv("BASE_URL", ""),
            subfolder=os.getenv("SUBFOLDER", ""),
            sources=get_sources(),
        )

    return app
