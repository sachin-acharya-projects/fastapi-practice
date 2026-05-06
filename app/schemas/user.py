from datetime import UTC, datetime

from pydantic import EmailStr, Field

from app.schemas.base import Base


class User(Base):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = Field(None, max_length=100)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    roles: list[str] = Field(default_factory=lambda: ["user"])
