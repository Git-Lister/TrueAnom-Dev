from datetime import datetime, timedelta, timezone
from collections import defaultdict

from backend.app.db.session import SessionLocal
from backend.app.db.schema import Event


def compute_bursts_for_pair(
    pair: str,
    bucket_days: int = 7,
    z_threshold: float = 1.5,
):
    """
    Simple burst detection:
    - Filter events with meta_json["pair"] == pair
    - Bucket counts by N-day windows
    - Compute mean and std of bucket counts
    - Return buckets whose count > mean + z_threshold * std
    """
    db = SessionLocal()
    try:
        q = db.query(Event).filter(Event.meta_json["pair"].as_string() == pair)
        events = q.all()
    finally:
        db.close()

    if not events:
        return []

    # Sort by time
    events.sort(key=lambda e: e.event_time)

    # Determine bucket start times
    bucket_size = timedelta(days=bucket_days)
    buckets = defaultdict(int)

    start = events[0].event_time
    for ev in events:
        delta = ev.event_time - start
        bucket_index = delta // bucket_size
        bucket_start = start + bucket_index * bucket_size
        buckets[bucket_start] += 1

    counts = list(buckets.values())
    mean = sum(counts) / len(counts)
    if len(counts) > 1:
        variance = sum((c - mean) ** 2 for c in counts) / (len(counts) - 1)
    else:
        variance = 0.0
    std = variance ** 0.5

    bursts = []
    for bucket_start, count in buckets.items():
        if std == 0:
            # If std is zero, any count greater than mean is "burst"
            is_burst = count > mean
        else:
            z = (count - mean) / std
            is_burst = z >= z_threshold
        if is_burst:
            bursts.append(
                {
                    "bucket_start": bucket_start.isoformat(),
                    "count": count,
                    "mean": mean,
                    "std": std,
                }
            )

    bursts.sort(key=lambda b: b["bucket_start"])
    return bursts


def main():
    bursts = compute_bursts_for_pair("A-B", bucket_days=7)
    print("Bursts:", bursts)


if __name__ == "__main__":
    main()
