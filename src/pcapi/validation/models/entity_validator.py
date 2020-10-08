from pcapi.models import ApiErrors, BankInformation, HasAddressMixin, OfferSQLEntity, Offerer, Product, StockSQLEntity, UserSQLEntity, VenueSQLEntity
from pcapi.models.db import Model
from pcapi.validation.models import offer, bank_information, offerer, product, stock, user, venue, has_address_mixin
from pcapi.validation.models.generic import validate_generic


def validate(model: Model) -> ApiErrors:
    api_errors = validate_generic(model)

    if api_errors.errors:
        return api_errors

    if isinstance(model, HasAddressMixin):
        api_errors = has_address_mixin.validate(model, api_errors)

    if isinstance(model, BankInformation):
        api_errors = bank_information.validate(model, api_errors)
    elif isinstance(model, OfferSQLEntity):
        api_errors = offer.validate(model, api_errors)
    elif isinstance(model, Offerer):
        api_errors = offerer.validate(model, api_errors)
    elif isinstance(model, Product):
        api_errors = product.validate(model, api_errors)
    elif isinstance(model, StockSQLEntity):
        api_errors = stock.validate(model, api_errors)
    elif isinstance(model, UserSQLEntity):
        api_errors = user.validate(model, api_errors)
    elif isinstance(model, VenueSQLEntity):
        api_errors = venue.validate(model, api_errors)

    return api_errors
