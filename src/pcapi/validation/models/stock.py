from pcapi.models import ApiErrors
from pcapi.models import StockSQLEntity


def validate(stock: StockSQLEntity, api_errors: ApiErrors) -> ApiErrors:
    if stock.quantity is not None and stock.quantity < 0:
        api_errors.add_error('quantity', 'Le stock doit être positif')

    return api_errors
