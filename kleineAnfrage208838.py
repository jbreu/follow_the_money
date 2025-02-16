from activity import Activity


class KleineAnfrage208838(Activity):
    def __init__(self):
        super().__init__()

    def from_pdf_table_row(self, row, year=2023):
        if year == 2023 and len(row) != 10 or (row[5] is None and row[6] is None):
            return None

        if year == 2024 and len(row) != 9 or (row[5] is None):
            return None

        if row[2] == "nicht einschlägig":
            row[2] = ""

        self.recipient_countries.append("Germany")
        self.reporting_org = row[0]
        self.identifier = row[1] + " " + row[2] + row[3]
        self.recipient_organization = row[2] + row[3]
        self.title = "Förderung nach " + row[4]
        self.recipient_is_owned_by_german_federal_government = (
            bool(row[2]) and row[2] != "nicht einschlägig"
        )
        self.legal_basis = row[4]

        if year == 2023:
            self.type_of_grant = row[7]
            self.start_date = row[8]
            self.end_date = row[9]

            self.transactions = []
            if row[5] and row[5] != "-":
                value_2022 = float(str(row[5]).replace(".", ""))
                self.transactions.append(
                    {
                        "type": "Spending",
                        "date": "2022",
                        "value": value_2022 * 1000,
                    }
                )

            if row[6] and row[6] != "-":
                value_2023 = float(str(row[6]).replace(".", ""))
                self.transactions.append(
                    {
                        "type": "Spending",
                        "date": "2023",
                        "value": value_2023 * 1000,
                    }
                )

            # edge case: it seems the values in those lines are meant in Euros, not thousands of Euros as in the other lines
            if row[0] == "AA" and row[1] == "05":
                for t in self.transactions:
                    t["value"] = t["value"] / 1000

        if year == 2024:
            self.type_of_grant = row[6]
            self.start_date = row[7]
            self.end_date = row[8]

            self.transactions = []
            if row[5] and row[5] != "-":
                try:
                    value_2024 = float(str(row[5]).replace(".", ""))
                except ValueError:
                    value_2024 = 0
                self.transactions.append(
                    {
                        "type": "Planned",
                        "date": "2024",
                        "value": value_2024 * 1000,
                    }
                )

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
        }
        self.reporting_org = org_mapping.get(row[0])

        self.total_transaction_value = sum([t["value"] for t in self.transactions])

        return True
