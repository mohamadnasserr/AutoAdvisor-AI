import csv
from pathlib import Path


def test_seed_inventory_rows_have_image_urls():
    seed_path = Path("data/seed/cars.csv")

    with seed_path.open(newline="", encoding="utf-8") as seed_file:
        rows = list(csv.DictReader(seed_file))

    missing_image_rows = [
        row
        for row in rows
        if not (row.get("image_url") or "").strip()
    ]

    assert rows
    assert missing_image_rows == []
