# Add columns for stored risk-scoring results.

import sqlite3


DATABASE_FILE = "abuseflow.db"


# Connect to the existing database.
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()


# Add a column for the numeric risk score.
try:
    cursor.execute(
        """
        ALTER TABLE reported_urls
        ADD COLUMN risk_score INTEGER
        """
    )
except sqlite3.OperationalError:
    print("risk_score column already exists.")


# Add a column for the review priority.
try:
    cursor.execute(
        """
        ALTER TABLE reported_urls
        ADD COLUMN priority TEXT
        """
    )
except sqlite3.OperationalError:
    print("priority column already exists.")


# Save schema changes and close the database.
connection.commit()
connection.close()


print("Risk-score columns are ready.")