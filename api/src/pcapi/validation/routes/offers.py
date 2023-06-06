from pcapi.models.api_errors import ApiErrors


def check_offer_name_length_is_valid(offer_name: str) -> None:
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def check_collective_offer_name_length_is_valid(offer_name: str) -> None:
    max_offer_name_length = 110
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 110 caractères.")
        raise api_error


def check_offer_ean_is_valid(ean: str | None) -> None:
    ean_length = 13
    if not ean or not (ean and ean.isnumeric() and len(ean) == ean_length):
        api_errors = ApiErrors()
        api_errors.add_error("ean", "Format d’EAN incorrect. Exemple de format correct : 9782020427852")
        raise api_errors
