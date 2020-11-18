from pcapi.models import ApiErrors
from pcapi.models import BankInformation
from pcapi.models import HasAddressMixin
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import UserSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.models.db import Model
from pcapi.validation.models import bank_information
from pcapi.validation.models import has_address_mixin
from pcapi.validation.models import offer
from pcapi.validation.models import offerer
from pcapi.validation.models import product
from pcapi.validation.models import stock
from pcapi.validation.models import user
from pcapi.validation.models import venue
from pcapi.validation.models.generic import validate_generic


def validate(model: Model) -> ApiErrors:
    api_errors = validate_generic(model)

    if api_errors.errors:
        return api_errors

    if isinstance(model, HasAddressMixin):
        api_errors = has_address_mixin.validate(model, api_errors)

    if isinstance(model, BankInformation):
        api_errors = bank_information.validate(model, api_errors)
    elif isinstance(model, Offer):
        api_errors = offer.validate(model, api_errors)
    elif isinstance(model, Offerer):
        api_errors = offerer.validate(model, api_errors)
    elif isinstance(model, Product):
        api_errors = product.validate(model, api_errors)
    elif isinstance(model, Stock):
        api_errors = stock.validate(model, api_errors)
    elif isinstance(model, UserSQLEntity):
        api_errors = user.validate(model, api_errors)
    elif isinstance(model, VenueSQLEntity):
        api_errors = venue.validate(model, api_errors)

    return api_errors
