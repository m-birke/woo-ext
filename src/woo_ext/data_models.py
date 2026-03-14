import json
from typing import Any

from pydantic import BaseModel, field_validator


def is_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


class WooMetaDatum(BaseModel):
    """
    value must be JSON serializable
    """

    id: int | None = None
    key: str
    value: Any

    @field_validator("value")
    def validate_value(self, v):
        if is_json_serializable(value=v):
            return v
        msg = f"Field 'value' for {self} of type {type(v)} is not JSON serializable"
        raise ValueError(msg)
