import dataclasses
import datetime
import re
import typing

import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.finance import models as finance_models
from pcapi.core.users import models as users_models
from pcapi.models.pc_object import BaseQuery
from pcapi.models.pc_object import PcObject
from pcapi.routes.backoffice.forms import search as search_forms


class UrlForPartial(typing.Protocol):
    def __call__(self, page: int) -> str: ...


@dataclasses.dataclass
class PaginatedQuery:
    items: list[PcObject]
    page: int
    pages: int
    per_page: int
    total: int


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


def paginate(query: BaseQuery, page: int = 1, per_page: int = 20) -> PaginatedQuery:
    if page < 1:
        raise NotFound()

    offset = (page - 1) * per_page
    total = query.count()

    if offset:
        query = query.offset(offset)

    items = query.limit(per_page).all()

    if total and not items:
        raise NotFound()
    return PaginatedQuery(
        items=items,
        page=page,
        pages=(total // per_page + (1 if (total % per_page) else 0)),
        per_page=per_page,
        total=total,
    )


def split_terms(search_query: str) -> list[str]:
    return re.split(r"[,;\s]+", search_query)


def apply_filter_on_beneficiary_status(query: BaseQuery, account_search_filters: list[str]) -> BaseQuery:
    query = query.outerjoin(
        finance_models.Deposit,
        sa.and_(
            users_models.User.id == finance_models.Deposit.userId,
            finance_models.Deposit.expirationDate > datetime.datetime.utcnow(),
        ),
    )

    if not account_search_filters:
        return query

    or_filters: list = []

    if search_forms.AccountSearchFilter.PASS_17_V3.name in account_search_filters:
        or_filters.append(
            sa.and_(
                finance_models.Deposit.type == finance_models.DepositType.GRANT_17_18,
                users_models.User.has_underage_beneficiary_role,
                users_models.User.isActive.is_(True),
            )
        )

    if search_forms.AccountSearchFilter.PASS_18_V3.name in account_search_filters:
        or_filters.append(
            sa.and_(
                finance_models.Deposit.type == finance_models.DepositType.GRANT_17_18,
                users_models.User.has_beneficiary_role,
                users_models.User.isActive.is_(True),
            )
        )
    if search_forms.AccountSearchFilter.PASS_15_17.name in account_search_filters:
        or_filters.append(
            sa.and_(
                finance_models.Deposit.type != finance_models.DepositType.GRANT_17_18,
                users_models.User.has_underage_beneficiary_role,
                users_models.User.isActive.is_(True),
            )
        )

    if search_forms.AccountSearchFilter.PASS_18.name in account_search_filters:
        or_filters.append(
            sa.and_(
                finance_models.Deposit.type != finance_models.DepositType.GRANT_17_18,
                users_models.User.has_beneficiary_role,
                users_models.User.isActive.is_(True),
            )
        )

    if search_forms.AccountSearchFilter.PUBLIC.name in account_search_filters:
        or_filters.append(
            sa.and_(
                sa.not_(users_models.User.is_beneficiary),
                users_models.User.isActive.is_(True),
            )
        )

    if search_forms.AccountSearchFilter.SUSPENDED.name in account_search_filters:
        or_filters.append(users_models.User.isActive.is_(False))

    return query.filter(sa.or_(*or_filters)) if or_filters else query
