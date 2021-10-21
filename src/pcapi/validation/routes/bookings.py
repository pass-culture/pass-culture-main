from typing import Optional

from pcapi.models import ApiErrors


def check_email_and_offer_id_for_anonymous_user(email: Optional[str], offer_id: Optional[int]) -> None:
    api_errors = ApiErrors()
    if not email:
        api_errors.add_error(
            "email", "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
        )
    if not offer_id:
        api_errors.add_error("offer_id", "L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]")
    if api_errors.errors:
        raise api_errors
