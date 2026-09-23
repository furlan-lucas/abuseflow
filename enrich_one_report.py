# enrich_one_report.py
# This script enriches one report from the database with URLHaus.

import json
import sqlite3
from datetime import datetime, timedelta, timezone

from url_utils import create_lookup_key
from urlhaus_client import lookup_urlhaus
from datetime import datetime, timedelta, timezone

DATABASE_PATH = "abuseflow.db"
CACHE_HOURS = 24


# Step 1: Connect to the database.
connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


# Step 2: Get one report.
cursor.execute("""
    SELECT report_id, url
    FROM reported_urls
    ORDER BY reported_at
    LIMIT 1
""")

report = cursor.fetchone()

if report is None:
    connection.close()
    raise ValueError("No reports were found in reported_urls.")

report_id = report[0]
url = report[1]

# Check whether this report already has a fresh URLHaus result.
cursor.execute("""
    SELECT found, url_status, tags_json, error_message, expires_at
    FROM url_enrichments
    WHERE report_id = ? AND provider = ?
""", (report_id, "urlhaus"))

cached_row = cursor.fetchone()

# Get the current time in UTC.
now = datetime.now(timezone.utc)

# Use the cache only when a saved result exists and has not expired.
if cached_row is not None:
    cached_expires_at = datetime.fromisoformat(cached_row[4])

    if cached_expires_at > now:
        print("Using fresh cached URLHaus result for:", report_id)

        # Build the same evidence dictionary the API client would return.
        # json.loads changes saved JSON text back into a Python list.
        evidence = {
            "provider": "urlhaus",
            "normalized_url": url,
            "found": bool(cached_row[0]),
            "url_status": cached_row[1],
            "tags": json.loads(cached_row[2]),
            "error_message": cached_row[3]
        }

    else:
        # Cache exists but is too old, so request fresh evidence.
        evidence = lookup_urlhaus(url)

else:
    # No cache entry exists, so request fresh evidence.
    evidence = lookup_urlhaus(url)


# The client already normalized the URL for us.
normalized_url = evidence["normalized_url"]

# Make a consistent cache key from the normalized URL.
lookup_key = create_lookup_key(normalized_url)


# Step 4: Set the cache timestamps.
queried_at = datetime.now(timezone.utc)
expires_at = queried_at + timedelta(hours=CACHE_HOURS)


# Step 5: Convert the tags list and evidence dictionary into JSON text.
# SQLite stores text, not Python lists or dictionaries.
tags_json = json.dumps(evidence["tags"])
raw_response_json = json.dumps(evidence)


# Step 6: Save the enrichment result.
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
    evidence["provider"],
    normalized_url,
    lookup_key,
    int(evidence["found"]),
    evidence["url_status"],
    tags_json,
    0,
    queried_at.isoformat(),
    expires_at.isoformat(),
    evidence["error_message"],
    raw_response_json
))


# Step 7: Commit saves the new record permanently.
connection.commit()


# Step 8: Print a short, safe result summary.
print("Enriched report:", report_id)
print("Provider:", evidence["provider"])
print("Found in URLHaus:", evidence["found"])
print("URLHaus status:", evidence["url_status"])
print("Error:", evidence["error_message"])


# Step 9: Close the database connection.
connection.close()