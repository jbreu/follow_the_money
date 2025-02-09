import pycountry


class IatiActivity:
    def __init__(self):
        self.identifier = None
        self.title = None
        self.description = None
        self.status = None
        self.start_date = None
        self.end_date = None
        self.budget = None
        self.participating_orgs = []
        self.recipient_countries = []
        self.sectors = []
        self.transactions = []

    def from_xml_element(self, activity_element):
        """
        Parse an XML element representing an IATI activity and populate the class
        attributes

        Args:
            activity_element: XML element containing IATI activity data
        """
        # Basic attributes
        self.identifier = activity_element.get("iati-identifier")

        # Reporting Organization
        reporting_org_elem = activity_element.find("reporting-org")
        if reporting_org_elem is not None:
            narrative = reporting_org_elem.find("narrative")
            if narrative is not None:
                self.reporting_org = narrative.text

        # Title (getting first narrative element if exists)
        title_elem = activity_element.find("title")
        if title_elem is not None:
            narrative = title_elem.find("narrative")
            if narrative is not None:
                self.title = narrative.text

        # Description
        desc_elem = activity_element.find("description")
        if desc_elem is not None:
            narrative = desc_elem.find("narrative")
            if narrative is not None:
                self.description = narrative.text

        # Status
        status_elem = activity_element.find("activity-status")
        if status_elem is not None:
            self.status = status_elem.get("code")

        # Dates
        start_date_elem = activity_element.find('activity-date[@type="1"]')
        if start_date_elem is not None:
            self.start_date = start_date_elem.get("iso-date")

        end_date_elem = activity_element.find('activity-date[@type="2"]')
        if end_date_elem is not None:
            self.end_date = end_date_elem.get("iso-date")

        # Budget
        budget_elem = activity_element.find("budget")
        if budget_elem is not None:
            self.budget = budget_elem.find("value").text

        # Participating Organizations
        for org_elem in activity_element.findall("participating-org"):
            self.participating_orgs.append(org_elem.text)

        # Recipient Countries
        for country_elem in activity_element.findall("recipient-country"):
            country_code = country_elem.get("code")
            try:
                country = pycountry.countries.get(alpha_2=country_code)
                country_name = country.name if country else country_code
                self.recipient_countries.append(country_name)
            except (KeyError, AttributeError):
                self.recipient_countries.append(country_code)

        # Sectors
        for sector_elem in activity_element.findall("sector"):
            self.sectors.append(sector_elem.get("code"))

        # Transactions
        for transaction_elem in activity_element.findall("transaction"):
            transaction = {
                "type": transaction_elem.find("transaction-type").get("code"),
                "date": transaction_elem.find("transaction-date").get("iso-date"),
                "value": transaction_elem.find("value").text,
            }
            self.transactions.append(transaction)
        """
        Parse an XML element representing an IATI activity and populate the class
        attributes

        Args:
            activity_element: XML element containing IATI activity data
        """
        # Basic attributes
        self.identifier = activity_element.get("iati-identifier")

        # Title (getting first narrative element if exists)
        title_elem = activity_element.find("title")
        if title_elem is not None:
            narrative = title_elem.find("narrative")
            if narrative is not None:
                self.title = narrative.text

        # Description
        desc_elem = activity_element.find("description")
        if desc_elem is not None:
            narrative = desc_elem.find("narrative")
            if narrative is not None:
                self.description = narrative.text

        # Status
        status_elem = activity_element.find("activity-status")
        if status_elem is not None:
            self.status = status_elem.get("code")

        # Dates
        start_date_elem = activity_element.find('activity-date[@type="1"]')
        if start_date_elem is not None:
            self.start_date = start_date_elem.get("iso-date")

        end_date_elem = activity_element.find('activity-date[@type="2"]')
        if end_date_elem is not None:
            self.end_date = end_date_elem.get("iso-date")

        # Budget
        budget_elem = activity_element.find("budget")
        if budget_elem is not None:
            self.budget = budget_elem.find("value").text

        # Participating Organizations
        for org_elem in activity_element.findall("participating-org"):
            self.participating_orgs.append(org_elem.text)

        # Recipient Countries
        for country_elem in activity_element.findall("recipient-country"):
            self.recipient_countries.append(country_elem.get("code"))

        # Sectors
        for sector_elem in activity_element.findall("sector"):
            self.sectors.append(sector_elem.get("code"))

        # Transactions
        for transaction_elem in activity_element.findall("transaction"):
            transaction = {
                "type": transaction_elem.find("transaction-type").get("code"),
                "date": transaction_elem.find("transaction-date").get("iso-date"),
                "value": transaction_elem.find("value").text,
            }
            self.transactions.append(transaction)

        # Calculate total transaction value
        self.total_transaction_value = sum(
            float(t["value"]) for t in self.transactions if t["value"] is not None
        )

    def __str__(self):
        """String representation of the IATI activity"""
        return f"IATI Activity: {self.identifier} - {self.title}"
