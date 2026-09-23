# Export the scored AbuseFlow review queue to a CSV file.

import csv
import sqlite3


DATABASE_FILE = "abuseflow.db"
OUTPUT_FILE = "data/review_queue.csv"


# Read the saved risk scores from SQLite.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        report_id,
        url,
        reported_at,
        reporter_type,
        account_age_days,
        risk_score,
        priority
    FROM reported_urls
    ORDER BY risk_score DESC, report_id ASC
    """
)

rows = cursor.fetchall()
connection.close()


# Define the CSV column names and their output order.
fieldnames = [
    "report_id",
    "url",
    "reported_at",
    "reporter_type",
    "account_age_days",
    "risk_score",
    "priority",
]


# Write the query results to a review-queue CSV file.
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as output_file:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)

    writer.writeheader()

    for row in rows:
        writer.writerow(
            {
                "report_id": row[0],
                "url": row[1],
                "reported_at": row[2],
                "reporter_type": row[3],
                "account_age_days": row[4],
                "risk_score": row[5],
                "priority": row[6],
            }
        )


print(f"Exported {len(rows)} reports to {OUTPUT_FILE}")