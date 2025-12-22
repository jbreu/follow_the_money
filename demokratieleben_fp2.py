from activity import Activity
import pdfplumber


def read_fp2_activities(pdf_file_path, start_page=None, end_page=None):
    activities = []
    with pdfplumber.open(pdf_file_path) as pdf:
        pages = pdf.pages
        sp = start_page or 0
        ep = end_page or len(pages)
        for page in pages[sp:ep]:
            tables = page.extract_tables()
            for table in tables:
                # look for a header containing typical column identifiers
                header = table[0][0] if table and table[0] and table[0][0] else ""

                first_data_row = 1 if "Zuwendungsempfänger" in header else 0

                for row in table[first_data_row:]:
                    activity = FP2Activity()
                    if activity.from_pdf_table_row(row):
                        activities.append(activity)

    return activities


class FP2Activity(Activity):
    def __init__(self):
        super().__init__()

    def from_pdf_table_row(self, row):
        try:
            self.recipient_countries.append("Germany")
            self.reporting_org = (
                "Bundesministerium für Familie, Senioren, Frauen und Jugend (BMFSFJ)"
            )

            # first column: recipient organization / project carrier
            if len(row) < 8:
                self.recipient_organization = (
                    row[0].strip().replace("\n", " ").replace("\r", " ")
                )
            else:
                self.recipient_organization = (
                    row[1].strip().replace("\n", " ").replace("\r", " ")
                )

            # second column: project / title
            if len(row) >= 8:
                self.title = row[2].strip().replace("\n", " ").replace("\r", " ")
                self.identifier = (
                    self.recipient_organization + self.title + " Demokratieleben FP2"
                )
            elif len(row) == 7:
                self.title = row[1].strip().replace("\n", " ").replace("\r", " ")

                self.identifier = (
                    self.recipient_organization + self.title + " Demokratieleben FP2"
                )
            elif len(row) == 6:
                self.identifier = (
                    self.recipient_organization + self.title + " Demokratieleben FP2"
                )

                self.title = "Demokratie leben! Förderperiode 2"

            self.recipient_is_owned_by_german_federal_government = False

            self.transactions = []

            # following numeric columns are treated as yearly funding amounts
            for i in range(0, len(row) - 2):
                cell = row[2 + i]
                if cell is None:
                    continue
                cell = cell.strip()
                if cell != "":
                    try:
                        # remove thousand separators and euro symbol
                        clean = cell.replace(".", "")
                        clean = clean.replace(
                            ",", "."
                        )  # convert decimal comma to point for later float conversion
                        clean = clean.replace(" €", "")
                        value = float(clean)
                    except Exception:
                        # skip non-numeric cells
                        continue
                    self.transactions.append(
                        {
                            "type": "Fördersumme",
                            "date": str(2020 + i),
                            "value": value,
                        }
                    )

            transaction_dates = [t["date"] for t in self.transactions]
            if transaction_dates:
                self.start_date = min(transaction_dates)
                if len(transaction_dates) > 1:
                    self.end_date = max(transaction_dates)

            self.total_transaction_value = sum([t["value"] for t in self.transactions])

            return True
        except Exception:
            return False
