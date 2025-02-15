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

        transaction_type_map = {
            "1": "Incoming Funds",
            "2": "Outgoing Commitment",
            "3": "Disbursement",
            "4": "Expenditure",
            "5": "Interest Payment",
            "6": "Loan Repayment",
            "7": "Reimbursement",
            "8": "Purchase of Equity",
            "9": "Sale of Equity",
            "10": "Credit Guarantee",
            "11": "Incoming Commitment",
        }

        for transaction_elem in activity_element.findall("transaction"):
            type_code = transaction_elem.find("transaction-type").get("code")
            transaction = {
                "type": transaction_type_map.get(type_code, type_code),
                "date": transaction_elem.find("transaction-date").get("iso-date"),
                "value": transaction_elem.find("value").text,
            }
            self.transactions.append(transaction)

        # Create a dict to keep only the latest transaction per date
        daily_transactions = {}
        for t in self.transactions:
            if t["value"] is not None and t["type"] != "Outgoing Commitment":
                date = t["date"]
                daily_transactions[date] = float(t["value"])

        self.total_transaction_value = sum(daily_transactions.values())

        # Set start and end dates based on transaction dates
        transaction_dates = [
            t["date"]
            for t in self.transactions
            if t["date"] is not None and t["type"] != "Outgoing Commitment"
        ]
        if transaction_dates:
            self.start_date = min(transaction_dates)
            if len(transaction_dates) > 1:
                self.end_date = max(transaction_dates)

    def __str__(self):
        return f"IATI Activity: {self.identifier} - {self.title}"
