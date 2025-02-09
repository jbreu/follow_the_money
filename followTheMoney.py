from bmz import IatiActivity
import os

import xml.etree.ElementTree as ET


def read_iati_activities(xml_file_path):
    """
    Read IATI XML file and return a list of IatiActivity objects

    Args:
        xml_file_path (str): Path to the IATI XML file

    Returns:
        list: List of IatiActivity objects
    """
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # List to store all activities
    activities = []

    # Find all activity elements and create IatiActivity objects
    for activity_element in root.findall(".//iati-activity"):
        activity = IatiActivity()
        activity.from_xml_element(activity_element)
        activities.append(activity)

    return activities


# Example usage:
if __name__ == "__main__":
    # Read all XML files from input directory
    input_dir = "input"
    all_activities = []

    try:
        # Iterate through all files in input directory
        for filename in os.listdir(input_dir):
            if filename.endswith(".xml"):
                xml_path = os.path.join(input_dir, filename)
                iati_activities = read_iati_activities(xml_path)
                all_activities.extend(iati_activities)
                print(f"Loaded {len(iati_activities)} activities from {filename}")

        print(f"\nTotal activities loaded: {len(all_activities)}")

        # Sort activities by total transaction value in descending order and print top 100
        sorted_activities = sorted(
            all_activities,
            key=lambda x: (
                float(x.total_transaction_value)
                if x.total_transaction_value is not None
                else 0
            ),
            reverse=True,
        )
        for i, activity in enumerate(sorted_activities[:100]):
            start_year = activity.start_date[:4] if activity.start_date else "N/A"
            end_year = activity.end_date[:4] if activity.end_date else "N/A"
            print(
                f"{i+1}. Total Transaction Value: {float(activity.total_transaction_value):,.2f} € - {start_year}-{end_year} - {activity.reporting_org} -> {', '.join(activity.recipient_countries)} - Title: {activity.title}"
            )

    except Exception as e:
        print(f"Error processing IATI XML files: {e}")
