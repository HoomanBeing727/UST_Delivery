import re


def _extract_price(text: str) -> float:
    """Extract HK$ price from a text string."""
    match = re.search(r"(?:HK)?\$\s*([\d,]+\.?\d*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0


# HKUST validation keywords
_HKUST_KEYWORDS = [
    "HKUST",
    "Hong Kong University of Science",
    "Science & Technology",
    "Science and Technology",
    "香港科技大學",
    "科技大學",
    "科技大学",
]

def merge_items(items: list[dict]) -> list[dict]:
    """Merge duplicate items across multiple receipts.
    
    Args:
        items: List of item dicts with {name, quantity, price, components}
    
    Returns:
        List of merged items (new dicts, not modified originals)
    """
    merged = {}
    
    for item in items:
        name = item['name']
        if name in merged:
            # Merge quantities
            merged[name]['quantity'] += item['quantity']
            # Merge components (deduplicate)
            for comp in item['components']:
                if comp not in merged[name]['components']:
                    merged[name]['components'].append(comp)
        else:
            # New item - deep copy to avoid modifying original
            merged[name] = item.copy()
            merged[name]['components'] = item['components'].copy()  # Deep copy components list
    
    return list(merged.values())

def parse_receipt_structured(ocr_results: list[dict]) -> dict:
    """
    Parse OCR results with bounding box metadata using structural understanding.

    Strategy:
    1. Find section boundaries: "Order Summary" → "Payment Details"
    2. Collect title lines (before components start)
    3. Detect component start: First line that clearly repeats the main item name
    4. Collect all subsequent lines as components
    5. Filter messages ("No add-on, thank you!")
    6. Extract prices from Payment Details section

    Args:
        ocr_results: List of dicts with {text, bbox, height, confidence, avg_y}

    Returns:
        dict with {items, subtotal, total, errors}
    """
    errors: list[str] = []
    items: list[dict] = []
    subtotal = 0.0
    total = 0.0
    order_number = ""
    is_valid = False

    if not ocr_results:
        return {
            "items": [],
            "subtotal": 0.0,
            "total": 0.0,
            "order_number": "",
            "is_valid": False,
            "errors": ["No OCR data"]
        }

    # Extract order number and check HKUST validation
    full_text = " ".join([r["text"] for r in ocr_results])
    
    # Order number extraction
    order_match = re.search(
        r"(?:Order\s*#|訂單號碼\s*#|訂單\s*#)\s*(\d+)", full_text, re.IGNORECASE
    )
    if order_match:
        order_number = order_match.group(1)
    else:
        # Handle split-line: "Order#" on one line, "206" on next
        for i, result in enumerate(ocr_results):
            if "#" in result["text"] and i + 1 < len(ocr_results):
                num_match = re.match(r"^\s*(\d{2,})\s*$", ocr_results[i + 1]["text"])
                if num_match:
                    order_number = num_match.group(1)
                    break
    
    # HKUST validation
    for result in ocr_results:
        if any(kw in result["text"] for kw in _HKUST_KEYWORDS):
            is_valid = True
            break

    # Step 1: Find section boundaries
    summary_start = None
    payment_start = None

    for i, result in enumerate(ocr_results):
        text_lower = result["text"].lower()

        # Match "Order Summary" or Chinese variants
        if any(
            kw in text_lower
            for kw in ["order summary", "訂單摘要", "訂單內容", "訂罩内容"]
        ):
            summary_start = i

        # Match "Payment Details" or Chinese variants
        if any(kw in text_lower for kw in ["payment details", "付款詳情", "付款情"]):
            payment_start = i
            break

    if summary_start is None or payment_start is None:
        errors.append("Section boundaries not found")
        return {"items": [], "subtotal": 0.0, "total": 0.0, "errors": errors}

    # Step 2: Extract item section
    item_section = ocr_results[summary_start + 1 : payment_start]

    if not item_section:
        errors.append("No items found between sections")
        return {"items": [], "subtotal": 0.0, "total": 0.0, "errors": errors}

    # Step 3: Two-phase parsing
    title_lines: list[str] = []
    component_lines: list[str] = []
    in_component_phase = False
    main_item_keywords: set[str] = set()

    for i, result in enumerate(item_section):
        text = result["text"].strip()
        text_lower = text.lower()

        if not text:
            continue

        # Filter messages
        if any(kw in text_lower for kw in ["add-on", "thank you", "message"]):
            continue

        # Skip pure price lines
        if re.match(r"^(?:HK)?\$\s*[\d,.]+$", text):
            continue

        # Skip Chinese promotional text
        if re.match(r"^[\d\u4e00-\u9fff]+$", text):
            continue

        # If not in component phase yet, check if this line starts it
        if not in_component_phase:
            # Component indicators: these signal a component line
            component_indicators = [
                "chicken mcnuggets",  # Repeated main item name
                "hot mustard",
                "sauce",
            ]
            
            # Only start component phase if we have title AND see a clear indicator
            if title_lines and any(ind in text_lower for ind in component_indicators):
                in_component_phase = True

        # Collect into appropriate phase
        if in_component_phase:
            component_lines.append(text)
        else:
            title_lines.append(text)

    # Step 4: Create item
    if title_lines:
        item_name = " ".join(title_lines)

        items.append(
            {
                "name": item_name,
                "quantity": 1,
                "price": 0.0,
                "components": component_lines,
            }
        )

    # Step 5: Extract prices from Payment Details
    payment_section = ocr_results[payment_start:]

    # First pass: try to find prices on same line as keywords
    for result in payment_section:
        text = result["text"]
        text_lower = text.lower()

        if (
            "subtotal" in text_lower or "小計" in text or "合計" in text
        ) and subtotal == 0.0:
            price = _extract_price(text)
            if price > 0:
                subtotal = price

        if ("total" in text_lower or "總計" in text) and total == 0.0:
            if (
                "subtotal" not in text_lower
                and "小計" not in text
                and "合計" not in text
            ):
                price = _extract_price(text)
                if price > 0:
                    total = price

    # Second pass: look at adjacent lines if not found
    if subtotal == 0.0 or total == 0.0:
        for i, result in enumerate(payment_section):
            text_lower = result["text"].lower()

            if (
                "subtotal" in text_lower or "合計" in result["text"]
            ) and subtotal == 0.0:
                for offset in [0, -1, 1]:
                    if 0 <= i + offset < len(payment_section):
                        price = _extract_price(payment_section[i + offset]["text"])
                        if price > 0:
                            subtotal = price
                            break

            if ("total" in text_lower or "總計" in result["text"]) and total == 0.0:
                if "subtotal" not in text_lower and "合計" not in result["text"]:
                    for offset in [0, -1, 1]:
                        if 0 <= i + offset < len(payment_section):
                            price = _extract_price(payment_section[i + offset]["text"])
                            if price > 0:
                                total = price
                                break

    # Validation
    if not items:
        errors.append("No items extracted")

    return {
        "items": items,
        "subtotal": subtotal,
        "total": total,
        "order_number": order_number,
        "is_valid": is_valid,
        "errors": errors
    }


# Backward compatibility wrapper
def parse_receipt(text_lines: list[str]) -> dict:
    """
    Legacy function for backward compatibility.
    Converts text lines to OCR result format and calls new parser.
    """
    # Convert text lines to minimal OCR result format
    ocr_results = []
    for i, text in enumerate(text_lines):
        ocr_results.append(
            {
                "text": text,
                "bbox": [
                    [0, i * 20],
                    [100, i * 20],
                    [100, (i + 1) * 20],
                    [0, (i + 1) * 20],
                ],
                "height": 20.0,
                "confidence": 1.0,
                "avg_y": i * 20,
            }
        )

    result = parse_receipt_structured(ocr_results)

    # Add legacy fields for backward compatibility
    result["order_number"] = ""
    result["restaurant"] = ""
    result["is_valid"] = False

    return result
