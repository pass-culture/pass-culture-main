from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2


class IndexPaginationQueryParams(serialization.ConfiguredBaseModel):
    limit: int = fields.PAGINATION_LIMIT_WITH_DEFAULT
    firstIndex: int = fields.PAGINATION_FIRST_INDEX_WITH_DEFAULT


class IndexPaginationQueryParamsV2(serialization.HttpQueryParamsModel):
    limit: int = fields_v2.PAGINATION_LIMIT_WITH_DEFAULT
    first_index: int = fields_v2.PAGINATION_FIRST_INDEX_WITH_DEFAULT
