import re
from difflib import SequenceMatcher
from typing import Any


# ─── Bilingual section markers ───
SECTIONS: dict[str, list[str]] = {
    "order_num": ["Order #", "訂單號碼"],
    "restaurant": ["Serving restaurant", "提供服務的餐廳"],
    "summary": ["Order Summary", "訂單內容"],
    "payment": ["Payment Details", "付款詳情"],
}


# =========================================================
# HELPERS
# =========================================================


def _extract_price(text: str) -> float:
    """Extract a decimal price from text like 'HK$ 1,089.00'."""
    match = re.search(r"([\d,]+\.\d{2})", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0.0


def _contains_hkust(text: str) -> bool:
    lower = text.lower()
    return "hong kong university of science" in lower or "hkust" in lower


def _convert_ocr_entries(ocr_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert OCR service format {text,bbox,height,confidence,avg_y,avg_x}
    to parser entry format {text,x,y,h}."""
    entries: list[dict[str, Any]] = []
    for item in ocr_results:
        text = item.get("text", "").strip()
        if not text:
            continue
        entries.append(
            {
                "text": text,
                "x": item.get("avg_x", 0.0),
                "y": item.get("avg_y", 0.0),
                "h": item.get("height", 0.0),
            }
        )
    return sorted(entries, key=lambda e: (e["y"], e["x"]))


# =========================================================
# Row clustering
# =========================================================


def cluster_rows(entries: list[dict[str, Any]], y_gap: float = 15) -> list[list[dict[str, Any]]]:
    """Group entries into rows by vertical proximity."""
    if not entries:
        return []
    rows: list[list[dict[str, Any]]] = []
    cur = [entries[0]]
    for e in entries[1:]:
        if e["y"] - cur[-1]["y"] > y_gap:
            rows.append(sorted(cur, key=lambda e: e["x"]))
            cur = []
        cur.append(e)
    rows.append(sorted(cur, key=lambda e: e["x"]))
    return rows


def row_text(row: list[dict[str, Any]]) -> str:
    return " ".join(e["text"] for e in row)


# =========================================================
# Multi-screenshot merge
# =========================================================


def merge_screenshots(entries_list: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """
    Merge multiple screenshot OCR results.
    Detects overlap between tail of image N and head of image N+1,
    deduplicates, then concatenates.
    """
    if len(entries_list) <= 1:
        return entries_list[0] if entries_list else []

    merged_rows = cluster_rows(entries_list[0])

    for entries in entries_list[1:]:
        new_rows = cluster_rows(entries)

        # compare tail of merged vs head of new to find overlap
        tail_texts = [row_text(r).lower() for r in merged_rows[-8:]]
        overlap_end = 0

        for i, nr in enumerate(new_rows):
            nt = row_text(nr).lower()
            for tt in tail_texts:
                if SequenceMatcher(None, nt, tt).ratio() > 0.75:
                    overlap_end = i + 1  # skip this row (it's a duplicate)
                    break

        # append non-overlapping rows with a y-offset so ordering is preserved
        y_offset = max(e["y"] for r in merged_rows for e in r) + 100

        for row in new_rows[overlap_end:]:
            merged_rows.append([{**e, "y": e["y"] + y_offset} for e in row])

    return [e for row in merged_rows for e in row]


# =========================================================
# Locate sections
# =========================================================


def find_sections(rows: list[list[dict[str, Any]]]) -> dict[str, int]:
    """Return {section_name: row_index} for each detected section marker."""
    idx: dict[str, int] = {}
    for i, row in enumerate(rows):
        t = row_text(row).lower()
        for name, keywords in SECTIONS.items():
            if any(kw.lower() in t for kw in keywords):
                idx[name] = i
    return idx


def next_section_idx(sec_idx: dict[str, int], after: int, total_rows: int) -> int:
    """Find the row index of the next section after `after`."""
    candidates = [v for k, v in sec_idx.items() if v > after]
    return min(candidates) if candidates else total_rows


# =========================================================
# Parse each section
# =========================================================


def parse_order_number(rows: list[list[dict[str, Any]]], sec_idx: dict[str, int]) -> str:
    if "order_num" not in sec_idx:
        return ""
    start = sec_idx["order_num"]
    end = next_section_idx(sec_idx, start, len(rows))
    for row in rows[start:end]:
        t = row_text(row)
        for kw in SECTIONS["order_num"] + ["#"]:
            t = t.replace(kw, "")
        nums = re.findall(r"\d+", t)
        if nums:
            return nums[0]
    return ""


def parse_restaurant(rows: list[list[dict[str, Any]]], sec_idx: dict[str, int]) -> str:
    if "restaurant" not in sec_idx:
        return ""
    start = sec_idx["restaurant"] + 1  # skip the marker row itself
    end = next_section_idx(sec_idx, sec_idx["restaurant"], len(rows))
    parts: list[str] = []
    for row in rows[start:end]:
        t = row_text(row)
        # stop if we accidentally hit another marker
        if any(any(kw.lower() in t.lower() for kw in kws) for kws in SECTIONS.values()):
            break
        parts.append(t)
    return " ".join(parts).strip()


def has_qty_on_right(row: list[dict[str, Any]], x_gap: float = 40) -> tuple[bool, int | None]:
    """
    Key heuristic: if the rightmost element in a row is a standalone
    number AND it's far to the right of the other text, it's a
    quantity indicator and this row starts a NEW item.
    """
    if len(row) < 2:
        return False, None
    rightmost = max(row, key=lambda e: e["x"])
    if not re.fullmatch(r"\d+", rightmost["text"]):
        return False, None
    rest_max_x = max(e["x"] for e in row if e is not rightmost)
    if rightmost["x"] - rest_max_x > x_gap:
        return True, int(rightmost["text"])
    return False, None


def parse_items(rows: list[list[dict[str, Any]]], sec_idx: dict[str, int]) -> list[dict[str, Any]]:
    """
    Between "Order Summary" and "Payment Details":
      - row with qty number on far right  →  new item (name = rest of row)
      - row without qty                   →  detail of current item
    """
    if "summary" not in sec_idx:
        return []
    start = sec_idx["summary"] + 1
    end = next_section_idx(sec_idx, sec_idx["summary"], len(rows))

    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for row in rows[start:end]:
        t = row_text(row)
        # stop if we hit another section marker
        if any(any(kw.lower() in t.lower() for kw in kws) for kws in SECTIONS.values()):
            break

        found_qty, qty = has_qty_on_right(row)

        if found_qty:
            # start new item
            if current:
                items.append(current)
            rightmost = max(row, key=lambda e: e["x"])
            name = " ".join(e["text"] for e in row if e is not rightmost)
            current = {"name": name, "quantity": qty, "price": 0.0}

        elif current is not None:
            # detail line of current item (not in schema, skip)
            pass

        else:
            # edge case: item without detected qty
            current = {"name": t, "quantity": 1, "price": 0.0}

    if current:
        items.append(current)
    return items


def parse_payment(
    rows: list[list[dict[str, Any]]], sec_idx: dict[str, int]
) -> tuple[float, float]:
    if "payment" not in sec_idx:
        return 0.0, 0.0
    subtotal = 0.0
    total = 0.0
    for row in rows[sec_idx["payment"] :]:
        t = row_text(row)
        t_lower = t.lower()
        if "subtotal" in t_lower or "合計" in t:
            subtotal = _extract_price(t)
        elif "total" in t_lower or "總計" in t:
            total = _extract_price(t)
    return subtotal, total


# =========================================================
# MAIN PARSER
# =========================================================


def parse_mcd_app_receipt(ocr_results_per_image: list[list[dict[str, Any]]]) -> dict[str, Any]:
    """
    Parse McDonald's app receipt from OCR results.

    Args:
        ocr_results_per_image: list of per-image OCR results,
            each a list of dicts with {text, bbox, height, confidence, avg_y, avg_x}

    Returns:
        dict with order_number, restaurant, is_valid, items, subtotal, total, errors
    """
    if not ocr_results_per_image or all(len(r) == 0 for r in ocr_results_per_image):
        return {
            "order_number": "",
            "restaurant": "",
            "is_valid": False,
            "items": [],
            "subtotal": 0.0,
            "total": 0.0,
            "errors": ["Empty OCR result"],
        }

    # 1. Convert each image's OCR results to parser entry format
    entries_list = [_convert_ocr_entries(results) for results in ocr_results_per_image]

    # 2. Merge multi-screenshot (handles overlap dedup)
    entries = merge_screenshots(entries_list)

    # 3. Cluster into rows
    rows = cluster_rows(entries)

    # 4. Find section boundaries
    sec_idx = find_sections(rows)

    # 5. Parse each section
    order_number = parse_order_number(rows, sec_idx)
    restaurant = parse_restaurant(rows, sec_idx)
    items = parse_items(rows, sec_idx)
    subtotal, total = parse_payment(rows, sec_idx)

    # 6. HKUST validation
    full_text = " ".join(row_text(r) for r in rows)
    is_valid = _contains_hkust(full_text)

    # 7. Validation errors
    errors: list[str] = []

    if not items:
        errors.append("No items detected")

    computed_sum = sum(i["price"] * i["quantity"] for i in items)
    if subtotal and computed_sum and abs(computed_sum - subtotal) > 1.0:
        errors.append("Subtotal mismatch")

    if subtotal and total and abs(subtotal - total) > 1.0:
        errors.append("Subtotal/Total mismatch")

    is_valid = is_valid and len(errors) == 0

    return {
        "order_number": order_number,
        "restaurant": restaurant,
        "is_valid": is_valid,
        "items": items,
        "subtotal": subtotal,
        "total": total,
        "errors": errors,
    }
