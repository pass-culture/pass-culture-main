import pydantic

from pcapi.routes import serialization


class PaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = pydantic.Field(50, le=50, gt=0, description="Maximum number of items per page.")
    page: int = pydantic.Field(1, ge=1, description="Page number of the items to return.")
