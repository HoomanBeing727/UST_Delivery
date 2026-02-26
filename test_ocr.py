"""Quick test: run OCR + parser on both test images."""

import sys
import os
import json

# Fix Windows console encoding for Chinese text
sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.ocr_service import extract_text
from app.services.receipt_parser import parse_receipt


def test_image(path: str, label: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"Testing: {label}")
    print(f"File: {path}")
    print(f"{'=' * 60}")

    with open(path, "rb") as f:
        image_bytes = f.read()

    print("\n--- Raw OCR Text Lines ---")
    lines = extract_text(image_bytes)
    for i, line in enumerate(lines):
        print(f"  [{i}] {line}")

    print("\n--- Parsed Result ---")
    result = parse_receipt(lines)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\n--- Validation ---")
    print(f"  is_valid (HKUST): {result['is_valid']}")
    print(f"  errors: {result['errors']}")


if __name__ == "__main__":
    base = os.path.dirname(__file__)
    test_image(os.path.join(base, "mcdonald_order_eng.PNG"), "English Receipt")
    test_image(os.path.join(base, "mcdonald_order_ch.PNG"), "Chinese Receipt")
