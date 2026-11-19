from pydantic import RootModel

from pcapi.core.nature_format_domain import nature_format_domain
from pcapi.routes.serialization import HttpBodyModel


class DomainResponseModel(HttpBodyModel):
    label: str
    domain: nature_format_domain.DomainEnum


class FormatResponseModel(HttpBodyModel):
    label: str
    format: nature_format_domain.FormatEnum
    domains: list[DomainResponseModel]


class NatureFormatDomainResponseModel(HttpBodyModel):
    nature: nature_format_domain.NatureEnum
    label: str
    formats: list[FormatResponseModel]


class NatureFormatDomainListResponseModel(RootModel):
    root: list[NatureFormatDomainResponseModel]
