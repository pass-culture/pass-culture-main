from datetime import datetime
from typing import Optional

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
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
    siren: Optional[str] = "123456789",
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
    beginning_datetime: Optional[datetime] = None,
    booking_limit_datetime: Optional[datetime] = None,
    date_created: datetime = datetime.utcnow(),
    date_modified: datetime = datetime.utcnow(),
    date_modified_at_last_provider: Optional[datetime] = None,
    idx: Optional[int] = None,
    id_at_providers: Optional[str] = None,
    is_soft_deleted: bool = False,
    last_provider_id: Optional[int] = None,
    offer: Optional[Offer] = None,
    price: float = 10,
    quantity: Optional[int] = None,
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


def create_venue(
    offerer: Offerer,
    address: Optional[str] = "123 rue de Paris",
    booking_email: Optional[str] = None,
    city: Optional[str] = "Montreuil",
    comment: Optional[str] = None,
    date_modified_at_last_provider: Optional[datetime] = None,
    departement_code: Optional[str] = "93",
    idx: Optional[int] = None,
    id_at_providers: Optional[str] = None,
    is_virtual: bool = False,
    last_provider_id: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    name: str = "La petite librairie",
    postal_code: Optional[str] = "93100",
    public_name: Optional[str] = None,
    siret: Optional[str] = "12345678912345",
    thumb_count: int = 0,
    validation_token: Optional[str] = None,
    venue_type_code: Optional[offerers_models.VenueTypeCode] = None,
    date_created: Optional[datetime] = datetime.utcnow(),
) -> Venue:
    venue = Venue()
    venue.bookingEmail = booking_email
    venue.comment = comment
    venue.dateModifiedAtLastProvider = date_modified_at_last_provider
    venue.dateCreated = date_created  # type: ignore [assignment]
    venue.id = idx  # type: ignore [assignment]
    venue.idAtProviders = id_at_providers
    venue.isVirtual = is_virtual
    venue.lastProviderId = last_provider_id
    venue.managingOfferer = offerer
    venue.name = name
    venue.publicName = public_name
    venue.thumbCount = thumb_count
    venue.validationToken = validation_token
    venue.siret = siret
    venue.venueTypeCode = venue_type_code  # type: ignore [assignment]

    if not is_virtual:
        venue.address = address
        venue.city = city
        venue.departementCode = departement_code
        venue.latitude = latitude  # type: ignore [assignment]
        venue.longitude = longitude  # type: ignore [assignment]
        venue.postalCode = postal_code

    return venue
