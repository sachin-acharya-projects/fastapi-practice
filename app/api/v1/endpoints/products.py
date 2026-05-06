from app.api.base.controller import BaseController
from app.schemas.product import Product
from app.services.product import product_service

product_controller = BaseController(
    service=product_service,
    schema=Product,
)
