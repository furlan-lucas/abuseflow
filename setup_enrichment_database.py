import sqlite3

DATABASE_PATH = "abuseflow.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS url_enrichments (
    enrichment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    lookup_key TEXT NOT NULL,
    found INTEGER NOT NULL DEFAULT 0,
    url_status TEXT,
    tags_json TEXT,
    detection_count INTEGER NOT NULL DEFAULT 0,
    queried_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    error_message TEXT,
    raw_response_json TEXT,
    FOREIGN KEY (report_id) REFERENCES reported_urls(report_id),
    UNIQUE (report_id, provider)
)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_url_enrichments_lookup
ON url_enrichments (provider, lookup_key)
""")

connection.commit()
connection.close()

print("URL enrichment cache table is ready.")