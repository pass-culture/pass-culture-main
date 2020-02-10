from models import ApiErrors, BankInformation, HasAddressMixin, Offer, Offerer, Product, Stock, User, Venue
from models.db import Model
from validation.models.bank_information import validate_bank_information
from validation.models.generic import validate_generic
from validation.models.has_address_mixin import validate_has_address_mixin
from validation.models import offer
from validation.models.offerer import validate_offerer
from validation.models.product import validate_product
from validation.models.stock import validate_stock
from validation.models.user import validate_user
from validation.models.venue import validate_venue


def validate(model: Model) -> ApiErrors:
    api_errors = validate_generic(model)

    if api_errors.errors:
        return api_errors

    if isinstance(model, HasAddressMixin):
        api_errors = validate_has_address_mixin(model, api_errors)

    if isinstance(model, BankInformation):
        api_errors = validate_bank_information(model, api_errors)
    elif isinstance(model, Offer):
        api_errors = offer.validate(model, api_errors)
    elif isinstance(model, Offerer):
        api_errors = validate_offerer(model, api_errors)
    elif isinstance(model, Product):
        api_errors = validate_product(model, api_errors)
    elif isinstance(model, Stock):
        api_errors = validate_stock(model, api_errors)
    elif isinstance(model, User):
        api_errors = validate_user(model, api_errors)
    elif isinstance(model, Venue):
        api_errors = validate_venue(model, api_errors)

    return api_errors
