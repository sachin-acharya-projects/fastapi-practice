from app.schemas.product import Product, ProductCreate
from app.services.base import Service

product_service = Service[Product, str, ProductCreate]("products")
