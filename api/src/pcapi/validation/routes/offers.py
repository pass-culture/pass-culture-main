from pcapi.models.api_errors import ApiErrors


def check_offer_name_length_is_valid(offer_name: str):  # type: ignore [no-untyped-def]
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error("name", "Le titre de l’offre doit faire au maximum 90 caractères.")
        raise api_error


def check_offer_isbn_is_valid(isbn: str):  # type: ignore [no-untyped-def]
    isbn_length = 13
    if not (isbn and isbn.isnumeric() and len(isbn) == isbn_length):
        api_errors = ApiErrors()
        api_errors.add_error("isbn", "Format d’ISBN incorrect. Exemple de format correct : 9782020427852")
        raise api_errors
