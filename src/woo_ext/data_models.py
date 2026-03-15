import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, field_validator


def is_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


class WooMetaDatum(BaseModel):
    """Models an entry in the woocommerce 'meta_data' field

    'value' must be JSON serializable
    """

    id: int | None = None
    key: str
    value: Any

    @field_validator("value")
    def validate_value(cls, v):  # noqa: N805
        if is_json_serializable(value=v):
            return v
        msg = f"Field 'value' for {cls} of type {type(v)} is not JSON serializable"
        raise ValueError(msg)


class WooOrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    ONHOLD = "on-hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"
    TRASH = "trash"


class WooOrderCondensed(BaseModel):
    system: str = "woocommerce"
    order_id: int
    status: WooOrderStatus
    date_paid: str
    payment_method: str
    product_id: int | None
    mail_address: str
    coupon: str | None

    model_config = {"extra": "allow"}
