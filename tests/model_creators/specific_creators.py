import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from models import Booking, EventType, Offer, Offerer, Product, Stock, ThingType, User, Venue, Provider
from utils.token import random_token


def create_booking_for_event(amount: int = 50,
                             date_created: datetime = datetime.utcnow(),
                             is_cancelled: bool = False,
                             quantity: int = 1,
                             type: EventType = EventType.CINEMA,
                             user: User = None) -> Booking:
    product = Product(from_dict={'type': str(type)})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.product = product
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    booking.user = user
    booking.isCancelled = is_cancelled
    booking.token = random_token()
    booking.dateCreated = date_created

    return booking


def create_booking_for_thing(amount: int = 50,
                             date_created: datetime = datetime.utcnow(),
                             is_cancelled: bool = False,
                             quantity: int = 1,
                             product_type: ThingType = ThingType.JEUX,
                             url: str = None,
                             user: User = None) -> Booking:
    product = Product(from_dict={'url': url, 'type': str(product_type)})
    offer = Offer(from_dict={'url': url, 'type': str(product_type)})
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.product = product
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    booking.user = user
    booking.isCancelled = is_cancelled
    booking.dateCreated = date_created

    return booking


def create_event_occurrence(offer: Offer,
                            beginning_datetime: datetime = datetime.utcnow() + timedelta(hours=2),
                            end_datetime: datetime = datetime.utcnow() + timedelta(hours=5)) -> Dict:
    event_occurrence = {}
    event_occurrence['offer'] = offer
    event_occurrence['offerId'] = offer.id
    event_occurrence['beginningDatetime'] = beginning_datetime
    event_occurrence['endDatetime'] = end_datetime

    return event_occurrence


def create_offer_with_event_product(venue: Venue = None,
                                    booking_email: Optional[str] = None,
                                    date_created: datetime = datetime.utcnow(),
                                    description: Optional[str] = None,
                                    duration_minutes: Optional[int] = 60,
                                    event_name: str = 'Test event',
                                    event_type: EventType = EventType.SPECTACLE_VIVANT,
                                    id_at_providers: str = None,
                                    idx: int = None,
                                    is_active: bool = True,
                                    is_duo: bool = False,
                                    is_national: bool = False,
                                    last_provider_id: int = None,
                                    product: Product = None,
                                    last_provider: Provider = None,
                                    id_at_providers: str = None,
                                    description: str = None,
                                    is_duo: bool = False,
                                    thumb_count: int = 0) -> Offer:
    offer = Offer()
    if product is None:
        product = create_product_with_event_type(event_name=event_name, event_type=event_type,
                                                 duration_minutes=duration_minutes,
                                                 thumb_count=thumb_count, is_national=is_national)
    offer.product = product
    offer.venue = venue
    offer.name = product.name
    offer.type = product.type
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
    offer.isDuo = is_duo

    return offer


def create_offer_with_thing_product(venue: Venue,
                                    author_name: str = 'Test Author',
                                    booking_email: Optional[str] = None,
                                    date_created: datetime = datetime.utcnow(),
                                    description: Optional[str] = None,
                                    id_at_providers: str = None,
                                    idx: int = None,
                                    is_active: bool = True,
                                    is_digital: bool = False,
                                    is_national: bool = False,
                                    is_offline_only: bool = False,
                                    media_urls: List[str] = ['test/urls'],
                                    product: Product = None,
                                    thing_name: str = 'Test Book',
                                    thing_type: ThingType = ThingType.AUDIOVISUEL,
                                    thumb_count: int = 0,
                                    url: Optional[str] = None,
                                    last_provider_id: int = None,
                                    last_provider: Provider = None) -> Offer:
    offer = Offer()
    if product:
        offer.product = product
        offer.productId = product.id
        offer.name = product.name
        offer.type = product.type
        offer.mediaUrls = product.mediaUrls
        offer.extraData = product.extraData
        offer.url = product.url
        offer.isNational = product.isNational
        offer.description = product.description
    else:
        if is_digital:
            url = 'fake/url'
        if is_offline_only:
            thing_type = ThingType.CINEMA_ABO

        offer.product = create_product_with_thing_type(thing_name=thing_name, thing_type=thing_type,
                                                       media_urls=media_urls,
                                                       author_name=author_name, url=url, thumb_count=thumb_count,
                                                       is_national=is_national,
                                                       description=description)
        offer.name = thing_name
        offer.type = str(thing_type)
        offer.mediaUrls = media_urls
        offer.extraData = {'author': author_name}
        offer.url = url
        offer.isNational = is_national
        offer.description = description
    offer.venue = venue
    offer.dateCreated = date_created
    offer.bookingEmail = booking_email
    offer.isActive = is_active
    offer.lastProviderId = last_provider_id
    offer.lastProvider = last_provider
    offer.id = idx

    if id_at_providers:
        offer.idAtProviders = id_at_providers
    elif venue is not None:
        offer.idAtProviders = "%s@%s" % (offer.product.idAtProviders, venue.siret or venue.id)

    return offer


def create_product_with_event_type(event_name: str = 'Test event',
                                   event_type: EventType = EventType.SPECTACLE_VIVANT,
                                   description: str = None,
                                   duration_minutes: int = 60,
                                   id_at_providers: str = None,
                                   is_national: bool = False,
                                   is_duo: bool = False,
                                   thumb_count: int = 0) -> Product:
    product = Product()
    product.name = event_name
    product.description = description
    product.durationMinutes = duration_minutes
    product.thumbCount = thumb_count
    product.idAtProviders = id_at_providers
    product.isNational = is_national
    product.isDuo = is_duo
    product.type = str(event_type)
    product.description = description

    return product


def create_product_with_thing_type(thing_name: str = 'Test Book',
                                   thing_type: ThingType = ThingType.LIVRE_EDITION,
                                   author_name: str = 'Test Author',
                                   is_national: bool = False,
                                   id_at_providers: str = None,
                                   date_modified_at_last_provider: datetime = None,
                                   last_provider_id: int = None,
                                   media_urls: List[str] = ['test/urls'],
                                   description: str = None,
                                   thumb_count: int = 1,
                                   url: str = None,
                                   owning_offerer: Offerer = None,
                                   extra_data: Dict = None) -> Product:
    product = Product()
    product.type = str(thing_type)
    product.name = thing_name
    product.description = description
    if extra_data:
        product.extraData = extra_data
    else:
        product.extraData = {'author': author_name}
    product.isNational = is_national
    if id_at_providers is None:
        id_at_providers = ''.join(random.choices(string.digits, k=13))
    product.dateModifiedAtLastProvider = date_modified_at_last_provider
    product.lastProviderId = last_provider_id
    product.idAtProviders = id_at_providers
    product.mediaUrls = media_urls
    product.thumbCount = thumb_count
    product.url = url
    product.owningOfferer = owning_offerer
    product.description = description

    return product


def create_stock_from_event_occurrence(event_occurrence: Dict,
                                       price: int = 10,
                                       available: int = 10,
                                       soft_deleted: bool = False,
                                       recap_sent: bool = False,
                                       booking_limit_date: datetime = None) -> Stock:
    stock = Stock()
    stock.beginningDatetime = event_occurrence['beginningDatetime']
    stock.endDatetime = event_occurrence['endDatetime']
    stock.offerId = event_occurrence['offerId']
    stock.offer = event_occurrence['offer']
    stock.price = price
    stock.available = available
    stock.isSoftDeleted = soft_deleted

    if recap_sent:
        stock.bookingRecapSent = datetime.utcnow()

    if booking_limit_date is None:
        stock.bookingLimitDatetime = event_occurrence['beginningDatetime']
    else:
        stock.bookingLimitDatetime = booking_limit_date

    return stock


def create_stock_from_offer(offer: Offer,
                            price: float = 9.90,
                            available: int = 10,
                            soft_deleted: bool = False,
                            booking_limit_datetime: datetime = None,
                            beginning_datetime: datetime = None,
                            end_datetime: datetime = None,
                            date_modified: datetime = datetime.utcnow()) -> Stock:
    stock = Stock()
    stock.offer = offer
    stock.price = price
    stock.available = available
    stock.isSoftDeleted = soft_deleted
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.beginningDatetime = beginning_datetime
    stock.endDatetime = end_datetime
    stock.dateModified = date_modified

    return stock


def create_stock_with_event_offer(offerer: Offerer,
                                  venue: Venue,
                                  price: int = 10,
                                  booking_email: str = 'offer.booking.email@example.com',
                                  available: int = 10,
                                  is_soft_deleted: bool = False,
                                  event_type: EventType = EventType.JEUX,
                                  name: str = 'Mains, sorts et papiers',
                                  offer_id: int = None,
                                  beginning_datetime: datetime = datetime.utcnow() + timedelta(hours=72),
                                  end_datetime: datetime = datetime.utcnow() + timedelta(hours=74),
                                  thumb_count: int = 0,
                                  booking_limit_datetime: datetime = datetime.utcnow() + timedelta(hours=71)) -> Stock:
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
    stock.available = available
    stock.beginningDatetime = beginning_datetime
    stock.endDatetime = end_datetime
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.offer = create_offer_with_event_product(venue, event_name=name, event_type=event_type,
                                                  booking_email=booking_email, is_national=False,
                                                  thumb_count=thumb_count)
    stock.offer.id = offer_id
    stock.isSoftDeleted = is_soft_deleted

    return stock


def create_stock_with_thing_offer(offerer: Offerer,
                                  venue: Venue,
                                  offer: Offer = None,
                                  price: int = 10,
                                  available: int = 50,
                                  name: str = 'Test Book',
                                  booking_email: str = 'offer.booking.email@example.com',
                                  soft_deleted: bool = False,
                                  url: str = None,
                                  booking_limit_datetime: datetime = None,
                                  thing_type: ThingType = ThingType.AUDIOVISUEL) -> Stock:
    stock = Stock()
    stock.offerer = offerer
    stock.price = price

    if offer:
        stock.offer = offer
    else:
        stock.offer = create_offer_with_thing_product(venue, thing_name=name, thing_type=thing_type)

    stock.offer.bookingEmail = booking_email
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.offer.url = url
    stock.offer.venue = venue
    stock.available = available
    stock.isSoftDeleted = soft_deleted

    return stock
