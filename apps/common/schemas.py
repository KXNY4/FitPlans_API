from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict

T = TypeVar("T")


def validate_image(v: Any) -> str | None:
    if not v:
        return None
    if hasattr(v, "url"):
        try:
            return v.url
        except ValueError:
            return None
    return str(v)


FileUrl = Annotated[str | None, BeforeValidator(validate_image)]
ImageStr = FileUrl


def validate_queryset(v: Any) -> list[Any]:
    if hasattr(v, "all"):
        return list(v.all())
    return v


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class MessageResponse(BaseModel):
    message: str
    status: str = "success"
