from pcapi.models.api_errors import ApiErrors


def check_email_and_offer_id_for_anonymous_user(email: str | None, offer_id: int | None) -> None:
    api_errors = ApiErrors()
    if not email:
        api_errors.add_error(
            "email", "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
        )
    if not offer_id:
        api_errors.add_error("offer_id", "L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]")
    if api_errors.errors:
        raise api_errors
