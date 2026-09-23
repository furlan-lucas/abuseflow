# Create a local SQLite database for synthetic abuse reports.

import sqlite3


# This file will be created in the project folder.
DATABASE_FILE = "abuseflow.db"


# Connect creates the database file if it does not exist.
connection = sqlite3.connect(DATABASE_FILE)


# A cursor sends SQL commands to the database.
cursor = connection.cursor()


# Create a table to store one row for each synthetic report.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS reported_urls (
        report_id TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        reported_at TEXT NOT NULL,
        reporter_type TEXT NOT NULL,
        account_age_days INTEGER NOT NULL
    )
    """
)


# Save the table creation.
connection.commit()


# Close the database connection cleanly.
connection.close()


print(f"Database setup complete: {DATABASE_FILE}")