# Calculate and store explainable risk scores for synthetic abuse reports.

import sqlite3


DATABASE_FILE = "abuseflow.db"


# Connect to the local SQLite database.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()


# Read reports and count other reports that use the same URL.
cursor.execute(
    """
    SELECT
        report_id,
        url,
        account_age_days,
        COUNT(*) OVER (PARTITION BY url) AS url_report_count
    FROM reported_urls
    ORDER BY report_id
    """
)

reports = cursor.fetchall()


# Calculate a score and save it for every report.
for report_id, url, account_age_days, url_report_count in reports:
    score = 0
    reasons = []

    if url_report_count > 1:
        score += 40
        reasons.append("URL reported more than once (+40)")

    if account_age_days < 7:
        score += 15
        reasons.append("New account under 7 days old (+15)")

    if score >= 55:
        priority = "HIGH"
    else:
        priority = "LOW"

    cursor.execute(
        """
        UPDATE reported_urls
        SET risk_score = ?, priority = ?
        WHERE report_id = ?
        """,
        (score, priority, report_id),
    )

    evidence = "; ".join(reasons) if reasons else "No risk signals"

    print(f"{report_id}: {priority} risk | score={score}")
    print(f"  URL: {url}")
    print(f"  Evidence: {evidence}")


# Save all updates first, then close the database.
connection.commit()
connection.close()