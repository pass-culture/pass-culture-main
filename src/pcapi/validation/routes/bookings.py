from typing import Union

from pcapi.models import ApiErrors


def check_email_and_offer_id_for_anonymous_user(email: str, offer_id: int) -> None:
    api_errors = ApiErrors()
    if not email:
        api_errors.add_error(
            "email", "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
        )
    if not offer_id:
        api_errors.add_error("offer_id", "L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]")
    if api_errors.errors:
        raise api_errors


def check_page_format_is_number(page: Union[int, str]):
    page_is_not_decimal = not isinstance(page, int) and not page.isdecimal()

    if page_is_not_decimal or int(page) < 1:
        api_errors = ApiErrors()
        api_errors.add_error("global", f"L'argument 'page' {page} n'est pas valide")
        raise api_errors
