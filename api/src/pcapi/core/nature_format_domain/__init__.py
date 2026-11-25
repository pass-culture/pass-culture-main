from pcapi.core.nature_format_domain import nature_format_domain as nfd_module
from pcapi.core.nature_format_domain.nature_format_domain import DomainEnum
from pcapi.core.nature_format_domain.nature_format_domain import FormatEnum
from pcapi.core.nature_format_domain.nature_format_domain import NatureEnum
from pcapi.core.nature_format_domain.nature_format_domain import get_capabilities
from pcapi.core.nature_format_domain.nature_format_domain import get_mandatory_fields
from pcapi.core.nature_format_domain.nfd_fields import FieldEnum


# Make nature_format_domain module accessible for compatibility
nature_format_domain = nfd_module

__all__ = [
    "DomainEnum",
    "FieldEnum",
    "FormatEnum",
    "NatureEnum",
    "get_capabilities",
    "get_mandatory_fields",
    "nature_format_domain",
]
