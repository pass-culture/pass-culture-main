from pcapi.core.offers.models import Stock
from pcapi.models.api_errors import ApiErrors


def validate(stock: Stock, api_errors: ApiErrors) -> ApiErrors:
    if stock.quantity is not None and stock.quantity < 0:
        api_errors.add_error("quantity", "La quantité doit être positive.")
    if stock.price is not None and stock.price < 0:
        api_errors.add_error("price", "Le prix doit être positif.")

    return api_errors
