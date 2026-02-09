# backend/app/ingestion/flight_logs_structured.py

import csv
from datetime import datetime, date, time as dt_time
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.db.schema import Event


FLIGHT_LOGS_DIR = Path("data/extracted/tables/flight_logs")


def parse_date(date_str: str) -> Optional[date]:
    """Parse a date string into a date object, or return None."""
    if not date_str:
        return None

    # Try a couple of common formats; extend as needed
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue

    # If nothing works, you can log/print and skip
    # print(f"Could not parse date: {date_str!r}")
    return None


def parse_time(time_str: str) -> Optional[dt_time]:
    """Parse a time string into a time object, or return None."""
    if not time_str:
        return None

    # Very basic; tweak when you see real data (e.g. "13:45", "1:45 PM")
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
        try:
            return datetime.strptime(time_str.strip(), fmt).time()
        except ValueError:
            continue

    return None


def build_event_time(date_str: str, time_str: str) -> Optional[datetime]:
    """Combine date and time strings into a timezone-naive datetime."""
    d = parse_date(date_str)
    if not d:
        return None

    t = parse_time(time_str) if time_str else None
    if not t:
        # Default to midnight if no time
        t = dt_time(0, 0, 0)

    return datetime.combine(d, t)


def read_flight_log_csv(path: Path) -> List[Dict[str, Any]]:
    """Read one flight log CSV into a list of row dicts."""
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            # Normalise keys we expect; DictReader will give them as-is
            rows.append({
                "date": (raw.get("date") or "").strip(),
                "time": (raw.get("time") or "").strip(),
                "aircraft_make_model": (raw.get("aircraft_make_model") or "").strip(),
                "aircraft_id": (raw.get("aircraft_id") or "").strip(),
                "origin": (raw.get("origin") or "").strip(),
                "destination": (raw.get("destination") or "").strip(),
                "miles_flown": (raw.get("miles_flown") or "").strip(),
                "flight_no": (raw.get("flight_no") or "").strip(),
                "remarks": (raw.get("remarks") or "").strip(),
                "landings": (raw.get("landings") or "").strip(),
                "aircraft_category": (raw.get("aircraft_category") or "").strip(),
            })
    return rows


def ingest_flight_logs(session: Session) -> None:
    """
    Ingest all CSV flight logs under data/extracted/tables/flight_logs
    into the Event table as event_type='flight'.
    """
    if not FLIGHT_LOGS_DIR.exists():
        print(f"[flight_logs_structured] Directory not found: {FLIGHT_LOGS_DIR}")
        return

    csv_paths = sorted(FLIGHT_LOGS_DIR.glob("*.csv"))
    if not csv_paths:
        print(f"[flight_logs_structured] No CSV files found in {FLIGHT_LOGS_DIR}")
        return

    created = 0

    for csv_path in csv_paths:
        print(f"[flight_logs_structured] Processing {csv_path}")
        rows = read_flight_log_csv(csv_path)

        for row in rows:
            # Skip empty lines (no date & no aircraft_id)
            if not row["date"] and not row["aircraft_id"]:
                continue

            event_time = build_event_time(row["date"], row["time"])
            if not event_time:
                # If we cannot parse date at all, skip this row for now
                print(f"[flight_logs_structured] Skipping row with bad date: {row!r}")
                continue

            # Basic numeric parsing with soft failure
            miles_flown = None
            if row["miles_flown"]:
                try:
                    miles_flown = float(row["miles_flown"])
                except ValueError:
                    pass

            landings = None
            if row["landings"]:
                try:
                    landings = int(row["landings"])
                except ValueError:
                    pass

            meta: Dict[str, Any] = {
                "aircraft_make_model": row["aircraft_make_model"],
                "aircraft_id": row["aircraft_id"],
                "origin": row["origin"],
                "destination": row["destination"],
                "miles_flown": miles_flown,
                "flight_no": row["flight_no"],
                "remarks": row["remarks"],
                "landings": landings,
                "aircraft_category": row["aircraft_category"],
                "source_csv": str(csv_path),
            }

            event = Event(
                event_type="flight",
                event_time=event_time,
                description=f"Flight {row['flight_no'] or ''} {row['origin']}→{row['destination']}".strip(),
                meta_json=meta,
            )

            session.add(event)
            created += 1

    session.commit()
    print(f"[flight_logs_structured] Created {created} flight events")


def main() -> None:
    """CLI entrypoint: python -m backend.app.ingestion.flight_logs_structured"""
    session = SessionLocal()
    try:
        ingest_flight_logs(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
