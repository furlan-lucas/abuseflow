# Export the scored AbuseFlow review queue to a CSV file.

import csv
import sqlite3


DATABASE_FILE = "abuseflow.db"
OUTPUT_FILE = "data/review_queue.csv"


# Connect to the local SQLite database.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()


# Read reports plus any URLHaus enrichment.
# LEFT JOIN keeps reports that have not been enriched yet.
cursor.execute("""
    SELECT
        reported_urls.report_id,
        reported_urls.url,
        reported_urls.reported_at,
        reported_urls.reporter_type,
        reported_urls.account_age_days,
        reported_urls.risk_score,
        reported_urls.priority,
        reported_urls.risk_reasons,
        url_enrichments.found,
        url_enrichments.url_status,
        url_enrichments.tags_json,
        url_enrichments.queried_at,
        url_enrichments.error_message
    FROM reported_urls
    LEFT JOIN url_enrichments
        ON reported_urls.report_id = url_enrichments.report_id
        AND url_enrichments.provider = 'urlhaus'
    ORDER BY reported_urls.risk_score DESC, reported_urls.report_id ASC
""")

rows = cursor.fetchall()
connection.close()


# Define the CSV columns and their order.
fieldnames = [
    "report_id",
    "url",
    "reported_at",
    "reporter_type",
    "account_age_days",
    "risk_score",
    "priority",
    "risk_reasons",
    "urlhaus_found",
    "urlhaus_status",
    "urlhaus_tags",
    "urlhaus_queried_at",
    "urlhaus_error",
]


# Write the analyst review queue to CSV.
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as output_file:
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)

    writer.writeheader()

    for row in rows:
        # A database value of 1 means URLHaus found a record.
        # 0 means a successful lookup had no matching record.
        # None means the report has not been enriched yet.
        if row[8] == 1:
            urlhaus_found = "Yes"
        elif row[8] == 0:
            urlhaus_found = "No"
        else:
            urlhaus_found = "Not enriched"

        writer.writerow(
            {
                "report_id": row[0],
                "url": row[1],
                "reported_at": row[2],
                "reporter_type": row[3],
                "account_age_days": row[4],
                "risk_score": row[5],
                "priority": row[6],
                "risk_reasons": row[7],
                "urlhaus_found": urlhaus_found,
                "urlhaus_status": row[9] or "",
                "urlhaus_tags": row[10] or "",
                "urlhaus_queried_at": row[11] or "",
                "urlhaus_error": row[12] or "",
            }
        )


print(f"Exported {len(rows)} reports to {OUTPUT_FILE}")