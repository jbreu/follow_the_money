from flask import Flask, render_template, request
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

        filtered_activities = all_activities

        year = request.args.get("year")
        organization = request.args.get("organization")
        min_value = request.args.get("min_value")
        max_value = request.args.get("max_value")
        country = request.args.get("country")
        search = request.args.get("search")

        if search:
            search_terms = search.lower().split()
            filtered_activities = [
                a
                for a in filtered_activities
                if a.title and all(term in a.title.lower() for term in search_terms)
            ]

        if year:
            filtered_activities = [
                a
                for a in filtered_activities
                if a.start_date and a.start_date.startswith(year)
            ]
        if organization:
            filtered_activities = [
                a
                for a in filtered_activities
                if organization.lower() in (a.reporting_org or "").lower()
            ]
        if min_value:
            filtered_activities = [
                a
                for a in filtered_activities
                if a.total_transaction_value >= float(min_value)
            ]
        if max_value:
            filtered_activities = [
                a
                for a in filtered_activities
                if a.total_transaction_value <= float(max_value)
            ]
        if country:
            filtered_activities = [
                a
                for a in filtered_activities
                if country in (a.recipient_countries or [])
            ]

        filtered_activities.sort(key=lambda x: x.total_transaction_value, reverse=True)

        # Get unique years from start dates
        available_years = sorted(
            list(
                set(
                    activity.start_date[:4]
                    for activity in all_activities
                    if activity.start_date
                )
            ),
            reverse=True,
        )

        # Get unique organizations
        available_organizations = sorted(
            list(
                set(
                    activity.reporting_org
                    for activity in all_activities
                    if activity.reporting_org
                )
            )
        )

        # Get unique recipient countries
        available_countries = sorted(
            list(
                set(
                    country
                    for activity in all_activities
                    for country in (activity.recipient_countries or [])
                )
            )
        )

        return render_template(
            "index.html",
            activities=filtered_activities,
            available_years=available_years,
            available_organizations=available_organizations,
            available_countries=available_countries,
        )

    return app
