"""
Functions which gets Sirene information using INSEE API and not Entreprise API, or the one configured in SIRENE_BACKEND.
"""

import datetime

from pcapi import settings

from . import models
from .backends.base import get_backend


def get_siren(siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
    """Return information about the requested SIREN.
    Getting the address requires a second HTTP request to the Sirene
    API. Ask it only if needed.
    """
    return get_backend(settings.SIRENE_BACKEND).get_siren(
        siren, with_address=with_address, raise_if_non_public=raise_if_non_public
    )


def get_siren_closed_at_date(date_closed: datetime.date) -> list[str]:
    """Returns the list of SIREN which closure has been declared on the given date.
    Closure date may be the same day, in the past or in the future.
    """
    return get_backend(settings.SIRENE_BACKEND).get_siren_closed_at_date(date_closed)
