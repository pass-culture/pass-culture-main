from pcapi import settings

from . import models
from .backends.base import get_backend


PROTECTED_DATA_PLACEHOLDER = "[ND]"


def get_siren_open_data(siren: str) -> models.SirenInfo:
    """
    Get INSEE information about the requested SIREN.
    All returned data is public. If entity is "partially diffusible", name and address are replaced by placeholder value.
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_siren_open_data(siren)


def get_siren(siren: str, with_address: bool = True, raise_if_non_public: bool = True) -> models.SirenInfo:
    """
    Get information from INSEE about the requested SIREN.
    Not all returned data is public. If entity is "partially diffusible", name and address are protected data.
    Use get_siren_open_data instead unless access to protected data is strictly necessary.
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_siren(
        siren, with_address=with_address, raise_if_non_public=raise_if_non_public
    )


def get_siret_open_data(siret: str) -> models.SiretInfo:
    """
    Get INSEE information about the requested SIRET.
    All returned data is public. If entity is "partially diffusible", name and address are replaced by placeholder value.
    """
    return get_backend(settings.ENTREPRISE_BACKEND).get_siret_open_data(siret)


def get_siret(siret: str, raise_if_non_public: bool = True) -> models.SiretInfo:
    """
    Get information from INSEE about the requested SIRET.
    Not all returned data is public. If entity is "partially diffusible", name and address are protected data.
    Use get_siret_open_data instead unless access to protected data is strictly necessary.
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


def is_valid_siret(search_input: str | int) -> bool:
    return (
        search_input is not None
        and (isinstance(search_input, int) or search_input.isnumeric())
        and len(str(search_input)) == 14
    )


def is_pass_culture_siret(search_input: str | int) -> bool:
    return str(search_input) == settings.PASS_CULTURE_SIRET
