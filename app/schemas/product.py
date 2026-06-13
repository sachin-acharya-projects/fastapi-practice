from pydantic import BaseModel

from app.schemas.base import Base


class ProductCreate(BaseModel):
    label: str
    rate: int
    quantity: int
    unit: str


class Product(ProductCreate, Base):
    pass
