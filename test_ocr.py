"""Quick test: run OCR + parser on test images using updated services."""

import sys
import os
import json

# Fix Windows console encoding for Chinese text
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.ocr_service import extract_text_with_metadata
from app.services.receipt_parser import parse_mcd_app_receipt


def test_image(path: str, label: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"Testing: {label}")
    print(f"File: {path}")
    print(f"{'=' * 60}")

    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "rb") as f:
        image_bytes = f.read()

    print("\n--- Running OCR with Metadata ---")
    ocr_data = extract_text_with_metadata(image_bytes)
    ocr_results = ocr_data['ocr_results']
    
    print(f"Found {len(ocr_results)} text boxes.")
    for i, res in enumerate(ocr_results[:10]):
        print(f"  [{i}] {res['text']} (x={res['avg_x']:.1f}, y={res['avg_y']:.1f})")
    if len(ocr_results) > 10:
        print(f"  ... and {len(ocr_results) - 10} more.")

    print("\n--- Parsed Result ---")
    # parse_mcd_app_receipt expects a list of lists of OCR results
    result = parse_mcd_app_receipt([ocr_results])
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"\n--- Validation ---")
    print(f"  is_valid (HKUST): {result['is_valid']}")
    print(f"  errors: {result.get('errors', [])}")


if __name__ == "__main__":
    base = os.path.dirname(__file__)
    test_image(os.path.join(base, "mcdonald_order_eng.PNG"), "English Receipt")
    test_image(os.path.join(base, "mcdonald_order_ch.PNG"), "Chinese Receipt")
    test_image(os.path.join(base, "testrun.JPG"), "TestRun Receipt")
