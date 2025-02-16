from activity import Activity
import pdfplumber


def read_kleine_anfrage2003843_activities(pdf_file_path):
    activities = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                print(
                    f"Processing table {tables.index(table) + 1} on page {pdf.pages.index(page) + 1}"
                )
                for row in table:
                    activity = KleineAnfrage2003843()
                    if activity.from_pdf_table_row(row) is not None:
                        activities.append(activity)

    return activities


class KleineAnfrage2003843(Activity):
    def __init__(self):
        super().__init__()

    def from_pdf_table_row(self, row):
        if row[0] == "" or "Abkürzung" in row[0]:
            return None

        self.recipient_countries.append("Germany")
        self.reporting_org = row[0]
        self.identifier = row[1] + " " + row[2] + " " + row[3]
        self.recipient_organization = (row[2] + " " + row[3]).strip()
        self.title = row[4]
        self.legal_basis = "Haushaltstitel " + row[4]

        self.start_date = "2021" if row[5] else None
        self.end_date = "2022" if row[6] else None

        self.transactions = []
        if row[5] and row[5] != "-":
            value_2021 = float(str(row[5]).replace(".", ""))
            self.transactions.append(
                {
                    "type": "Spending",
                    "date": "2021",
                    "value": value_2021 * 1000,
                }
            )

        if row[6] and row[6] != "-":
            value_2022 = float(str(row[6]).replace(".", ""))
            self.transactions.append(
                {
                    "type": "Spending",
                    "date": "2022",
                    "value": value_2022 * 1000,
                }
            )

        # Map abbreviations to full names
        org_mapping = {
            "AA": "Auswärtiges Amt (AA)",
            "BMAS": "Bundesministerium für Arbeit und Soziales (BMAS)",
            "BMBF": "Bundesministerium für Bildung und Forschung (BMBF)",
            "BMEL": "Bundesministerium für Ernährung und Landwirtschaft (BMEL)",
            "BMFSFJ": "Bundesministerium für Familie, Senioren, Frauen und Jugend (BMFSFJ)",
            "BMG": "Bundesministerium für Gesundheit (BMG)",
            "BMJ": "Bundesministerium der Justiz (BMJ)",
            "BMUV": "Bundesministerium für Umwelt, Naturschutz, nukleare Sicherheit und Verbraucherschutz (BMUV)",
            "BMVg": "Bundesministerium der Verteidigung (BMVg)",
            "BMWK": "Bundesministerium für Wirtschaft und Klimaschutz (BMWK)",
            "BMI": "Bundesministerium des Innern und für Heimat (BMI)",
            "BMZ": "Bundesministerium für wirtschaftliche Zusammenarbeit und Entwicklung (BMZ)",
            "BT": "Deutscher Bundestag (BT)",
            "BKAmt/IntB": "Bundeskanzleramt/Internationale Beziehungen (BKAmt/IntB)",
            "BpB": "Bundeszentrale für politische Bildung (BpB)",
            "BMUV/BMWK": "Bundesministerium für Umwelt, Naturschutz, nukleare Sicherheit und Verbraucherschutz (BMUV)/Bundesministerium für Wirtschaft und Klimaschutz (BMWK)",
        }
        self.reporting_org = org_mapping.get(row[0])

        self.total_transaction_value = sum([t["value"] for t in self.transactions])

        return True
