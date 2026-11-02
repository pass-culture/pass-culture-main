from pcapi.core.nature_format_domain import nature_format_domain
from pcapi.routes.serialization import HttpBodyModel


class GetCapabilitiesResponseModel(HttpBodyModel):
    capabilities: list[str]


class GetCapabilitiesQueryModel(HttpBodyModel):
    nature: nature_format_domain.NatureEnum
    format: nature_format_domain.FormatEnum
