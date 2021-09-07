from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import random
import string
from typing import Iterable
from typing import Optional

from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.providers.models import Provider
from pcapi.models import Criterion
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import Venue


def create_offer_with_event_product(
    venue: Venue = None,
    booking_email: str = "booking@example.net",
    criteria: list[Criterion] = None,
    date_created: datetime = datetime.utcnow(),
    description: Optional[str] = None,
    duration_minutes: Optional[int] = 60,
    event_name: str = "Test event",
    event_subcategory_id: Optional[str] = subcategories.SPECTACLE_REPRESENTATION.id,
    id_at_providers: str = None,
    idx: int = None,
    is_active: bool = True,
    is_duo: bool = False,
    is_national: bool = False,
    last_provider_id: int = None,
    product: Product = None,
    last_provider: Provider = None,
    ranking_weight: int = None,
    thumb_count: int = 0,
    withdrawal_details: Optional[str] = None,
    extra_data: Optional[dict] = None,
    validation: OfferValidationStatus = OfferValidationStatus.APPROVED,
) -> Offer:
    offer = Offer()
    if product is None:
        product = create_product_with_event_subcategory(
            event_name=event_name,
            event_subcategory_id=event_subcategory_id,
            duration_minutes=duration_minutes,
            thumb_count=thumb_count,
            is_national=is_national,
        )
    if criteria:
        offer.criteria = criteria
    offer.product = product
    offer.venue = venue
    offer.name = product.name
    offer.subcategoryId = product.subcategoryId
    offer.description = description
    offer.isNational = product.isNational
    offer.durationMinutes = product.durationMinutes
    offer.dateCreated = date_created
    offer.bookingEmail = booking_email
    offer.isActive = is_active
    offer.id = idx
    offer.lastProviderId = last_provider_id
    offer.lastProvider = last_provider
    offer.idAtProviders = id_at_providers
    offer.idAtProvider = id_at_providers
    offer.isDuo = is_duo
    offer.validation = validation
    offer.withdrawalDetails = withdrawal_details
    offer.extraData = extra_data
    offer.rankingWeight = ranking_weight

    return offer


def create_event_occurrence(
    offer: Offer, beginning_datetime: datetime = datetime.utcnow() + timedelta(hours=2)
) -> dict:
    event_occurrence = {}
    event_occurrence["offer"] = offer
    event_occurrence["offerId"] = offer.id
    event_occurrence["beginningDatetime"] = beginning_datetime

    return event_occurrence


def create_offer_with_thing_product(
    venue: Venue,
    author_name: str = "Test Author",
    booking_email: Optional[str] = "booking@example.net",
    date_created: datetime = datetime.utcnow(),
    description: Optional[str] = None,
    id_at_providers: str = None,
    idx: int = None,
    product_idx: int = None,
    is_active: bool = True,
    is_digital: bool = False,
    is_national: bool = False,
    is_offline_only: bool = False,
    media_urls: Iterable[str] = ("test/urls",),
    product: Product = None,
    thing_name: Optional[str] = "Test Book",
    thing_subcategory_id: Optional[str] = subcategories.VOD.id,
    thumb_count: int = 0,
    url: Optional[str] = None,
    last_provider_id: int = None,
    last_provider: Provider = None,
    extra_data: dict = None,
    withdrawal_details: Optional[str] = None,
    date_modified_at_last_provider: Optional[datetime] = datetime.utcnow(),
    validation: OfferValidationStatus = OfferValidationStatus.APPROVED,
) -> Offer:
    offer = Offer()
    if product:
        offer.product = product
        offer.productId = product.id
        offer.name = product.name
        offer.subcategoryId = product.subcategoryId
        offer.mediaUrls = product.mediaUrls
        offer.extraData = product.extraData
        offer.url = product.url
        offer.isNational = product.isNational
        offer.description = product.description
    else:
        if is_digital:
            url = "fake/url"
        if is_offline_only:
            thing_subcategory_id = subcategories.CARTE_CINE_MULTISEANCES.id

        offer.product = create_product_with_thing_subcategory(
            thing_name=thing_name,
            thing_subcategory_id=thing_subcategory_id,
            media_urls=media_urls,
            idx=product_idx,
            author_name=author_name,
            url=url,
            thumb_count=thumb_count,
            is_national=is_national,
            description=description,
        )
        offer.name = thing_name
        offer.subcategoryId = thing_subcategory_id
        offer.mediaUrls = media_urls
        offer.extraData = {"author": author_name}
        offer.url = url
        offer.isNational = is_national
        offer.description = description
    offer.venue = venue
    offer.dateCreated = date_created
    offer.dateModifiedAtLastProvider = date_modified_at_last_provider
    offer.bookingEmail = booking_email
    offer.isActive = is_active
    offer.lastProviderId = last_provider_id
    offer.lastProvider = last_provider
    offer.id = idx
    offer.withdrawalDetails = withdrawal_details
    offer.isDuo = False
    offer.validation = validation

    if extra_data:
        offer.extraData = extra_data

    if id_at_providers:
        offer.idAtProviders = id_at_providers
    elif venue is not None:
        offer.idAtProviders = "%s@%s" % (offer.product.idAtProviders, venue.siret or venue.id)
        offer.idAtProvider = "%s" % offer.product.idAtProviders

    return offer


def create_product_with_event_subcategory(
    event_name: str = "Test event",
    event_subcategory_id: Optional[str] = subcategories.SPECTACLE_REPRESENTATION.id,
    description: str = None,
    duration_minutes: int = 60,
    id_at_providers: str = None,
    is_national: bool = False,
    is_duo: bool = False,
    thumb_count: int = 0,
) -> Product:
    product = Product()
    product.name = event_name
    product.description = description
    product.durationMinutes = duration_minutes
    product.thumbCount = thumb_count
    product.idAtProviders = id_at_providers
    product.isNational = is_national
    product.isDuo = is_duo
    product.subcategoryId = event_subcategory_id
    product.description = description

    return product


def create_product_with_thing_subcategory(
    thing_name: str = "Test Book",
    thing_subcategory_id: Optional[str] = subcategories.LIVRE_PAPIER.id,
    author_name: str = "Test Author",
    is_national: bool = False,
    id_at_providers: str = None,
    idx: int = None,
    is_digital: bool = False,
    is_gcu_compatible: bool = True,
    is_offline_only: bool = False,
    date_modified_at_last_provider: datetime = None,
    last_provider_id: int = None,
    media_urls: Iterable[str] = ("test/urls",),
    description: str = None,
    thumb_count: int = 1,
    url: str = None,
    owning_offerer: Offerer = None,
    extra_data: dict = None,
) -> Product:
    product = Product()
    product.id = idx
    product.subcategoryId = thing_subcategory_id
    product.name = thing_name
    product.description = description
    if extra_data:
        product.extraData = extra_data
    else:
        product.extraData = {"author": author_name}
    product.isNational = is_national
    if id_at_providers is None:
        id_at_providers = "".join(random.choices(string.digits, k=13))
    product.dateModifiedAtLastProvider = date_modified_at_last_provider
    product.lastProviderId = last_provider_id
    product.idAtProviders = id_at_providers
    product.isGcuCompatible = is_gcu_compatible
    product.mediaUrls = media_urls
    product.thumbCount = thumb_count
    product.url = url
    product.owningOfferer = owning_offerer
    product.description = description
    if is_digital:
        product.url = "fake/url"
    if is_offline_only:
        product.subcategoryId = subcategories.CARTE_CINE_MULTISEANCES.id
    return product


def create_stock_from_event_occurrence(
    event_occurrence: dict,
    price: int = 10,
    quantity: int = 10,
    soft_deleted: bool = False,
    recap_sent: bool = False,
    booking_limit_date: datetime = None,
) -> Stock:
    stock = Stock()
    stock.beginningDatetime = event_occurrence["beginningDatetime"]
    stock.offerId = event_occurrence["offerId"]
    stock.offer = event_occurrence["offer"]
    stock.price = price
    stock.quantity = quantity
    stock.isSoftDeleted = soft_deleted

    if recap_sent:
        stock.bookingRecapSent = datetime.utcnow()

    if booking_limit_date is None:
        stock.bookingLimitDatetime = event_occurrence["beginningDatetime"]
    else:
        stock.bookingLimitDatetime = booking_limit_date

    return stock


def create_stock_from_offer(
    offer: Offer,
    price: float = 9.90,
    quantity: Optional[int] = 10,
    soft_deleted: bool = False,
    booking_limit_datetime: datetime = None,
    beginning_datetime: datetime = None,
    idx: int = None,
    date_modified: datetime = datetime.utcnow(),
) -> Stock:
    stock = Stock()
    stock.id = idx
    stock.offer = offer
    stock.price = price
    stock.quantity = quantity
    stock.isSoftDeleted = soft_deleted
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.beginningDatetime = beginning_datetime
    stock.dateModified = date_modified

    return stock


def create_stock_with_event_offer(
    offerer: Offerer,
    venue: Venue,
    price: int = 10,
    booking_email: str = "offer.booking.email@example.com",
    quantity: int = 10,
    is_soft_deleted: bool = False,
    event_subcategory_id: Optional[str] = subcategories.EVENEMENT_JEU.id,
    name: str = "Mains, sorts et papiers",
    offer_id: int = None,
    beginning_datetime: datetime = datetime.utcnow() + timedelta(hours=72),
    thumb_count: int = 0,
    booking_limit_datetime: datetime = datetime.utcnow() + timedelta(hours=71),
    date_created: datetime = datetime.utcnow(),
    date_modified_at_last_provider: datetime = datetime.utcnow(),
    date_modifed: datetime = datetime.utcnow(),
) -> Stock:
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
    stock.quantity = quantity
    stock.beginningDatetime = beginning_datetime
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.dateCreated = date_created
    stock.dateModifiedAtLastProvider = date_modified_at_last_provider
    stock.dateModified = date_modifed
    stock.offer = create_offer_with_event_product(
        venue,
        event_name=name,
        event_subcategory_id=event_subcategory_id,
        booking_email=booking_email,
        is_national=False,
        thumb_count=thumb_count,
    )
    stock.offer.id = offer_id
    stock.isSoftDeleted = is_soft_deleted

    return stock


def create_stock_with_thing_offer(
    offerer: Offerer,
    venue: Venue,
    offer: Offer = None,
    price: Optional[Decimal] = 10,
    quantity: int = 50,
    name: str = "Test Book",
    booking_email: str = "offer.booking.email@example.com",
    soft_deleted: bool = False,
    url: str = None,
    booking_limit_datetime: datetime = None,
    thing_subcategory_id: str = subcategories.SUPPORT_PHYSIQUE_FILM.id,
) -> Stock:
    stock = Stock()
    stock.offerer = offerer
    stock.price = price

    if offer:
        stock.offer = offer
    else:
        stock.offer = create_offer_with_thing_product(venue, thing_name=name, thing_subcategory_id=thing_subcategory_id)

    stock.offer.bookingEmail = booking_email
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.offer.url = url
    stock.offer.venue = venue
    stock.quantity = quantity
    stock.isSoftDeleted = soft_deleted

    return stock
