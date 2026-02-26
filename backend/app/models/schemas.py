from pydantic import BaseModel


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float


class OCRResponse(BaseModel):
    order_number: str
    restaurant: str
    items: list[OrderItem]
    subtotal: float
    total: float
    is_valid: bool
    errors: list[str]
    raw_text: list[str]
