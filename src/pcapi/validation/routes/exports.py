import re

from pcapi.models import ApiErrors
from pcapi.models.api_errors import ForbiddenError


def check_user_is_admin(user):
    if not user.isAdmin:
        api_errors = ForbiddenError()
        api_errors.add_error("isAdmin", "Vous devez être admin")
        raise api_errors


def check_get_venues_params(param: {}) -> bool:
    if param.get("sirens", None):
        _check_sirens(param["sirens"])

    if param.get("dpts", []):
        _check_dpts_list(param["dpts"])

    if param.get("has_validated_offerer", None):
        _check_has_validated_offerer_param(param["has_validated_offerer"])

    if param.get("zip_codes", []):
        _check_zip_codes_list(param["zip_codes"])

    if param.get("from_date", None):
        _check_date_format(param["from_date"])

    if param.get("to_date", None):
        _check_date_format(param["to_date"])

    if param.get("has_siret", None):
        _check_has_siret_param(param["has_siret"])

    if param.get("is_virtual", None):
        _check_is_virtual_param(param["is_virtual"])

    if param.get("offer_status", None):
        _check_offer_status_param(param["offer_status"])

    if param.get("is_validated", None):
        _check_is_validated_param(param["is_validated"])

    if param.get("has_offerer_with_siren", None):
        _check_has_offerer_with_siren_param(param["has_offerer_with_siren"])

    if param.get("has_validated_user_offerer", None):
        _check_has_validated_user_offerer_param(param["has_validated_user_offerer"])

    if param.get("has_validated_user", None):
        _check_has_validated_user_param(param["has_validated_user"])

    return True


def check_get_offerers_params(param: {}) -> bool:
    if param.get("sirens", None):
        _check_sirens(param["sirens"])

    if param.get("dpts", None):
        _check_dpts_list(param["dpts"])

    if param.get("zip_codes", None):
        _check_zip_codes_list(param["zip_codes"])

    if param.get("from_date", None):
        _check_date_format(param["from_date"])

    if param.get("to_date", None):
        _check_date_format(param["to_date"])

    if param.get("has_siren", None):
        _check_has_siren_param(param["has_siren"])

    if param.get("has_not_virtual_venue", None):
        _check_has_not_virtual_venue_param(param["has_not_virtual_venue"])

    if param.get("has_validated_venue", None):
        _check_has_validated_venue_param(param["has_validated_venue"])

    if param.get("has_venue_with_siret", None):
        _check_has_venue_with_siret_param(param["has_venue_with_siret"])

    if param.get("offer_status", None):
        _check_offer_status_param(param["offer_status"])

    if param.get("is_validated", None):
        _check_is_validated_param(param["is_validated"])

    if param.get("has_validated_user", None):
        _check_has_validated_user_param(param["has_validated_user"])

    if param.get("has_bank_information", None):
        _check_has_bank_information_param(param["has_bank_information"])

    if param.get("is_active", None):
        _check_is_active_param(param["is_active"])

    if param.get("has_validated_user_offerer", None):
        _check_has_validated_user_offerer_param(param["has_validated_user_offerer"])

    return True


def _check_date_format(date: str) -> bool:
    if re.search(r"^(\d){4}-(\d){2}-(\d){2}$", date):
        return True
    api_errors = ApiErrors()
    api_errors.add_error("date_format", "to_date and from_date are of type yyyy-mm-dd")
    raise api_errors


def _check_sirens(sirens: []) -> bool:
    if not type(sirens) == []:
        api_errors = ApiErrors()
        api_errors.add_error("sirens", 'sirens is a list of 9 digits : ["123456789", "789654123"]')
    for siren in sirens:
        if not re.search(r"^(\d){9}$", siren):
            api_errors = ApiErrors()
            api_errors.add_error("sirens", 'sirens is a list of 9 digits : ["123456789", "789654123"]')
            raise api_errors
    return True


def _check_dpts_list(dpts_list: []) -> bool:
    if not type(dpts_list) == []:
        api_errors = ApiErrors()
        api_errors.add_error(
            "dpts",
            'dpts is a list of type xx or xxx (2 or 3 digits), or 2A, or 2B :\
            ["34", "37"]',
        )
    for dpts in dpts_list:
        if not re.search(r"^(\d){2}$|^2{1}(a|b|A|B)$|^(\d){3}$", dpts):
            api_errors = ApiErrors()
            api_errors.add_error(
                "dpts",
                'dpts is a list of type xx or xxx (2 or 3 digits), or 2A, or 2B :\
                ["34", "37"]',
            )
            raise api_errors
    return True


def _check_zip_codes_list(zip_codes_list: []) -> bool:
    if not type(zip_codes_list) == []:
        api_errors = ApiErrors()
        api_errors.add_error(
            "zip_codes",
            'zip_codes is a list of type xxxxx (5 digits, ex: 78140 ou 2a000) : \
        ["78140", "69007"]',
        )
    for zip_code in zip_codes_list:
        if not re.search(r"^(\d){5}$|^2{1}(a|b|A|B)(\d){3}$", zip_code):
            api_errors = ApiErrors()
            api_errors.add_error(
                "zip_codes",
                'zip_codes is a list of type xxxxx (5 digits, ex: 78140 ou 2a000) : \
        ["78140", "69007"]',
            )
            raise api_errors
    return True


def _check_has_validated_offerer_param(has_validated_offerer) -> bool:
    if type(has_validated_offerer) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_validated_offerer", "has_validated_offerer is a boolean, it accepts True or False")
    raise api_errors


def _check_is_virtual_param(is_virtual) -> bool:
    if type(is_virtual) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("is_virtual", "is_virtual is a boolean, it accepts True or False")
    raise api_errors


def _check_offer_status_param(offer_status: str) -> bool:
    valid_param = ["ALL", "VALID", "WITHOUT", "EXPIRED"]
    for elem in valid_param:
        if offer_status == elem:
            return True
    api_errors = ApiErrors()
    api_errors.add_error("offer_status", "offer_status accepte ALL ou VALID ou WITHOUT ou EXPIRED")
    raise api_errors


def _check_has_siret_param(has_siret) -> bool:
    if type(has_siret) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_siret", "has_siret is a boolean, it accepts True or False")
    raise api_errors


def _check_is_validated_param(is_validated) -> bool:
    if type(is_validated) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("is_validated", "is_validated is a boolean, it accepts True or False")
    raise api_errors


def _check_has_offerer_with_siren_param(has_offerer_with_siren) -> bool:
    if type(has_offerer_with_siren) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_offerer_with_siren", "has_offerer_with_siren is a boolean, it accepts True or False")
    raise api_errors


def _check_has_validated_user_offerer_param(has_validated_user_offerer) -> bool:
    if type(has_validated_user_offerer) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error(
        "has_validated_user_offerer", "has_validated_user_offerer is a boolean, it accepts True or False"
    )
    raise api_errors


def _check_has_validated_user_param(has_validated_user) -> bool:
    if type(has_validated_user) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_validated_user", "has_validated_user is a boolean, it accepts True or False")
    raise api_errors


def _check_has_siren_param(has_siren) -> bool:
    if type(has_siren) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_siren", "has_siren is a boolean, it accepts True or False")
    raise api_errors


def _check_has_not_virtual_venue_param(has_not_virtual_venue) -> bool:
    if type(has_not_virtual_venue) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_not_virtual_venue", "has_not_virtual_venue is a boolean, it accepts True or False")
    raise api_errors


def _check_has_validated_venue_param(has_validated_venue) -> bool:
    if type(has_validated_venue) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_validated_venue", "has_validated_venue is a boolean, it accepts True or False")
    raise api_errors


def _check_has_venue_with_siret_param(has_venue_with_siret) -> bool:
    if type(has_venue_with_siret) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_venue_with_siret", "has_venue_with_siret is a boolean, it accepts True or False")
    raise api_errors


def _check_has_bank_information_param(has_bank_information) -> bool:
    if type(has_bank_information) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("has_bank_information", "has_bank_information is a boolean, it accepts True or False")
    raise api_errors


def _check_is_active_param(is_active) -> bool:
    if type(is_active) == bool:
        return True
    api_errors = ApiErrors()
    api_errors.add_error("is_active", "is_active is a boolean, it accepts True or False")
    raise api_errors
