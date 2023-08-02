import enum
import typing

import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import BaseModel


SearchTerm = pydantic_v1.constr(min_length=1, max_length=128, strip_whitespace=True)
SortByCol = typing.Literal[
    "id",
    "-id",
    "email",
    "-email",
    "firstName",
    "-firstName",
    "lastName",
    "-lastName",
]

#  SearchTerms = pydantic_v1.conlist(item_type=SearchTerm, min_items=1, max_items=16, unique_items=True)
SearchOrderBy = pydantic_v1.conlist(item_type=SortByCol, min_items=0, max_items=16, unique_items=True)  # type: ignore
SearchPage = pydantic_v1.conint(ge=1, le=100)
SearchPerPage = pydantic_v1.conint(ge=1, le=21)

OrderByCols: typing.Collection[str] = SortByCol.__args__  # type: ignore


class SearchUserModel(BaseModel):
    terms: SearchTerm  # type: ignore
    order_by: SearchOrderBy = ["id"]  # type: ignore
    page: SearchPage = 1  # type: ignore
    per_page: SearchPerPage = 20  # type: ignore

    @pydantic_v1.validator("order_by", pre=True)
    def validate_order_by(cls, value: str) -> list[str]:
        if not value:
            return ["id"]
        return value.split(",")

    @pydantic_v1.root_validator(pre=True)
    def filter_empty_fields(cls, values: dict) -> dict:
        return {k: v for k, v in values.items() if v}


class TypeOptions(enum.Enum):
    OFFERER = "offerer"
    VENUE = "venue"
    USER = "user"


class SearchProModel(SearchUserModel):
    pro_type: TypeOptions

    @pydantic_v1.validator("pro_type", pre=True)
    def validate_pro_type(cls, pro_type: str) -> TypeOptions:
        return TypeOptions[pro_type]
