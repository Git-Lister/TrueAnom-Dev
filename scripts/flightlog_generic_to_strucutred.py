import csv
from pathlib import Path

GENERIC_CSV = Path("data/extracted/tables/flight_logs/doj_maxwell_flight_log1_table1.csv")
STRUCTURED_CSV = Path("data/extracted/tables/flight_logs/doj_maxwell_flight_log1_structured.csv")

HEADERS = [
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


def main():
    rows_out = []

    with GENERIC_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for raw in reader:
            cells = [c.strip() for c in raw]
            cells += [""] * (8 - len(cells))

            date = cells[0]
            aircraft_make_model = cells[1]
            aircraft_id = cells[2]
            origin = cells[3]
            destination = cells[4]
            miles_flown = cells[5]
            flight_no = cells[6]
            remarks = cells[7] if len(cells) > 7 else ""

            if not any([date, aircraft_id, origin, destination, miles_flown, flight_no, remarks]):
                continue

            rows_out.append([
                date,
                "",  # time
                aircraft_make_model,
                aircraft_id,
                origin,
                destination,
                miles_flown,
                flight_no,
                remarks,
                "",  # landings
                "",  # aircraft_category
            ])

    STRUCTURED_CSV.parent.mkdir(parents=True, exist_ok=True)
    with STRUCTURED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(rows_out)

    print(f"Wrote structured CSV with {len(rows_out)} rows to {STRUCTURED_CSV}")


if __name__ == "__main__":
    main()
