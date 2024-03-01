from pcapi import settings

from . import models
from .backends.base import get_backend


def get_siren(siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
    """
    Get information from INSEE about the requested SIREN.
    Returned data is public, except name and address when "non-diffusible"
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_siren(
        siren, with_address=with_address, raise_if_non_public=raise_if_non_public
    )


def get_siret(siret: str, raise_if_non_public: bool = True) -> models.SiretInfo:
    """
    Get information from INSEE about the requested SIRET.
    Returned data is public, except name and address when "non-diffusible"
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_siret(siret, raise_if_non_public=raise_if_non_public)


def get_rcs(siren: str) -> models.RCSInfo:
    """
    Get information from the Registre du Commerce et des Sociétés (Kbis).
    Returned data is public.
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_rcs(siren)


def get_urssaf(siren: str) -> models.UrssafInfo:
    """
    Get status of "attestation de vigilance" (URSSAF).
    This is always confidential information, with restricted access.
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_urssaf(siren)


def get_dgfip(siren: str) -> models.DgfipInfo:
    """
    Get status of "attestation de régularité fiscale" (DGFIP).
    This is always confidential information, with restricted access.
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_dgfip(siren)


EI_CATEGORY_CODE = 1000
PUBLIC_CATEGORIES_MIN_CODE = 7000


def siren_is_individual_or_public(siren_info: models.SirenInfo) -> bool:
    # This implementation is very basic and may be updated later depending on errors when calling get_dgfip()
    legal_category_code = int(siren_info.legal_category_code)
    return (legal_category_code == EI_CATEGORY_CODE) or (legal_category_code > PUBLIC_CATEGORIES_MIN_CODE)
