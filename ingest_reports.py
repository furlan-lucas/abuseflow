# Read synthetic URL reports and identify repeated reports.

import csv
from collections import Counter


# This is the path to our input data file.
CSV_FILE = "data/reported_urls.csv"


# Open the CSV file so Python can read it.
with open(CSV_FILE, "r", encoding="utf-8") as input_file:
    # DictReader uses the header row as keys for each report.
    reader = csv.DictReader(input_file)

    # Read every report row into a list.
    reports = list(reader)


# Collect each URL from the report records.
urls = [report["url"] for report in reports]


# Count how many times each URL appears.
url_report_counts = Counter(urls)


# Print the total number of reports.
print(f"Loaded {len(reports)} synthetic abuse reports.")


# Print each report and its number of matching reports.
for report in reports:
    url = report["url"]
    report_count = url_report_counts[url]

    print(
        f"{report['report_id']}: "
        f"{url} "
        f"(reported {report_count} time(s))"
    )