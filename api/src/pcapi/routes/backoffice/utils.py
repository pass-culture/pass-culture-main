import typing

from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.backoffice.serialization import PaginatedResponse
from pcapi.routes.serialization import BaseModel


def get_user_or_error(user_id: int, error_code: int = 400) -> users_models.User:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"}, status_code=error_code)

    return user


def build_paginated_response(
    page: int,
    pages: int,
    total: int,
    sort: str | None,
    data: list[BaseModel],
    response_model: typing.Type[PaginatedResponse] = PaginatedResponse,
) -> PaginatedResponse:
    response = response_model(pages=pages, total=total, page=page, size=len(data), sort=sort, data=data)
    return response
