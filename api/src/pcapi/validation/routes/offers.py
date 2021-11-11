from pcapi.models.api_errors import ApiErrors


def check_offer_name_length_is_valid(offer_name: str):
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def check_offer_id_is_present_in_request(offer_id: str):
    if offer_id is None:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error("global", "Le paramètre offerId est obligatoire")
        errors.maybe_raise()
        raise errors


def check_offer_isbn_is_valid(isbn: str):
    isbn_length = 13
    if not (isbn and isbn.isnumeric() and len(isbn) == isbn_length):
        api_errors = ApiErrors()
        api_errors.add_error("isbn", "Format d’ISBN incorrect. Exemple de format correct : 9782020427852")
        raise api_errors
