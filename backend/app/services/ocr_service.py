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
