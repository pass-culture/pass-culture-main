from pcapi.models import ApiErrors
from pcapi.models import Stock


def validate(stock: Stock, api_errors: ApiErrors) -> ApiErrors:
    if stock.quantity is not None and stock.quantity < 0:
        api_errors.add_error("quantity", "Le stock doit être positif")
    if stock.price is not None and stock.price < 0:
        api_errors.add_error("price", "Le prix doit être positif")

    return api_errors
