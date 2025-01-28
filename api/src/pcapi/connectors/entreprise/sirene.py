"""
Legacy functions which gets Sirene information using INSEE API directly, for public information only.
Or the one configured in SIRENE_BACKEND.
Not through API Entreprise. No protected data.
Can be used to retrieve information for autocomplete features in PC Pro.
"""

import datetime

from pcapi import settings
from pcapi.models import feature

from . import models
from .backends.base import get_backend


def get_siren(siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
    """Return information about the requested SIREN.

    Getting the address requires a second HTTP request to the Sirene
    API. Ask it only if needed.
    """
    _check_feature_flag()
    return get_backend(settings.SIRENE_BACKEND).get_siren(
        siren, with_address=with_address, raise_if_non_public=raise_if_non_public
    )


def get_siret(siret: str, raise_if_non_public: bool = True) -> models.SiretInfo:
    """Return information about the requested SIRET."""
    _check_feature_flag()
    return get_backend(settings.SIRENE_BACKEND).get_siret(siret, raise_if_non_public)


def siret_is_active(siret: str, raise_if_non_public: bool = True) -> bool:
    """Return whether the requested SIRET is active."""
    siret_info = get_siret(siret, raise_if_non_public)
    return siret_info.active


def get_siren_closed_at_date(date_closed: datetime.date) -> list[str]:
    """Returns the list of SIREN which have been closed exactly on the given date."""
    return get_backend(settings.SIRENE_BACKEND).get_siren_closed_at_date(date_closed)


def _check_feature_flag() -> None:
    if feature.FeatureToggle.DISABLE_ENTERPRISE_API.is_active():
        raise feature.DisabledFeatureError("DISABLE_ENTERPRISE_API is activated")
