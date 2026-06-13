import builtins
from typing import TYPE_CHECKING, TypeVar, cast

from fastapi import status

from app.exceptions.exceptions import AppError
from app.models.mock_db import tables

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")
C = TypeVar("C", bound="BaseModel")
PK = TypeVar("PK")


class Service[T: BaseModel, PK, C: BaseModel]:
    default_pk: str = "id"

    def __init__(self, table: str, default_pk: str | None = None) -> None:
        self.table = table
        self.default_pk = default_pk or self.default_pk

        if table not in tables:
            raise AppError(
                name="table_not_found",
                message=f"Table '{table}' does not exist in the database.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Helpers
    def _get_table(self) -> list[T]:
        return tables[self.table]

    def _get_value(self, item: T, key: str) -> object | None:
        if isinstance(item, dict):
            return item.get(key)
        return getattr(item, key, None)

    def _match(self, item: T, **filters) -> bool:
        return all(self._get_value(item, k) == v for k, v in filters.items())

    def list(self) -> list[T]:
        return self._get_table()

    def create(self, item: C) -> T:
        _item = cast("T", item.model_dump())

        self._get_table().append(_item)
        return _item

    def filter(self, *, first: bool = False, **filters) -> builtins.list[T] | T | None:
        results = [item for item in self._get_table() if self._match(item, **filters)]

        if first:
            return results[0] if results else None

        return results

    def retrieve(self, pk: PK) -> T:
        item = self.filter(first=True, **{self.default_pk: pk})

        if item is None:
            raise AppError(
                name="not_found",
                message=f"Item with '{self.default_pk}' = '{pk}' was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return cast("T", item)

    def update(self, pk: PK, payload: dict) -> T:
        data = self._get_table()

        for index, existing in enumerate(data):
            if self._get_value(existing, self.default_pk) == pk:

                if isinstance(existing, dict):
                    updated = {**existing, **payload}
                elif hasattr(existing, "copy"):
                    updated = cast("BaseModel", existing).model_copy(update=payload)
                else:
                    raise AppError(
                        name="invalid_update",
                        message="Unsupported object type for update operation.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                data[index] = cast("T", updated)
                return cast("T", updated)

        raise AppError(
            name="not_found",
            message=f"Cannot update: item with '{self.default_pk}' = '{pk}' does not exist.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    def delete(self, pk: PK) -> None:
        data = self._get_table()

        for index, item in enumerate(data):
            if self._get_value(item, self.default_pk) == pk:
                del data[index]
                return

        raise AppError(
            name="not_found",
            message=f"Cannot delete: item with '{self.default_pk}' = '{pk}' does not exist.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
