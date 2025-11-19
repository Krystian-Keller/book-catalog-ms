"""Very small subset of Pydantic for academic exercises."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


class ValidationError(ValueError):
    """Raised when validation constraints fail."""


@dataclass
class FieldInfo:
    default: Any
    min_length: Optional[int] = None
    ge: Optional[int] = None


def Field(
    default: Any = ...,
    *,
    min_length: Optional[int] = None,
    ge: Optional[int] = None,
) -> "FieldInfo":
    return FieldInfo(default=default, min_length=min_length, ge=ge)


class BaseModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: Dict[str, Any]):
        annotations = namespace.get("__annotations__", {})
        fields: Dict[str, FieldInfo] = {}
        for field_name, _ in annotations.items():
            default = namespace.get(field_name, Field(...))
            if isinstance(default, FieldInfo):
                field_info = default
                namespace.pop(field_name, None)
            else:
                field_info = Field(default=default)
            fields[field_name] = field_info
        namespace["__fields__"] = fields
        return super().__new__(mcls, name, bases, namespace)


class BaseModel(metaclass=BaseModelMeta):
    """Very small subset implementing validation logic."""

    __fields__: Dict[str, FieldInfo]

    def __init__(self, **data: Any) -> None:
        values: Dict[str, Any] = {}
        for name, info in self.__fields__.items():
            if name in data:
                value = data[name]
            elif info.default is ...:
                raise ValidationError(f"Field '{name}' is required")
            else:
                value = info.default
            value = self._apply_constraints(name, value, info)
            values[name] = value
        self.__dict__.update(values)

    def _apply_constraints(self, name: str, value: Any, info: FieldInfo) -> Any:
        if isinstance(value, str) and info.min_length is not None:
            if len(value) < info.min_length:
                raise ValidationError(f"Field '{name}' must have length >= {info.min_length}")
        if isinstance(value, int) and info.ge is not None:
            if value < info.ge:
                raise ValidationError(f"Field '{name}' must be >= {info.ge}")
        return value

    def model_dump(self) -> Dict[str, Any]:
        return dict(self.__dict__)


__all__ = ["BaseModel", "Field", "ValidationError"]
