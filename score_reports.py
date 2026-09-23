# Calculate and store explainable risk scores for synthetic abuse reports.

import sqlite3


DATABASE_FILE = "abuseflow.db"
URLHAUS_MATCH_POINTS = 40


# Connect to the local SQLite database.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()


# Read every report, count repeated URLs, and include URLHaus evidence.
# LEFT JOIN keeps reports even if they do not have URLHaus enrichment yet.
cursor.execute("""
    SELECT
        reported_urls.report_id,
        reported_urls.url,
        reported_urls.account_age_days,
        COUNT(*) OVER (
            PARTITION BY reported_urls.url
        ) AS url_report_count,
        url_enrichments.found AS urlhaus_found,
        url_enrichments.url_status AS urlhaus_status
    FROM reported_urls
    LEFT JOIN url_enrichments
        ON reported_urls.report_id = url_enrichments.report_id
        AND url_enrichments.provider = 'urlhaus'
    ORDER BY reported_urls.report_id
""")

reports = cursor.fetchall()


# Calculate a score and save it for every report.
for report_id, url, account_age_days, url_report_count, urlhaus_found, urlhaus_status in reports:
    score = 0
    reasons = []

    # Internal signal: the same URL was reported more than once.
    if url_report_count > 1:
        score += 40
        reasons.append("URL reported more than once (+40)")

    # Internal signal: the related account is very new.
    if account_age_days < 7:
        score += 15
        reasons.append("New account under 7 days old (+15)")

    # External signal: URLHaus confirms the URL is in its dataset.
    # A no-results response adds no points and does not mean the URL is safe.
    if urlhaus_found == 1:
        score += URLHAUS_MATCH_POINTS

        if urlhaus_status:
            reasons.append(
                f"URLHaus match: {urlhaus_status} (+{URLHAUS_MATCH_POINTS})"
            )
        else:
            reasons.append(
                f"URLHaus match (+{URLHAUS_MATCH_POINTS})"
            )

    # Choose a review priority from the total score.
    if score >= 55:
        priority = "HIGH"
    else:
        priority = "LOW"

    # Turn the reasons list into one readable database value.
    evidence = "; ".join(reasons) if reasons else "No risk signals"

    # Save score, priority, and explanation for the analyst queue.
    cursor.execute("""
        UPDATE reported_urls
        SET risk_score = ?, priority = ?, risk_reasons = ?
        WHERE report_id = ?
    """, (score, priority, evidence, report_id))

    # Print a readable result in the terminal.
    print(f"{report_id}: {priority} risk | score={score}")
    print(f"  URL: {url}")
    print(f"  Evidence: {evidence}")


# Save all updates, then close the database connection.
connection.commit()
connection.close()