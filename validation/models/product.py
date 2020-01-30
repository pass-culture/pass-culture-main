from models import ApiErrors
from models.db import Model


def get_product_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.isDigital and model.type_can_only_be_offline():
        api_errors.add_error('url', f'Une offre de type {model.get_label_from_type_string()} ne peut pas être numérique')

    return api_errors
