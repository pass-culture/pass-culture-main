from pydantic import RootModel

from pcapi.core.nature_format_domain import nature_format_domain
from pcapi.routes.serialization import HttpBodyModel


class FormatResponseModel(HttpBodyModel):
    label: str
    format: nature_format_domain.FormatEnum


class NatureFormatDomainResponseModel(HttpBodyModel):
    name: nature_format_domain.NatureEnum
    label: str
    formats: list[FormatResponseModel]


class NatureFormatDomainListResponseModel(RootModel):
    root: list[NatureFormatDomainResponseModel]
