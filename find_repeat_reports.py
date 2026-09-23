# Find URLs that appear in more than one synthetic abuse report.

import sqlite3


# Connect to the local AbuseFlow database.
connection = sqlite3.connect("abuseflow.db")
cursor = connection.cursor()


# GROUP BY puts matching URLs together.
# COUNT(*) counts how many reports each URL has.
# HAVING keeps only URLs reported more than once.
cursor.execute(
    """
    SELECT
        url,
        COUNT(*) AS report_count
    FROM reported_urls
    GROUP BY url
    HAVING COUNT(*) > 1
    ORDER BY report_count DESC
    """
)


# Get all matching database rows.
repeat_urls = cursor.fetchall()


# Close the connection after the query is complete.
connection.close()


# Print the results.
print(f"Found {len(repeat_urls)} URL(s) reported more than once.")

for url, report_count in repeat_urls:
    print(f"{url} -> {report_count} reports")
