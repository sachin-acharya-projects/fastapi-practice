from pydantic import Field

from app.schemas.product import Product
from app.schemas.user import User


class Seller(User):
    products: list[Product] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=lambda: ["user", "seller"])
