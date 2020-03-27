from models import ApiErrors, Stock


def validate(stock: Stock, api_errors: ApiErrors) -> ApiErrors:
    if stock.available is not None and stock.available < 0:
        api_errors.add_error('available', 'Le stock doit être positif')

    return api_errors
