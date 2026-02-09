import csv
from pathlib import Path

# Adjust if needed
OUTPUT = Path("data/extracted/tables/flight_logs/doj_maxwell_flight_log1_table1.csv")

# For now, start with an empty CSV with headers only.
# Later you can plug in table-extraction logic or paste rows.
headers = [
    "date",
    "time",
    "aircraft_make_model",
    "aircraft_id",
    "origin",
    "destination",
    "miles_flown",
    "flight_no",
    "remarks",
    "landings",
    "aircraft_category",
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

print(f"Wrote empty CSV with headers to {OUTPUT}")
