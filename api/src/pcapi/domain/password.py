import re
import secrets
import string

from pcapi.core.users.models import User
from pcapi.domain import password_exceptions


def random_password() -> str:
    uppercase = [secrets.choice(string.ascii_uppercase) for i in range(12)]
    lowercase = [secrets.choice(string.ascii_lowercase) for i in range(12)]
    number = [secrets.choice("0123456789") for i in range(12)]
    special_chars = [secrets.choice("#~|=;:,+><?!@$%^&*_.-")]

    password_chars = uppercase + lowercase + special_chars + number
    secrets._sysrand.shuffle(password_chars)  # type: ignore[attr-defined]

    return "".join(password_chars)


def compute_password_rule_violations(
    new_password: str, new_confirmation_password: str, old_password: str, user: User
) -> dict[str, list[str]]:
    rule_violations: dict[str, list[str]] = {}
    rule_violations |= compute_new_password_violations(user, new_password)
    rule_violations |= compute_old_password_valid_violations(user, old_password)
    rule_violations |= compute_confirmation_password_violations(new_password, new_confirmation_password)
    return rule_violations


def check_password_strength(field_name: str, password: str) -> None:
    violations = compute_password_strength_violations(field_name, password)
    if violations:
        raise password_exceptions.WeakPassword(violations)


def compute_new_password_violations(user: User, new_password: str) -> dict[str, list[str]]:
    violations = []

    password_strength_violations = compute_password_strength_violations("newPassword", new_password)
    if password_strength_violations:
        violations += password_strength_violations["newPassword"]

    different_password_violations = compute_different_password_violations(user, new_password)
    if different_password_violations:
        violations += different_password_violations["newPassword"]

    if violations:
        return {"newPassword": violations}
    return {}


def compute_different_password_violations(user: User, new_password: str) -> dict[str, list[str]]:
    if user.checkPassword(new_password):
        return {"newPassword": ["Le nouveau mot de passe est identique à l’ancien."]}
    return {}


def compute_old_password_valid_violations(user: User, old_password: str) -> dict[str, list[str]]:
    if not user.checkPassword(old_password):
        return {"oldPassword": ["Le mot de passe actuel est incorrect."]}
    return {}


def compute_password_strength_violations(field_name: str, password: str) -> dict[str, list[str]]:
    at_least_one_uppercase = "(?=.*?[A-Z])"
    at_least_one_lowercase = "(?=.*?[a-z])"
    at_least_one_digit = "(?=.*?[0-9])"
    min_length = ".{12,}"

    regex = "^" + at_least_one_uppercase + at_least_one_lowercase + at_least_one_digit + min_length + "$"

    # Special characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    at_least_one_special_char = len(set(password).intersection(set(string.punctuation))) > 0

    if not re.match(regex, password) or not at_least_one_special_char:
        return {
            field_name: [
                "Le mot de passe doit contenir au moins :\n"
                "- 12 caractères\n"
                "- Un chiffre\n"
                "- Une majuscule et une minuscule\n"
                "- Un caractère spécial"
            ]
        }
    return {}


def compute_confirmation_password_violations(
    new_password_value: str, new_confirmation_password_value: str
) -> dict[str, list[str]]:
    if new_password_value != new_confirmation_password_value:
        return {"newConfirmationPassword": ["Les deux mots de passe ne sont pas identiques."]}
    return {}
