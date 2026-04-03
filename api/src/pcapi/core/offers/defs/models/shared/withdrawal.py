from typing import Literal
from typing import Union

import pydantic


class NoTicketWithdrawal(pydantic.BaseModel):
    kind: Literal["NO_TICKET"]
    delay: Literal[None] = None
    has_ticketing_service: bool | None = None


class OnSiteWithdrawal(pydantic.BaseModel):
    kind: Literal["ON_SITE"]
    delay: int
    has_ticketing_service: bool | None = None


class EmailWithdrawal(pydantic.BaseModel):
    kind: Literal["BY_EMAIL"]
    delay: int
    has_ticketing_service: bool | None = None


class InAppWithdrawal(pydantic.BaseModel):
    kind: Literal["IN_APP"]
    delay: None = None
    has_ticketing_service: Literal[True] = True


WithdrawalInfo = Union[NoTicketWithdrawal, OnSiteWithdrawal, EmailWithdrawal, InAppWithdrawal]
