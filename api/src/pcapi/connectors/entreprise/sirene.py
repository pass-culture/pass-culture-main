"""
Functions which gets Sirene information using INSEE API and not Entreprise API, or the one configured in SIRENE_BACKEND.
"""

import datetime

from pcapi import settings

from .backends.base import get_backend


def get_siren_closed_at_date(date_closed: datetime.date) -> list[str]:
    """Returns the list of SIREN which closure has been declared on the given date.
    Closure date may be the same day, in the past or in the future.
    """
    return get_backend(settings.SIRENE_BACKEND).get_siren_closed_at_date(date_closed)
