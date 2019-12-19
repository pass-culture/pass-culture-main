import random
import string
from datetime import datetime, timedelta
from unittest.mock import Mock

from models import ThingType, User, Product, Offer, Stock, Booking, EventType
from utils.token import random_token


def create_booking_for_thing(
        amount: int = 50,
        date_created: datetime = datetime.utcnow(),
        is_cancelled: bool = False,
        quantity: int = 1,
        product_type: ThingType = ThingType.JEUX,
        url: str = None,
        user: User = None,
):
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


def create_booking_for_event(
        amount: int = 50,
        date_created: datetime = datetime.utcnow(),
        is_cancelled: bool = False,
        quantity: int = 1,
        type: EventType = EventType.CINEMA,
        user: User = None,
):
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


def create_stock_with_event_offer(offerer, venue, price=10, booking_email='offer.booking.email@test.com', available=10,
                                  is_soft_deleted=False, event_type=EventType.JEUX, name='Mains, sorts et papiers',
                                  offer_id=None, beginning_datetime=datetime.utcnow() + timedelta(hours=72),
                                  end_datetime=datetime.utcnow() + timedelta(hours=74), thumb_count=0,
                                  booking_limit_datetime=datetime.utcnow() + timedelta(hours=71)):
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


def create_stock_from_event_occurrence(event_occurrence, price=10, available=10, soft_deleted=False, recap_sent=False,
                                       booking_limit_date=None):
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


def create_stock_from_offer(offer, price=10, available=10, soft_deleted=False, booking_limit_datetime=None,
                            beginning_datetime=None, end_datetime=None, date_modified=datetime.utcnow()):
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


def create_stock_with_thing_offer(offerer, venue, offer=None, price=10, available=50, name='Test Book',
                                  booking_email='offer.booking.email@test.com', soft_deleted=False, url=None,
                                  booking_limit_datetime=None, thing_type=ThingType.AUDIOVISUEL) -> Stock:
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


def create_product_with_thing_type(
        thing_name='Test Book',
        thing_type=ThingType.LIVRE_EDITION,
        author_name='Test Author',
        is_national=False,
        id_at_providers=None,
        date_modified_at_last_provider=None,
        last_provider_id=None,
        media_urls=['test/urls'],
        description=None,
        thumb_count=1,
        url=None,
        owning_offerer=None,
        extra_data=None
) -> Product:
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


def create_product_with_event_type(
        event_name='Test event',
        event_type=EventType.SPECTACLE_VIVANT,
        description=None,
        duration_minutes=60,
        id_at_providers=None,
        is_national=False,
        is_duo=False,
        thumb_count=0,
) -> Product:
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


def create_offer_with_thing_product(venue, product=None, date_created=datetime.utcnow(),
                                    booking_email='booking.email@test.com',
                                    thing_type=ThingType.AUDIOVISUEL, thing_name='Test Book', media_urls=['test/urls'],
                                    author_name='Test Author', description=None, thumb_count=1, url=None,
                                    is_national=False, is_active=True, id_at_providers=None, idx=None,
                                    last_provider_id=None) -> Offer:
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

    if id_at_providers:
        offer.idAtProviders = id_at_providers
    elif venue is not None:
        offer.idAtProviders = "%s@%s" % (offer.product.idAtProviders, venue.siret or venue.id)
    offer.id = idx

    return offer


def create_offer_with_event_product(venue=None, product=None, event_name='Test event', duration_minutes=60,
                                    date_created=datetime.utcnow(),
                                    booking_email='booking.email@test.com', thumb_count=0,
                                    event_type=EventType.SPECTACLE_VIVANT, is_national=False, is_active=True,
                                    idx=None, last_provider_id=None, id_at_providers=None, description=None,
                                    is_duo=False) -> Offer:
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
    offer.idAtProviders = id_at_providers
    offer.isDuo = is_duo
    return offer


def create_event_occurrence(
        offer,
        beginning_datetime=datetime.utcnow() + timedelta(hours=2),
        end_datetime=datetime.utcnow() + timedelta(hours=5)
):
    event_occurrence = {}
    event_occurrence['offer'] = offer
    event_occurrence['offerId'] = offer.id
    event_occurrence['beginningDatetime'] = beginning_datetime
    event_occurrence['endDatetime'] = end_datetime
    return event_occurrence


def create_mocked_bookings(num_bookings, venue_email, name='Offer name'):
    bookings = []
    for i in range(num_bookings):
        booking = Mock(spec=Booking)
        booking.user.email = 'user_email%s' % i
        booking.user.firstName = 'First %s' % i
        booking.user.lastName = 'Last %s' % i
        booking.stock.resolvedOffer.bookingEmail = venue_email
        booking.stock.resolvedOffer.product.name = name
        bookings.append(booking)
    return bookings