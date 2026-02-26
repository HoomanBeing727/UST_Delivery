import re


# Section markers in McDonald's receipts (including OCR-mangled variants)
_SECTION_MARKERS = [
    "order details", "serving restaurant", "order summary",
    "payment details", "subtotal", "total",
    "訂單詳情", "提供服務的餐廳", "訂單摘要", "訂單內容",
    "付款詳情", "合計", "總計",
    # OCR-mangled variants
    "订罩", "付款情", "訂罩",
]

_HKUST_KEYWORDS = [
    "HKUST",
    "Hong Kong University of Science",
    "Science & Technology",
    "Science and Technology",
    "香港科技大學",
    "科技大學",
    "科技大学",
]


def _extract_price(text: str) -> float | None:
    """Extract HK$ price from a text string."""
    match = re.search(r"(?:HK)?\$\s*([\d,]+\.?\d*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def _is_section_marker(line: str) -> bool:
    """Check if a line is a known section marker."""
    lower = line.strip().lower()
    return any(marker in lower for marker in _SECTION_MARKERS)


def parse_receipt(text_lines: list[str]) -> dict:
    """Parse OCR text lines from a McDonald's receipt into structured order data."""
    errors: list[str] = []
    order_number = ""
    restaurant = ""
    items: list[dict] = []
    subtotal = 0.0
    total = 0.0

    full_text = "\n".join(text_lines)

    # --- Order Number ---
    # Handle same-line: "Order #163" or "訂單號碼 #168"
    order_match = re.search(
        r"(?:Order\s*#|訂單號碼\s*#|訂單\s*#)\s*(\d+)", full_text, re.IGNORECASE
    )
    if order_match:
        order_number = order_match.group(1)
    else:
        # Handle split-line: any line with "#" followed by next line being a number
        for i, line in enumerate(text_lines):
            if "#" in line and i + 1 < len(text_lines):
                num_match = re.match(r"^\s*(\d{2,})\s*$", text_lines[i + 1])
                if num_match:
                    order_number = num_match.group(1)
                    break

    if not order_number:
        errors.append("Could not extract order number")

    # --- Restaurant ---
    for i, line in enumerate(text_lines):
        if any(kw in line for kw in _HKUST_KEYWORDS):
            restaurant = line.strip()
            # Only concatenate if next line starts with "&" (continuation)
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1].strip()
                if next_line.startswith("&"):
                    restaurant = f"{restaurant} {next_line}"
            break

    if not restaurant:
        # Fuzzy: look for lines after "Serving restaurant" / "提供服務的餐廳"
        for i, line in enumerate(text_lines):
            lower = line.strip().lower()
            if "serving restaurant" in lower or "提供服務" in lower:
                if i + 1 < len(text_lines):
                    restaurant = text_lines[i + 1].strip()
                    if i + 2 < len(text_lines):
                        next2 = text_lines[i + 2].strip()
                        if next2.startswith("&"):
                            restaurant = f"{restaurant} {next2}"
                break

    if not restaurant:
        errors.append("Could not extract restaurant name")

    # --- HKUST Validation ---
    is_valid = bool(
        restaurant and any(kw in restaurant for kw in _HKUST_KEYWORDS)
    )

    # --- Items ---
    # Find the "item section" between Order Summary and Payment Details
    item_start = -1
    item_end = len(text_lines)

    for i, line in enumerate(text_lines):
        lower = line.strip().lower()
        # Match "Order Summary" or Chinese variants (including OCR-mangled)
        if any(kw in lower for kw in ["order summary", "訂單摘要", "訂單內容",
                                        "訂罩内容", "訂罩內容", "订罩内容"]):
            item_start = i + 1
        elif item_start >= 0 and any(
            kw in lower for kw in ["payment details", "付款詳情", "付款情",
                                    "subtotal", "合計"]
        ):
            item_end = i
            break

    if item_start >= 0:
        item_section = text_lines[item_start:item_end]

        # Check for quantity markers
        has_qty_markers = any(
            re.search(r"[×xX]\s*\d+", line) for line in item_section
        )

        if has_qty_markers:
            for i, line in enumerate(item_section):
                qty_match = re.search(r"[×xX]\s*(\d+)", line)
                if qty_match:
                    quantity = int(qty_match.group(1))
                    name_part = re.split(r"\s*[×xX]\s*\d+", line)[0].strip()
                    if not name_part and i > 0:
                        name_part = item_section[i - 1].strip()
                    price = 0.0
                    price_val = _extract_price(line)
                    if price_val is not None:
                        price = price_val
                    elif i + 1 < len(item_section):
                        price_val = _extract_price(item_section[i + 1])
                        if price_val is not None:
                            price = price_val
                    if name_part:
                        items.append({"name": name_part, "quantity": quantity, "price": price})
        else:
            # No quantity markers. Pick the LAST readable name before Payment Details
            # as the item name (McDonald's shows item multiple times: Chinese, UPPERCASE, mixed case)
            # The mixed-case version is the most readable.
            candidate_names: list[str] = []
            for line in item_section:
                stripped = line.strip()
                if not stripped or len(stripped) < 3:
                    continue
                if re.match(r"^(?:HK)?\$\s*[\d.]+$", stripped):
                    continue
                if re.match(r"^\d+$", stripped):
                    continue
                if _is_section_marker(stripped):
                    continue
                candidate_names.append(stripped)

            if candidate_names:
                # Use the last candidate (typically the mixed-case display name)
                # This avoids picking garbled OCR text or ALL-CAPS code names
                best_name = candidate_names[-1]
                # If there are multiple candidates, try to find one with mixed case
                for name in reversed(candidate_names):
                    if not name.isupper() and any(c.isalpha() for c in name):
                        best_name = name
                        break
                items.append({"name": best_name, "quantity": 1, "price": 0.0})

    # Fallback: look for quantity markers anywhere in the text
    if not items:
        for i, line in enumerate(text_lines):
            qty_match = re.search(r"[×xX]\s*(\d+)", line)
            if qty_match:
                quantity = int(qty_match.group(1))
                name_part = re.split(r"\s*[×xX]\s*\d+", line)[0].strip()
                if not name_part and i > 0:
                    name_part = text_lines[i - 1].strip()
                price = 0.0
                price_val = _extract_price(line)
                if price_val:
                    price = price_val
                if name_part:
                    skip_kw = ["subtotal", "total", "合計", "總計", "order", "訂單"]
                    if not any(kw in name_part.lower() for kw in skip_kw):
                        items.append({"name": name_part, "quantity": quantity, "price": price})

    if not items:
        errors.append("Could not extract any order items")

    # --- Subtotal ---
    for i, line in enumerate(text_lines):
        if re.search(r"(?:Subtotal|合計)", line, re.IGNORECASE):
            price_val = _extract_price(line)
            if price_val is not None:
                subtotal = price_val
                break
            if i > 0:
                price_val = _extract_price(text_lines[i - 1])
                if price_val is not None:
                    subtotal = price_val
                    break
            if i + 1 < len(text_lines):
                price_val = _extract_price(text_lines[i + 1])
                if price_val is not None:
                    subtotal = price_val
                    break

    # --- Total ---
    for i, line in enumerate(text_lines):
        lower = line.strip().lower()
        is_total_line = ("total" in lower or "總計" in lower) and not (
            "subtotal" in lower or "合計" in lower
        )
        if is_total_line:
            price_val = _extract_price(line)
            if price_val is not None:
                total = price_val
                break
            if i > 0:
                price_val = _extract_price(text_lines[i - 1])
                if price_val is not None:
                    total = price_val
                    break
            if i + 1 < len(text_lines):
                price_val = _extract_price(text_lines[i + 1])
                if price_val is not None:
                    total = price_val
                    break

    # Fallback: if no total found, use the last HK$ price in the text
    if total == 0.0:
        for line in reversed(text_lines):
            price_val = _extract_price(line)
            if price_val is not None:
                total = price_val
                break

    # Assign item price from subtotal if items have no price
    if items and all(item["price"] == 0.0 for item in items) and subtotal > 0:
        if len(items) == 1:
            items[0]["price"] = subtotal

    return {
        "order_number": order_number,
        "restaurant": restaurant,
        "items": items,
        "subtotal": subtotal,
        "total": total,
        "is_valid": is_valid,
        "errors": errors,
    }
