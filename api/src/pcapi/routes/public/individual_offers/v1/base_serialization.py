from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields


class IndexPaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = fields.PAGINATION_LIMIT_WITH_DEFAULT
    firstIndex: int = fields.PAGINATION_FIRST_INDEX_WITH_DEFAULT
