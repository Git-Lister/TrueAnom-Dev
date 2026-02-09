from pathlib import Path
import csv

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.db.schema import Document, Page

VOL00001_DAT = Path(
    "data/raw/epstein_subset/DataSet 1/DataSet 1/VOL00001/DATA/VOL00001.DAT"
)


def detect_delimiter(sample: str) -> str:
    candidates = ["þ", "|", ",", "\t", ";"]
    best_delim = ","
    best_count = 1
    for delim in candidates:
        parts = sample.split(delim)
        if len(parts) > best_count:
            best_count = len(parts)
            best_delim = delim
    return best_delim


def load_bates_ranges():
    if not VOL00001_DAT.exists():
        raise RuntimeError(f".DAT file not found at {VOL00001_DAT}")

    with VOL00001_DAT.open("r", encoding="utf-8", errors="ignore") as f:
        first_line = f.readline().rstrip("\n\r")
        if not first_line:
            raise RuntimeError("VOL00001.DAT appears to be empty.")

        delim = detect_delimiter(first_line)

    # Parse the whole file
    bates_rows = []
    with VOL00001_DAT.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            # Columns look like: '', 'Begin Bates', '\x14', 'End Bates', ''
            begin = (row.get("Begin Bates") or "").strip()
            end = (row.get("End Bates") or "").strip()
            if begin:
                bates_rows.append((begin, end or begin))

    return bates_rows


def apply_bates_to_pages():
    """
    For now we do a simple mapping:
    - Document.external_id already holds something like 'EFTA00000001.pdf'
    - Page.bates_id should match the Bates id (e.g. 'EFTA00000001') when possible.

    This is approximate because we don't yet walk the .OPT/image mapping,
    but it gives us a first linkage between pages and Bates ids.
    """
    bates_rows = load_bates_ranges()
    print(f"Loaded {len(bates_rows)} Bates ranges from VOL00001.DAT")

    db: Session = SessionLocal()
    try:
        # Build a map from Bates id -> (begin, end)
        # For single-page docs here, begin == end.
        bates_set = {begin for begin, _ in bates_rows}

        # Update pages whose document external_id matches a Bates id-derived pattern
        pages = (
            db.query(Page)
            .join(Document, Page.document_id == Document.id)
            .all()
        )

        updated = 0
        for p in pages:
            doc: Document = p.document
            # external_id like 'EFTA00000001.pdf' -> strip extension
            if doc.external_id:
                core = doc.external_id.rsplit(".", 1)[0]
            else:
                core = None

            # If the core looks like a Bates id in our set, assign it
            if core and core in bates_set:
                if p.bates_id != core:
                    p.bates_id = core
                    updated += 1

        db.commit()
        print(f"Updated {updated} pages with Bates IDs.")
    finally:
        db.close()


def inspect_vol00001_dat(max_rows: int = 2):
    # (keep your previous inspect function if you find it useful)
    pass


def main():
    apply_bates_to_pages()


if __name__ == "__main__":
    main()
