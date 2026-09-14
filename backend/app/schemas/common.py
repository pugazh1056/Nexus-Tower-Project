"""Request models shared by the API modules."""

from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class AuthRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class AuthLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class ResourcePayload(FlexibleModel):
    data: dict[str, Any] | None = None
