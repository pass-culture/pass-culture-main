from datetime import datetime

from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock


def create_offerer(
    address: str = None,
    city: str = "Montreuil",
    date_created: datetime = datetime.utcnow(),
    date_modified_at_last_provider: datetime = None,
    idx: int = None,
    id_at_providers: str = None,
    is_active: bool = True,
    last_provider_id: int = None,
    name: str = "Test Offerer",
    postal_code: str = "93100",
    siren: str | None = "123456789",
    thumb_count: int = 0,
    validation_token: str = None,
    date_validated: datetime = None,
) -> Offerer:
    offerer = Offerer()
    offerer.address = address
    offerer.city = city
    offerer.dateCreated = date_created
    offerer.dateModifiedAtLastProvider = date_modified_at_last_provider
    offerer.id = idx  # type: ignore [assignment]
    offerer.idAtProviders = id_at_providers
    offerer.isActive = is_active
    offerer.lastProviderId = last_provider_id
    offerer.name = name
    offerer.postalCode = postal_code
    offerer.siren = siren
    offerer.thumbCount = thumb_count
    offerer.validationToken = validation_token
    offerer.dateValidated = date_validated

    return offerer


def create_stock(
    beginning_datetime: datetime | None = None,
    booking_limit_datetime: datetime | None = None,
    date_created: datetime = datetime.utcnow(),
    date_modified: datetime = datetime.utcnow(),
    date_modified_at_last_provider: datetime | None = None,
    idx: int | None = None,
    id_at_providers: str | None = None,
    is_soft_deleted: bool = False,
    last_provider_id: int | None = None,
    offer: Offer | None = None,
    price: float = 10,
    quantity: int | None = None,
) -> Stock:
    stock = Stock()
    stock.quantity = quantity
    stock.beginningDatetime = beginning_datetime
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.dateCreated = date_created
    stock.dateModified = date_modified
    stock.dateModifiedAtLastProvider = date_modified_at_last_provider
    if idx:
        stock.id = idx
    stock.idAtProviders = id_at_providers
    stock.isSoftDeleted = is_soft_deleted
    stock.lastProviderId = last_provider_id
    stock.offer = offer  # type: ignore [assignment]
    stock.price = price  # type: ignore [assignment]

    return stock
