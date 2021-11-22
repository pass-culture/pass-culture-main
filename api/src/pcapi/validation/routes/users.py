from pcapi.models import ApiErrors


def check_valid_signin(identifier: str, password: str) -> None:
    errors = ApiErrors()
    errors.status_code = 401

    if identifier is None:
        errors.add_error("identifier", "Identifiant manquant")
    if password is None:
        errors.add_error("password", "Mot de passe manquant")

    errors.maybe_raise()
