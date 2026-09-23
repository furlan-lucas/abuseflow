# Load synthetic CSV reports into the local SQLite database.

import csv
import sqlite3


# Define where the CSV input and SQLite database are located.
CSV_FILE = "data/reported_urls.csv"
DATABASE_FILE = "abuseflow.db"


# Read the synthetic report rows from the CSV file.
with open(CSV_FILE, "r", encoding="utf-8") as input_file:
    reader = csv.DictReader(input_file)
    reports = list(reader)


# Connect to the existing SQLite database.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()


# Add every CSV report to the reported_urls table.
for report in reports:
    cursor.execute(
        """
        INSERT INTO reported_urls (
            report_id,
            url,
            reported_at,
            reporter_type,
            account_age_days
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(report_id) DO NOTHING
        """,
        (
            report["report_id"],
            report["url"],
            report["reported_at"],
            report["reporter_type"],
            int(report["account_age_days"]),
        ),
    )


# Save all inserted records.
connection.commit()


# Count how many records exist after loading.
cursor.execute("SELECT COUNT(*) FROM reported_urls")
report_count = cursor.fetchone()[0]


# Close the database connection.
connection.close()


print(f"Database now contains {report_count} report records.")
