from app.schemas.product import Product
from app.services.base import Service

product_service = Service[Product, str]("products")
