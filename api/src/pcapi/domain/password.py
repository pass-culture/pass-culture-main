import re
import secrets
import string

from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors


def random_password() -> str:
    uppercase = [secrets.choice(string.ascii_uppercase) for i in range(12)]
    lowercase = [secrets.choice(string.ascii_lowercase) for i in range(12)]
    number = [secrets.choice("0123456789") for i in range(12)]
    special_chars = [secrets.choice("#~|=;:,+><?!@$%^&*_.-")]

    password_chars = uppercase + lowercase + special_chars + number
    secrets._sysrand.shuffle(password_chars)  # type: ignore[attr-defined]

    return "".join(password_chars)


def check_password_validity(new_password: str, new_confirmation_password: str, old_password: str, user: User) -> None:
    api_errors = ApiErrors()
    _ensure_new_password_is_strong_enough("newPassword", new_password, api_errors)
    _ensure_given_old_password_is_correct(user, old_password, api_errors)
    _ensure_new_password_is_different_from_old(user, new_password, api_errors)
    _ensure_confirmation_password_is_same_as_new_password(new_password, new_confirmation_password, api_errors)
    if len(api_errors.errors) > 0:
        raise api_errors


def check_password_strength(key: str, password: str) -> None:
    api_errors = ApiErrors()
    _ensure_new_password_is_strong_enough(key, password, api_errors)
    if len(api_errors.errors) > 0:
        raise api_errors


def _ensure_new_password_is_different_from_old(user: User, new_password: str, errors: ApiErrors) -> None:
    if user.checkPassword(new_password):
        errors.add_error("newPassword", "Le nouveau mot de passe est identique à l’ancien.")


def _ensure_given_old_password_is_correct(user: User, old_password: str, errors: ApiErrors) -> None:
    if not user.checkPassword(old_password):
        errors.add_error("oldPassword", "Le mot de passe actuel est incorrect.")


def _ensure_new_password_is_strong_enough(field_name: str, field_value: str, errors: ApiErrors) -> None:
    at_least_one_uppercase = "(?=.*?[A-Z])"
    at_least_one_lowercase = "(?=.*?[a-z])"
    at_least_one_digit = "(?=.*?[0-9])"
    min_length = ".{12,}"

    regex = "^" + at_least_one_uppercase + at_least_one_lowercase + at_least_one_digit + min_length + "$"

    # Special characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    at_least_one_special_char = len(set(field_value).intersection(set(string.punctuation))) > 0

    if not re.match(regex, field_value) or not at_least_one_special_char:
        errors.add_error(
            field_name,
            "Le mot de passe doit contenir au moins :\n"
            "- 12 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial",
        )


def _ensure_confirmation_password_is_same_as_new_password(
    new_password_value: str, new_confirmation_password_value: str, errors: ApiErrors
) -> None:
    if new_password_value != new_confirmation_password_value:
        errors.add_error("newConfirmationPassword", "Les deux mots de passe ne sont pas identiques.")
