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
        self.total_transaction_value = 0.0
        self.reporting_org = None

    def from_xml_element(self, activity_element):
        self.identifier = activity_element.get("iati-identifier")

        reporting_org_elem = activity_element.find("reporting-org")
        if reporting_org_elem is not None:
            narrative = reporting_org_elem.find("narrative")
            if narrative is not None:
                self.reporting_org = narrative.text

        title_elem = activity_element.find("title")
        if title_elem is not None:
            narrative = title_elem.find("narrative")
            if narrative is not None:
                self.title = narrative.text

        desc_elem = activity_element.find("description")
        if desc_elem is not None:
            narrative = desc_elem.find("narrative")
            if narrative is not None:
                self.description = narrative.text

        status_elem = activity_element.find("activity-status")
        if status_elem is not None:
            self.status = status_elem.get("code")

        start_date_elem = activity_element.find('activity-date[@type="1"]')
        if start_date_elem is not None:
            self.start_date = start_date_elem.get("iso-date")

        end_date_elem = activity_element.find('activity-date[@type="2"]')
        if end_date_elem is not None:
            self.end_date = end_date_elem.get("iso-date")

        budget_elem = activity_element.find("budget")
        if budget_elem is not None:
            self.budget = budget_elem.find("value").text

        for org_elem in activity_element.findall("participating-org"):
            self.participating_orgs.append(org_elem.text)

        for country_elem in activity_element.findall("recipient-country"):
            country_code = country_elem.get("code")
            try:
                country = pycountry.countries.get(alpha_2=country_code)
                country_name = country.name if country else country_code
            except AttributeError:
                country_name = country_code
            self.recipient_countries.append(country_name)

        for sector_elem in activity_element.findall("sector"):
            self.sectors.append(sector_elem.get("code"))

        for transaction_elem in activity_element.findall("transaction"):
            transaction = {
                "type": transaction_elem.find("transaction-type").get("code"),
                "date": transaction_elem.find("transaction-date").get("iso-date"),
                "value": transaction_elem.find("value").text,
            }
            self.transactions.append(transaction)

        # Create a dict to keep only the latest transaction per date
        daily_transactions = {}
        for t in self.transactions:
            if t["value"] is not None:
            date = t["date"]
            if date not in daily_transactions:
                daily_transactions[date] = float(t["value"])
            else:
                daily_transactions[date] += float(t["value"])
        
        self.total_transaction_value = sum(daily_transactions.values())

    def __str__(self):
        return f"IATI Activity: {self.identifier} - {self.title}"
