from datetime import datetime, timedelta, timezone

from backend.app.db.session import SessionLocal
from backend.app.db.schema import Event

def seed_test_events():
    db = SessionLocal()
    try:
        db.query(Event).delete()

        base = datetime(2020, 1, 1, tzinfo=timezone.utc)

        # Low baseline: 1 event per week for 4 weeks
        events = []
        for i in range(4):
            events.append(
                Event(
                    document_id=None,
                    event_type="email",
                    event_time=base + timedelta(days=7 * i),
                    description="A ↔ B baseline",
                    meta_json={"pair": "A-B"},
                )
            )

        # Burst: 5 events in a single week
        burst_start = base + timedelta(days=28)
        for j in range(5):
            events.append(
                Event(
                    document_id=None,
                    event_type="email",
                    event_time=burst_start + timedelta(days=j),
                    description="A ↔ B burst",
                    meta_json={"pair": "A-B"},
                )
            )

        for ev in events:
            db.add(ev)

        db.commit()
        print("Seeded test events.")
    finally:
        db.close()


def main():
    seed_test_events()


if __name__ == "__main__":
    main()
