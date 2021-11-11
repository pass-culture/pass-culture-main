from typing import Optional
from typing import Union

from flask import Request

from pcapi.domain.password import check_password_strength
from pcapi.models import ApiErrors


def check_valid_signup_webapp(request: Request) -> None:
    contact_ok = request.json.get("contact_ok")
    password = request.json.get("password")
    email = request.json.get("email")

    _check_email_is_present(email)
    _check_valid_contact_ok(contact_ok)
    _check_password_is_present(password)
    check_password_strength("password", password)


def check_valid_signin(identifier: str, password: str) -> None:
    errors = ApiErrors()
    errors.status_code = 401

    if identifier is None:
        errors.add_error("identifier", "Identifiant manquant")
    if password is None:
        errors.add_error("password", "Mot de passe manquant")

    errors.maybe_raise()


def _check_password_is_present(password: Optional[str]) -> None:
    if not password:
        errors = ApiErrors()
        errors.add_error("password", "Vous devez renseigner un mot de passe.")
        raise errors


def _check_valid_contact_ok(contact_ok: Optional[Union[bool, str]]) -> None:
    if not contact_ok or _contact_ok_is_not_checked(contact_ok):
        errors = ApiErrors()
        errors.add_error("contact_ok", "Vous devez obligatoirement cocher cette case.")
        raise errors


def _check_email_is_present(email: Optional[str]) -> None:
    if email is None:
        errors = ApiErrors()
        errors.add_error("email", "Vous devez renseigner un email.")
        raise errors


def _contact_ok_is_not_checked(contact_ok: Optional[Union[bool, str]]) -> bool:
    contact_ok_is_not_checked_as_bool = contact_ok is not True
    contact_ok_is_not_checked_as_str = str(contact_ok).lower() != "true"
    return contact_ok_is_not_checked_as_bool and contact_ok_is_not_checked_as_str
