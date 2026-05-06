from fastapi import APIRouter

from app.api.v1.endpoints import health, products

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(
    products.product_controller.router,
    prefix="/products",
    tags=["Products"],
)
