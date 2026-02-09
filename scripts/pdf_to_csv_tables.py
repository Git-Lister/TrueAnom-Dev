import csv
from pathlib import Path
from typing import List, Optional

import pdfplumber

# Root for raw PDFs and extracted tables
RAW_ROOT = Path("data/raw")
OUT_ROOT = Path("data/extracted/tables")


def extract_tables(pdf_path: Path) -> List[List[str]]:
    """
    Extract all table rows (excluding header rows) from a PDF
    into generic cell lists.
    """
    rows: List[List[str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if not tables:
                continue

            for table_idx, table in enumerate(tables):
                for r_idx, row in enumerate(table):
                    # Heuristic: skip first row of each table as header
                    if r_idx == 0:
                        continue
                    cells = [c.strip() if isinstance(c, str) else "" for c in row]
                    # Skip completely empty rows
                    if not any(cells):
                        continue
                    rows.append(cells)

    return rows


def write_csv(rows: List[List[str]], out_path: Path, header: Optional[List[str]] = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(rows)


def default_output_path(pdf_path: Path) -> Path:
    """
    Map e.g. data/raw/flight_logs/foo.pdf -> data/extracted/tables/flight_logs/foo_table1.csv
    """
    relative = pdf_path.relative_to(RAW_ROOT)
    return OUT_ROOT / relative.parent / (relative.stem + "_table1.csv")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract tables from a PDF into a generic CSV")
    parser.add_argument("pdf_path", type=str, help="Path to input PDF (under data/raw/...)")
    parser.add_argument("--out", type=str, default=None, help="Optional explicit CSV output path")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    rows = extract_tables(pdf_path)
    print(f"Extracted {len(rows)} table rows from {pdf_path}")

    out_path = Path(args.out) if args.out else default_output_path(pdf_path)
    # For generic export, we don’t force a header; callers can re-map later
    write_csv(rows, out_path, header=None)
    print(f"Wrote CSV to {out_path}")


if __name__ == "__main__":
    main()
