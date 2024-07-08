import pydantic.v1 as pydantic_v1

from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields


class PaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = pydantic_v1.Field(50, le=50, gt=0, description="Maximum number of items per page.")
    page: int = pydantic_v1.Field(1, ge=1, description="Page number of the items to return.")


class IndexPaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = fields.PAGINATION_LIMIT_WITH_DEFAULT
    firstIndex: int = fields.PAGINATION_FIRST_INDEX_WITH_DEFAULT
