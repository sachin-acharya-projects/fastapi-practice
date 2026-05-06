"""
Mock database that uses in-memory storage for storing the database
"""

from typing import TypedDict

from app.schemas.product import Product
from app.schemas.seller import Seller
from app.schemas.user import User


class TableSchema(TypedDict):
    users: list[User]
    sellers: list[Seller]
    products: list[Product]


tables: TableSchema = {
    "users": [],
    "sellers": [],
    "products": [],
}
