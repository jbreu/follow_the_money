from activity import Activity
import pdfplumber


def read_demokratieleben1_activities(pdf_file_path):
    activities = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages[110:134]:
            tables = page.extract_tables()
            for table in tables:
                print(
                    f"Processing table {tables.index(table) + 1} on page {pdf.pages.index(page) + 1}"
                )

                if "Träger" not in table[0][0]:
                    continue

                for row in table[1:]:
                    activity = DemokratieLeben1()
                    if activity.from_pdf_table_row(row):
                        activities.append(activity)

    return activities


class DemokratieLeben1(Activity):
    def __init__(self):
        super().__init__()

    def from_pdf_table_row(self, row):
        self.recipient_countries.append("Germany")
        self.reporting_org = (
            "Bundesministerium für Familie, Senioren, Frauen und Jugend (BMFSFJ)"
        )

        self.recipient_organization = (
            row[0].strip().replace("\n", " ").replace("\r", " ")
        )
        self.title = row[1].strip().replace("\n", " ").replace("\r", " ")

        self.identifier = self.recipient_organization + self.title + " Demokratieleben1"

        self.recipient_is_owned_by_german_federal_government = False

        self.transactions = []

        for i in range(0, len(row) - 2):
            if row[2 + i] != "":
                self.transactions.append(
                    {
                        "type": "Fördersumme",
                        "date": str(2015 + 5 - (len(row) - 2) + i),
                        "value": int(
                            row[2 + i]
                            .replace(".", "")
                            .replace(",", "")
                            .replace(" €", "")
                        ),
                    }
                )

        # Set start and end dates based on transaction dates
        transaction_dates = [t["date"] for t in self.transactions]
        if transaction_dates:
            self.start_date = min(transaction_dates)
            if len(transaction_dates) > 1:
                self.end_date = max(transaction_dates)

        self.total_transaction_value = sum([t["value"] for t in self.transactions])

        return True
