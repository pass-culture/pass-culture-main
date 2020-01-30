from models import ApiErrors
from models.db import Model


def get_stock_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.available is not None and model.available < 0:
        api_errors.add_error('available', 'Le stock doit être positif')

    if model.endDatetime \
            and model.beginningDatetime \
            and model.endDatetime <= model.beginningDatetime:
        api_errors.add_error('endDatetime', 'La date de fin de l’événement doit être postérieure à la date de début')

    return api_errors
