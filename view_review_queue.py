# Display the review queue stored in the SQLite database.

import sqlite3


DATABASE_FILE = "abuseflow.db"


# Connect to the database and create a cursor for the query.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()


# Show highest-risk reports first.
cursor.execute(
    """
    SELECT
        report_id,
        url,
        risk_score,
        priority
    FROM reported_urls
    ORDER BY risk_score DESC, report_id ASC
    """
)

queue = cursor.fetchall()


# Close the database after retrieving the results.
connection.close()


# Print the stored queue.
print("AbuseFlow review queue:")

for report_id, url, risk_score, priority in queue:
    print(f"{priority} | score={risk_score} | {report_id} | {url}")