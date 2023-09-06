import typing

from flask_sqlalchemy import BaseQuery
from flask_sqlalchemy import Pagination

from .serialization import search


SearchFunc = typing.Callable[[str, list[str] | None], BaseQuery]


def fetch_paginated_rows(search_func: SearchFunc, search_model: search.SearchUserModel) -> Pagination:
    query = search_func(search_model.terms, search_model.order_by)
    return query.paginate(page=search_model.page, per_page=search_model.per_page, error_out=False)


class UrlForPartial(typing.Protocol):
    def __call__(self, page: int) -> str:
        ...


PAGINATION_STEPS = 7
PAGINATION_SIDE_STEPS = PAGINATION_STEPS // 2


def pagination_links(partial_func: UrlForPartial, current_page: int, pages_total: int) -> list[tuple[int, str]]:
    start_page = current_page - PAGINATION_SIDE_STEPS
    end_page = current_page + PAGINATION_SIDE_STEPS

    if start_page < 1:
        distance = 1 - start_page
        start_page = 1
        end_page = min(end_page + distance, pages_total)
    elif end_page > pages_total:
        distance = end_page - pages_total
        end_page = pages_total
        start_page = max(start_page - distance, 1)

    return [(page, partial_func(page=page)) for page in range(start_page, end_page + 1)]
