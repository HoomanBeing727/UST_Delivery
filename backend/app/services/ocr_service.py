import io
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

# Singleton OCR engine — initialized once, reused across requests
_engine = RapidOCR()


def extract_text(image_bytes: bytes) -> list[str]:
    """Run OCR on image bytes and return text lines sorted top-to-bottom."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(image)

    result, _ = _engine(img_array)

    if result is None:
        return []

    # result is list of [bbox, text, confidence]
    # bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    # Sort by average y-coordinate (top-to-bottom)
    lines: list[tuple[float, str]] = []
    for item in result:
        bbox = item[0]
        text = item[1]
        avg_y = sum(point[1] for point in bbox) / len(bbox)
        lines.append((avg_y, text))

    lines.sort(key=lambda x: x[0])
    return [text for _, text in lines]


def extract_text_with_metadata(image_bytes: bytes) -> dict:
    """
    Run OCR on image bytes and return structured data with bounding box metadata.
    
    Returns:
        dict with keys:
        - ocr_results: list of dicts with {text, bbox, height, confidence, avg_y}
        - full_text: concatenated text (same as extract_text output)
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(image)

    result, _ = _engine(img_array)

    if result is None:
        return {"ocr_results": [], "full_text": ""}

    # Parse OCR results and calculate metadata
    ocr_results: list[dict] = []
    for item in result:
        bbox = item[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        text = item[1]
        confidence = item[2]

        # Calculate height: bottom-left Y - top-left Y
        height = bbox[2][1] - bbox[0][1]

        # Calculate average Y for sorting (top-to-bottom)
        avg_y = sum(point[1] for point in bbox) / len(bbox)

        ocr_results.append({
            "text": text,
            "bbox": bbox,
            "height": height,
            "confidence": confidence,
            "avg_y": avg_y
        })

    # Sort by vertical position (top-to-bottom)
    ocr_results.sort(key=lambda x: x["avg_y"])

    # Generate full text for backward compatibility
    full_text = "\n".join([r["text"] for r in ocr_results])

    return {
        "ocr_results": ocr_results,
        "full_text": full_text
    }
