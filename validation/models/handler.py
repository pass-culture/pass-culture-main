from models import ApiErrors, BankInformation, HasAddressMixin, Offer, Offerer, Product, Stock, User, Venue
from models.db import Model
from validation.models.bank_information import get_bank_information_errors
from validation.models.generic import generic_errors
from validation.models.has_address_mixin import get_has_address_mixin_errors
from validation.models.offer import get_offer_errors
from validation.models.offerer import get_offerer_errors
from validation.models.product import get_product_errors
from validation.models.stock import get_stock_errors
from validation.models.user import get_user_errors
from validation.models.venue import get_venue_errors


def errors(model: Model) -> ApiErrors:
    api_errors = generic_errors(model)

    if api_errors.errors:
        return api_errors

    if isinstance(model, HasAddressMixin):
        api_errors = get_has_address_mixin_errors(model, api_errors)

    if isinstance(model, BankInformation):
        api_errors = get_bank_information_errors(model, api_errors)
    elif isinstance(model, Offer):
        api_errors = get_offer_errors(model, api_errors)
    elif isinstance(model, Offerer):
        api_errors = get_offerer_errors(model, api_errors)
    elif isinstance(model, Product):
        api_errors = get_product_errors(model, api_errors)
    elif isinstance(model, Stock):
        api_errors = get_stock_errors(model, api_errors)
    elif isinstance(model, User):
        api_errors = get_user_errors(model, api_errors)
    elif isinstance(model, Venue):
        api_errors = get_venue_errors(model, api_errors)

    return api_errors
