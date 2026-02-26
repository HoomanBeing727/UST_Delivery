import base64
import io
import json
import logging
from typing import Any

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

# Configure logging
logger = logging.getLogger(__name__)

# Singleton - load once
_model: Llama | None = None


def _load_model() -> Llama:
    """
    Load the SmolVLM model as a singleton.
    Uses lazy loading on first request.
    """
    global _model
    if _model is None:
        model_path = "models/SmolVLM2-2.2B-Instruct-Q4_K_M.gguf"
        mmproj_path = "models/mmproj-SmolVLM2-2.2B-Instruct-Q8_0.gguf"

        logger.info(f"Loading VLM model from {model_path}...")

        # Initialize chat handler for multimodal support
        # Note: SmolVLM typically uses LLaVA-style architecture compatible with standard handlers
        # We use Llava15ChatHandler as a safe default for modern GGUF vision models
        chat_handler = Llava15ChatHandler(clip_model_path=mmproj_path)

        _model = Llama(
            model_path=model_path,
            chat_handler=chat_handler,
            n_ctx=8192,  # Context for image embeddings
            n_gpu_layers=0,  # CPU-only (target: ≤1.4s per image)
            verbose=False,
        )
        logger.info("VLM model loaded successfully.")

    return _model


def _image_bytes_to_base64_uri(image_bytes: bytes) -> str:
    """Convert image bytes to base64 data URI for llama.cpp."""
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_data}"


def _check_hkust_validation(image_bytes: bytes) -> bool:
    """
    Check if receipt is from HKUST McDonald's using VLM.
    Looks for keywords: HKUST, Hong Kong University of Science and Technology, 科技大學.
    """
    try:
        model = _load_model()
        image_uri = _image_bytes_to_base64_uri(image_bytes)

        response = model.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_uri}},
                        {
                            "type": "text",
                            "text": "Does this receipt mention HKUST, Hong Kong University of Science and Technology, or 科技大學? Answer only 'yes' or 'no'.",
                        },
                    ],
                }
            ],
            temperature=0.0,
            max_tokens=10,
        )

        answer = response["choices"][0]["message"]["content"].strip().lower()
        return "yes" in answer
    except Exception as e:
        logger.error(f"Validation check failed: {e}")
        return False  # Fail safe or fail secure? Fail safe for now, but mark invalid if unsure.


def extract_receipt_data(image_bytes: bytes) -> dict[str, Any]:
    """
    Extract structured receipt data using SmolVLM Q4 GGUF.
    VLM-only approach - no OCR fallback.

    Returns:
        dict: Structured receipt data with order_number, items, totals, validation status.
    """
    try:
        model = _load_model()

        # Convert image to base64 URI
        image_uri = _image_bytes_to_base64_uri(image_bytes)

        # Prompt for structured JSON output
        prompt = """Extract structured data from this McDonald's receipt.
        Return ONLY valid JSON with this exact structure:
        {
          "order_number": "string (order ID from receipt)",
          "items": [
            {"name": "string", "quantity": 1, "price": 0.0}
          ],
          "subtotal": 0.0,
          "total": 0.0
        }
        
        CRITICAL RULES:
        - Meals with add-ons (e.g., "Chicken McNuggets Meal w Filet-O-Fish") are ONE item
        - Do NOT split meals into separate items
        - Extract exact prices from receipt (HK$ currency)
        - Return ONLY JSON, no other text
        """

        # Call VLM with JSON schema enforcement
        response = model.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_uri}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "order_number": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                    "price": {"type": "number"},
                                },
                                "required": ["name", "quantity", "price"],
                            },
                        },
                        "subtotal": {"type": "number"},
                        "total": {"type": "number"},
                    },
                    "required": ["order_number", "items", "subtotal", "total"],
                },
            },
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=1024,
        )

        # Parse JSON from response
        content = response["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {content}")
            raise ValueError(f"VLM failed to return valid JSON: {e}")

        # Add HKUST validation
        parsed["is_valid"] = _check_hkust_validation(image_bytes)
        parsed["errors"] = []

        return parsed

    except Exception as e:
        logger.error(f"VLM Extraction Error: {e}")
        return {
            "order_number": "",
            "items": [],
            "subtotal": 0.0,
            "total": 0.0,
            "is_valid": False,
            "errors": [str(e)],
        }
