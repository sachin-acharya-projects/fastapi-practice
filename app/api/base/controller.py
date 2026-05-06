from enum import Enum
from typing import TypeVar

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.base import Service

T = TypeVar("T", bound=BaseModel)
PK = TypeVar("PK")


class BaseController[T: BaseModel, PK]:
    def __init__(
        self,
        *,
        service: Service[T, PK],
        schema: type[BaseModel],
        prefix: str = "",
        tags: list[str | Enum] | None = None,
    ) -> None:
        if not issubclass(schema, BaseModel):
            raise TypeError("`schema` must be a subclass of `pydantic.BaseModel`")

        self.service = service
        self.schema = schema
        self.router = APIRouter(prefix=prefix, tags=tags or [])

        self._register_routes()

    # Route registration
    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/",
            self.list,
            methods=["GET"],
            response_model=list[self.schema],
        )

        self.router.add_api_route(
            "/{pk}",
            self.retrieve,
            methods=["GET"],
            response_model=self.schema,
        )

        self.router.add_api_route(
            "/",
            self.create,
            methods=["POST"],
            response_model=self.schema,
        )

        self.router.add_api_route(
            "/{pk}",
            self.update,
            methods=["PUT"],
            response_model=self.schema,
        )

        self.router.add_api_route(
            "/{pk}",
            self.delete,
            methods=["DELETE"],
        )

    # Handlers
    def list(self) -> list[T]:
        return self.service.list()

    def retrieve(self, pk: PK) -> T:
        try:
            return self.service.retrieve(pk)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from None

    def create(self, item: T) -> T:
        return self.service.create(item)

    def update(self, pk: PK, payload: dict) -> T:
        try:
            return self.service.update(pk, payload)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from None

    def delete(self, pk: PK) -> dict:
        try:
            self.service.delete(pk)
            return {"detail": "Item deleted successfully."}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from None
