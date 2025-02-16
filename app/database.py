import sqlite3
from contextlib import contextmanager
from tqdm import tqdm

DATABASE_PATH = "app/activities.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS activities (
            iati_identifier TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            reporting_org TEXT,
            total_transaction_value REAL,
            recipient_countries TEXT,
            recipient_organization TEXT,
            recipient_is_owned_by_german_federal_government BOOLEAN,
            legal_basis TEXT,
            type_of_grant TEXT
        )
        """
        )
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id TEXT,
            type TEXT,
            date TEXT,
            value REAL,
            FOREIGN KEY (activity_id) REFERENCES activities (iati_identifier)
        )
        """
        )
        conn.commit()


def _insert_activity(conn, activity):
    conn.execute(
        """
    INSERT OR REPLACE INTO activities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            activity.identifier,
            activity.title,
            activity.description,
            activity.start_date,
            activity.end_date,
            activity.reporting_org,
            activity.total_transaction_value,
            (
                ",".join(activity.recipient_countries)
                if activity.recipient_countries
                else None
            ),
            activity.recipient_organization,
            activity.recipient_is_owned_by_german_federal_government,
            activity.legal_basis,
            activity.type_of_grant,
        ),
    )

    # Insert transactions
    conn.execute(
        "DELETE FROM transactions WHERE activity_id = ?", (activity.identifier,)
    )
    for transaction in activity.transactions:
        if transaction["value"] is not None:
            conn.execute(
                """
                INSERT INTO transactions (activity_id, type, date, value)
                VALUES (?, ?, ?, ?)
                """,
                (
                    activity.identifier,
                    transaction["type"],
                    transaction["date"],
                    float(transaction["value"]),
                ),
            )


def insert_activity(activity):
    with get_db() as conn:
        _insert_activity(conn, activity)
        conn.commit()


def batch_insert_activities(activities):
    with get_db() as conn:
        for activity in tqdm(activities, desc="Inserting activities"):
            _insert_activity(conn, activity)
        conn.commit()


def get_filtered_activities(
    year=None,
    organization=None,
    min_value=None,
    max_value=None,
    country=None,
    search=None,
    recipient_organization=None,
):
    conditions = []
    params = []

    if search:
        conditions.append(
            "(title LIKE ? OR recipient_organization LIKE ? OR legal_basis LIKE ?)"
        )
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if year:
        conditions.append("start_date LIKE ?")
        params.append(f"{year}%")
    if organization:
        conditions.append("reporting_org LIKE ?")
        params.append(f"%{organization}%")
    if min_value:
        conditions.append("total_transaction_value >= ?")
        params.append(float(min_value))
    if max_value:
        conditions.append("total_transaction_value <= ?")
        params.append(float(max_value))
    if country:
        conditions.append("recipient_countries LIKE ?")
        params.append(f"%{country}%")
    if recipient_organization:
        conditions.append("recipient_organization LIKE ?")
        params.append(f"%{recipient_organization}%")

    where_clause = " AND ".join(conditions) if conditions else "1"

    with get_db() as conn:
        return conn.execute(
            f"""
            SELECT * FROM activities 
            WHERE {where_clause}
            ORDER BY total_transaction_value DESC
        """,
            params,
        ).fetchall()


def get_metadata():
    with get_db() as conn:
        years = conn.execute(
            """
            SELECT DISTINCT substr(start_date, 1, 4) as year 
            FROM activities 
            WHERE start_date IS NOT NULL
            ORDER BY year DESC
        """
        ).fetchall()

        orgs = conn.execute(
            """
            SELECT DISTINCT reporting_org 
            FROM activities 
            WHERE reporting_org IS NOT NULL
            ORDER BY reporting_org ASC
        """
        ).fetchall()

        countries = conn.execute(
            """
            SELECT DISTINCT recipient_countries 
            FROM activities 
            WHERE recipient_countries IS NOT NULL
            ORDER BY recipient_countries ASC
        """
        ).fetchall()

        recipient_orgs = conn.execute(
            """
            SELECT DISTINCT recipient_organization 
            FROM activities 
            WHERE recipient_organization IS NOT NULL
            ORDER BY recipient_organization ASC
        """
        ).fetchall()

        return {
            "years": [r["year"] for r in years],
            "organizations": [r["reporting_org"] for r in orgs],
            "countries": [c["recipient_countries"] for c in countries],
            "recipient_organizations": [
                r["recipient_organization"] for r in recipient_orgs
            ],
        }


def get_activity_transactions(activity_id):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT type, date, value
            FROM transactions
            WHERE activity_id = ?
            ORDER BY date
            """,
            (activity_id,),
        ).fetchall()
