# reuse_urlhaus_cache.py
# This script copies a fresh URLHaus result to HIGH-priority reports
# that have the same normalized URL.

import sqlite3
from datetime import datetime, timezone

from url_utils import normalize_url


DATABASE_PATH = "abuseflow.db"
PROVIDER = "urlhaus"


# Connect to the SQLite database.
connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

# Get all HIGH-priority reports.
cursor.execute("""
    SELECT report_id, url
    FROM reported_urls
    WHERE priority = ?
""", ("HIGH",))

high_priority_reports = cursor.fetchall()

# Current time in UTC, used to check whether cached results are still fresh.
now = datetime.now(timezone.utc)

copied_count = 0

# Look at one high-priority report at a time.
for report_id, url in high_priority_reports:

    # Normalize this report's URL.
    normalized_url = normalize_url(url)

    # Look for a fresh URLHaus record from any report
    # with the same normalized URL.
    cursor.execute("""
        SELECT
            lookup_key,
            found,
            url_status,
            tags_json,
            detection_count,
            queried_at,
            expires_at,
            error_message,
            raw_response_json
        FROM url_enrichments
        WHERE provider = ?
          AND normalized_url = ?
        ORDER BY queried_at DESC
        LIMIT 1
    """, (PROVIDER, normalized_url))

    source_cache = cursor.fetchone()

    # If there is no matching cached record, skip this report.
    if source_cache is None:
        print("No existing cache found for:", report_id)
        continue

    # Read the saved expiration time.
    expires_at = datetime.fromisoformat(source_cache[6])

    # If the record is expired, do not reuse it.
    if expires_at <= now:
        print("Cache is expired for:", report_id)
        continue

    # Save the same evidence for this report.
    cursor.execute("""
        INSERT INTO url_enrichments (
            report_id,
            provider,
            normalized_url,
            lookup_key,
            found,
            url_status,
            tags_json,
            detection_count,
            queried_at,
            expires_at,
            error_message,
            raw_response_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(report_id, provider) DO UPDATE SET
            normalized_url = excluded.normalized_url,
            lookup_key = excluded.lookup_key,
            found = excluded.found,
            url_status = excluded.url_status,
            tags_json = excluded.tags_json,
            detection_count = excluded.detection_count,
            queried_at = excluded.queried_at,
            expires_at = excluded.expires_at,
            error_message = excluded.error_message,
            raw_response_json = excluded.raw_response_json
    """, (
        report_id,
        PROVIDER,
        normalized_url,
        source_cache[0],
        source_cache[1],
        source_cache[2],
        source_cache[3],
        source_cache[4],
        source_cache[5],
        source_cache[6],
        source_cache[7],
        source_cache[8],
    ))

    copied_count += 1
    print("Fresh URLHaus evidence saved for:", report_id)

# Make the database changes permanent.
connection.commit()
connection.close()

print("Reports updated:", copied_count)