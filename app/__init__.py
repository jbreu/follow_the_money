from flask import Flask, render_template, request
from bmz import IatiActivity
from kleineAnfrage208838 import KleineAnfrage208838
import os
import pdfplumber
import xml.etree.ElementTree as ET
from .database import (
    init_db,
    batch_insert_activities,
    get_filtered_activities,
    get_metadata,
    get_activity_transactions,
)


def read_iati_activities(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    activities = []

    for activity_element in root.findall(".//iati-activity"):
        activity = IatiActivity()
        activity.from_xml_element(activity_element)
        activities.append(activity)

    return activities


def read_kleine_anfrage_activities(pdf_file_path):
    activities = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages[3:94]:
            tables = page.extract_tables()
            for table in tables:
                print(
                    f"Processing table {tables.index(table) + 1} on page {pdf.pages.index(page) + 1}"
                )
                for row in table:
                    activity = KleineAnfrage208838()
                    if activity.from_pdf_table_row(row) is not None:
                        activities.append(activity)

        for page in pdf.pages[95:]:
            tables = page.extract_tables()
            for table in tables:
                print(
                    f"Processing table {tables.index(table) + 1} on page {pdf.pages.index(page) + 1}"
                )
                for row in table:
                    activity = KleineAnfrage208838()
                    if activity.from_pdf_table_row(row, 2024) is not None:
                        activities.append(activity)

    return activities


def create_app():
    app = Flask(__name__)

    # Initialize database only if it doesn't exist
    db_path = os.path.join(os.path.dirname(__file__), "activities.db")

    if not os.path.exists(db_path):
        init_db()
        # Initialize database and load data
        input_dir = os.path.join("input")

        # Load XML data into SQLite using batch inserts
        for filename in os.listdir(input_dir):
            if filename.endswith(".xml"):
                xml_path = os.path.join(input_dir, filename)
                activities = read_iati_activities(xml_path)
                batch_insert_activities(activities)

        # Load PDF data from input directory
        pdf_dir = os.path.join("input")
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_dir, filename)
                activities = read_kleine_anfrage_activities(pdf_path)
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
        )

    return app
