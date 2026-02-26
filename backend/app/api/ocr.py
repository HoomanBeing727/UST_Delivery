from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import OCRResponse, OrderItem
from app.services.ocr_service import extract_text
from app.services.receipt_parser import parse_receipt

router = APIRouter(prefix="/api", tags=["OCR"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/ocr", response_model=OCRResponse)
async def process_receipt(file: UploadFile = File(...)) -> OCRResponse:
    """Accept a receipt image, run OCR, and return structured order data."""
    # Validate content type
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image, got {file.content_type}",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(contents)} bytes). Max is {MAX_FILE_SIZE} bytes.",
        )

    # Run OCR
    text_lines = extract_text(contents)

    # Parse receipt
    parsed = parse_receipt(text_lines)

    return OCRResponse(
        order_number=parsed["order_number"],
        restaurant=parsed["restaurant"],
        items=[OrderItem(**item) for item in parsed["items"]],
        subtotal=parsed["subtotal"],
        total=parsed["total"],
        is_valid=parsed["is_valid"],
        errors=parsed["errors"],
        raw_text=text_lines,
    )
