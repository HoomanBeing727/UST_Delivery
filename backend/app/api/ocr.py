
from typing import Any

from fastapi import APIRouter, File, UploadFile

from app.models.schemas import OCRResponse, OrderItem
from app.services.ocr_service import extract_text_with_metadata
from app.services.receipt_parser import parse_mcd_app_receipt

router = APIRouter(prefix="/api", tags=["OCR"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/ocr", response_model=OCRResponse)
async def process_receipt(files: list[UploadFile] = File(...)) -> OCRResponse:
    """Accept multiple receipt images, run OCR on each, parse as one receipt."""
    all_ocr_results: list[list[dict[str, Any]]] = []
    all_errors = []
    all_raw_text = []

    # Process each file sequentially
    for file in files:
        try:
            # Validate content type
            if file.content_type and not file.content_type.startswith("image/"):
                all_errors.append(f"File {file.filename} is not an image: {file.content_type}")
                continue

            # Read and validate size
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                all_errors.append(f"File {file.filename} too large: {len(contents)} bytes")
                continue

            # Extract OCR with metadata
            ocr_data = extract_text_with_metadata(contents)
            all_ocr_results.append(ocr_data['ocr_results'])
            all_raw_text.extend(ocr_data['full_text'].split('\n'))

        except Exception as e:
            all_errors.append(f"OCR failed for {file.filename}: {str(e)}")

    # Parse combined OCR results as ONE receipt
    parsed = parse_mcd_app_receipt(all_ocr_results)
    
    # Merge errors
    if parsed.get("errors"):
        parsed["errors"].extend(all_errors)
    else:
        parsed["errors"] = all_errors

    return OCRResponse(
        order_number=parsed.get("order_number", ""),
        restaurant=parsed.get("restaurant", ""),
        items=[OrderItem(**item) for item in parsed.get("items", [])],
        subtotal=parsed.get("subtotal", 0.0),
        total=parsed.get("total", 0.0),
        is_valid=parsed.get("is_valid", False),
        errors=parsed.get("errors", []),
        raw_text=all_raw_text,
    )
