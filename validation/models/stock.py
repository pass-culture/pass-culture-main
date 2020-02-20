from models import ApiErrors, Stock


def validate(stock: Stock, api_errors: ApiErrors) -> ApiErrors:
    if stock.available is not None and stock.available < 0:
        api_errors.add_error('available', 'Le stock doit être positif')

    if stock.endDatetime \
            and stock.beginningDatetime \
            and stock.endDatetime <= stock.beginningDatetime:
        api_errors.add_error('endDatetime', 'La date de fin de l’événement doit être postérieure à la date de début')

    return api_errors
