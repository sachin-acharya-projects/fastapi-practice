from collections.abc import Callable
from enum import Enum
from typing import TypeVar, cast

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel

from app.services.base import Service

T = TypeVar("T", bound=BaseModel)
C = TypeVar("C", bound=BaseModel)
PK = TypeVar("PK")


def body_model(model: type[BaseModel]) -> Callable[[dict], BaseModel]:
    def dependency(payload: dict) -> BaseModel:
        return model(**payload)

    return dependency


class BaseController[T: BaseModel, PK, C: BaseModel]:
    def __init__(
        self,
        *,
        service: Service[T, PK, C],
        schema: type[BaseModel],
        create_schema: type[BaseModel] | None = None,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
    ) -> None:
        if not issubclass(schema, BaseModel):
            raise TypeError("`schema` must be a subclass of `pydantic.BaseModel`")

        if create_schema and not issubclass(create_schema, BaseModel):
            raise TypeError(
                "`create_schema` must be a subclass of `pydantic.BaseModel`"
            )

        self.service = service
        self.schema = schema
        self.create_schema = create_schema or self.schema
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
            status_code=status.HTTP_201_CREATED,
            dependencies=[],
        )

        self.router.add_api_route(
            "/{pk}",
            self.update,
            methods=["PUT"],
            response_model=self.schema,
            response_model_exclude_none=True,
        )

        self.router.add_api_route(
            "/{pk}",
            self.delete,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
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

    def create(self, item: dict = Body(...)) -> T:
        validated = self.create_schema(**item)
        return self.service.create(cast("C", validated))

    def update(self, pk: PK, payload: dict = Body(...)) -> T:
        try:
            return self.service.update(pk, payload)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from None

    def delete(self, pk: PK) -> None:
        try:
            self.service.delete(pk)
            return
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from None
