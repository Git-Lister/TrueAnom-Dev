import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
from PIL import Image

# Adjust if Tesseract is not on PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_PATH = Path("data/raw/flight_logs/doj_maxwell_flight_log1.pdf")
CSV_PATH = Path("data/extracted/tables/flight_logs/doj_maxwell_flight_log1_structured.csv")

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


@dataclass
class ColumnBand:
    name: str
    x_min: float
    x_max: float


def detect_column_bands(image: Image.Image) -> List[ColumnBand]:
    """
    Define approximate column bands for the logbook layout.
    For v1 we hard-code relative positions; later we can refine per page.
    """
    width, _ = image.size

    # These fractions are heuristic and may need tuning once you inspect output.
    # They assume columns from left to right: date, make/model, tail, from, to, miles, flight_no, remarks.
    return [
        ColumnBand("date", 0.00 * width, 0.10 * width),
        ColumnBand("aircraft_make_model", 0.10 * width, 0.30 * width),
        ColumnBand("aircraft_id", 0.30 * width, 0.45 * width),
        ColumnBand("origin", 0.45 * width, 0.60 * width),
        ColumnBand("destination", 0.60 * width, 0.75 * width),
        ColumnBand("miles_flown", 0.75 * width, 0.85 * width),
        ColumnBand("flight_no", 0.85 * width, 0.93 * width),
        ColumnBand("remarks", 0.00 * width, 1.00 * width),  # catch-all; we’ll assign by y-position
    ]


def group_words_into_rows(data: Dict[str, List[Any]], y_tol: int = 10) -> List[List[Dict[str, Any]]]:
    """
    Group OCR words into horizontal rows based on their center y position.
    """
    n = len(data["text"])
    words = []
    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue
        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])
        words.append(
            {
                "text": text,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "cx": x + w / 2,
                "cy": y + h / 2,
            }
        )

    # Sort by vertical position
    words.sort(key=lambda w: w["cy"])

    rows: List[List[Dict[str, Any]]] = []
    current_row: List[Dict[str, Any]] = []
    last_y: float = None

    for w in words:
        if last_y is None or abs(w["cy"] - last_y) <= y_tol:
            current_row.append(w)
            last_y = w["cy"] if last_y is None else (last_y + w["cy"]) / 2
        else:
            rows.append(sorted(current_row, key=lambda ww: ww["cx"]))
            current_row = [w]
            last_y = w["cy"]

    if current_row:
        rows.append(sorted(current_row, key=lambda ww: ww["cx"]))

    return rows


def map_row_to_fields(row_words: List[Dict[str, Any]], bands: List[ColumnBand]) -> Dict[str, str]:
    """
    Assign words in a row to columns based on x position vs column bands.
    """
    fields: Dict[str, List[str]] = {b.name: [] for b in bands}

    for w in row_words:
        for b in bands:
            if b.name == "remarks":
                # We'll fill remarks later from everything not clearly in earlier columns
                continue
            if b.x_min <= w["cx"] < b.x_max:
                fields[b.name].append(w["text"])
                break
        else:
            # Words that don't fall into any band go to remarks
            fields["remarks"].append(w["text"])

    # Join tokens into strings
    out: Dict[str, str] = {}
    for b in bands:
        out[b.name] = " ".join(fields[b.name]).strip()

    return out


def process_page(image: Image.Image) -> List[Dict[str, str]]:
    """
    OCR a page image and return structured row dicts.
    """
    # Basic preprocessing: convert to grayscale, maybe increase contrast
    gray = image.convert("L")

    # You can experiment with thresholds if needed.
    # gray = gray.point(lambda x: 0 if x < 180 else 255, "1")

    ocr_data = pytesseract.image_to_data(gray, output_type=Output.DICT, config="--psm 6")
    rows_words = group_words_into_rows(ocr_data, y_tol=10)

    bands = detect_column_bands(gray)

    records: List[Dict[str, str]] = []

    for row in rows_words:
        fields = map_row_to_fields(row, bands)

        # Heuristic: skip rows that clearly look like headers or totals
        text_all = " ".join(f for f in fields.values())
        if not text_all:
            continue
        if "Aircraft Make" in text_all or "Date" in text_all or "Page Total" in text_all:
            continue
        if "I certify that the statements" in text_all:
            continue

        records.append(fields)

    return records


def extract_flightlog_records(pdf_path: Path) -> List[Dict[str, str]]:
    """
    High-level: PDF -> images -> OCR -> row dicts with flight-log-ish fields.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    # Render pages; you can restrict first few pages while testing (e.g. pages[0:2])
    pages = convert_from_path(str(pdf_path), dpi=300)

    all_records: List[Dict[str, str]] = []
    for idx, img in enumerate(pages):
        print(f"[ocr] Processing page {idx + 1}/{len(pages)}")
        page_records = process_page(img)
        print(f"[ocr]  -> {len(page_records)} row candidates")
        all_records.extend(page_records)

    return all_records


def write_structured_csv(records: List[Dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)

        for r in records:
            # Map fields into your schema; we leave time/landings/aircraft_category empty for now.
            writer.writerow(
                [
                    r.get("date", ""),
                    "",  # time
                    r.get("aircraft_make_model", ""),
                    r.get("aircraft_id", ""),
                    r.get("origin", ""),
                    r.get("destination", ""),
                    r.get("miles_flown", ""),
                    r.get("flight_no", ""),
                    r.get("remarks", ""),
                    "",  # landings
                    "",  # aircraft_category
                ]
            )


def main():
    print(f"[ocr] Reading {PDF_PATH}")
    records = extract_flightlog_records(PDF_PATH)
    print(f"[ocr] Total row candidates: {len(records)}")

    write_structured_csv(records, CSV_PATH)
    print(f"[ocr] Wrote structured CSV to {CSV_PATH}")


if __name__ == "__main__":
    main()
