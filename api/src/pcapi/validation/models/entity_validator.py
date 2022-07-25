from pcapi.core.finance.models import BankInformation
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors
from pcapi.models.has_address_mixin import HasAddressMixin
from pcapi.validation.models import bank_information
from pcapi.validation.models import has_address_mixin
from pcapi.validation.models import offer
from pcapi.validation.models import offerer
from pcapi.validation.models import product
from pcapi.validation.models import stock
from pcapi.validation.models import user
from pcapi.validation.models import venue
from pcapi.validation.models.generic import validate_generic


def validate(model: Model) -> ApiErrors:  # type: ignore [valid-type]
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
    elif isinstance(model, User):
        api_errors = user.validate(model, api_errors)
    elif isinstance(model, Venue):
        api_errors = venue.validate(model, api_errors)

    return api_errors
