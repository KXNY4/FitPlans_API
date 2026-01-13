import re
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from apps.common.schemas import BaseSchema, ImageStr


class RegisterIn(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str
    first_name: str = Field(default="", max_length=50)
    last_name: str = Field(default="", max_length=50)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username может содержать только буквы, цифры и _")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать заглавную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать цифру")
        return v

    def model_post_init(self, __context) -> None:
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserUpdateIn(BaseModel):
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    height: int | None = Field(None, ge=50, le=300)
    weight: Decimal | None = Field(None, ge=20, le=500)
    goal: Literal["WEIGHT_LOSS", "MUSCLE_GAIN", "STRENGTH", "ENDURANCE", "MAINTENANCE"] | None = None


class UserProgressIn(BaseModel):
    weight: Decimal = Field(..., ge=20, le=500)
    date: date
    notes: str = Field(default="", max_length=500)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        from datetime import date as date_today

        if v > date_today.today():
            raise ValueError("Дата не может быть в будущем")
        return v


class TokensOut(BaseModel):
    access: str
    refresh: str


class UserOut(BaseSchema):
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    height: int | None = None
    weight: Decimal | None = None
    goal: str | None = None
    avatar: ImageStr = None
    created_at: datetime = Field(validation_alias="date_joined")


class UserShortOut(BaseSchema):
    id: UUID
    first_name: str
    last_name: str
    avatar: ImageStr = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class AuthOut(BaseModel):
    user: UserOut
    tokens: TokensOut


class UserProgressOut(BaseSchema):
    id: int
    weight: Decimal
    date: date
    notes: str
