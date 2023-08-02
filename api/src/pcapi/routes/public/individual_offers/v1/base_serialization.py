import pydantic.v1 as pydantic_v1

from pcapi.routes import serialization


class PaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = pydantic_v1.Field(50, le=50, gt=0, description="Maximum number of items per page.")
    page: int = pydantic_v1.Field(1, ge=1, description="Page number of the items to return.")


class IndexPaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = pydantic_v1.Field(50, le=50, gt=0, description="Maximum number of items per page.")
    firstIndex: int = pydantic_v1.Field(1, ge=1, description="Index of the first item in page.")
