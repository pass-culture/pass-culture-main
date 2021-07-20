from datetime import datetime
from hashlib import sha256
import random
import string
from typing import Iterable
from typing import Optional

from pcapi.core.bookings import api as bookings_api
from pcapi.core.offerers.models import Offerer
from pcapi.core.providers.models import Provider
from pcapi.core.users.models import User
from pcapi.models import Booking
from pcapi.models import EventType
from pcapi.models import Offer
from pcapi.models import Payment
from pcapi.models import PaymentMessage
from pcapi.models import Product
from pcapi.models import Stock
from pcapi.models import ThingType
from pcapi.models import UserOfferer
from pcapi.models import Venue
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.utils.token import random_token


PLAIN_DEFAULT_TESTING_PASSWORD = "user@AZERTY123"


def create_user(
    activity: str = None,
    is_beneficiary: bool = True,
    civility: str = None,
    cultural_survey_id: str = None,
    cultural_survey_filled_date: datetime = None,
    date_created: datetime = datetime.utcnow(),
    date_of_birth: datetime = None,
    departement_code: str = "93",
    email: str = "john.doe@example.com",
    first_name: str = None,
    has_seen_tutorials: bool = None,
    idx: int = None,
    is_admin: bool = False,
    last_name: str = None,
    needs_to_fill_cultural_survey: bool = False,
    password: str = None,
    phone_number: str = None,
    postal_code: str = None,
    public_name: str = "John Doe",
    validation_token: str = None,
) -> User:
    user = User()
    user.activity = activity
    user.isBeneficiary = is_beneficiary
    user.civility = civility
    user.culturalSurveyId = cultural_survey_id
    user.culturalSurveyFilledDate = cultural_survey_filled_date
    user.dateCreated = date_created
    user.dateOfBirth = date_of_birth
    user.departementCode = departement_code
    user.email = email
    user.firstName = first_name
    user.hasSeenTutorials = has_seen_tutorials
    user.id = idx
    user.isAdmin = is_admin
    user.lastName = last_name
    user.needsToFillCulturalSurvey = needs_to_fill_cultural_survey
    user.phoneNumber = phone_number
    user.publicName = public_name
    user.postalCode = postal_code
    user.validationToken = validation_token

    if password:
        user.setPassword(password)
    else:
        user.setPassword(PLAIN_DEFAULT_TESTING_PASSWORD)

    return user


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
) -> Offerer:
    offerer = Offerer()
    offerer.address = address
    offerer.city = city
    offerer.dateCreated = date_created
    offerer.dateModifiedAtLastProvider = date_modified_at_last_provider
    offerer.id = idx
    offerer.idAtProviders = id_at_providers
    offerer.isActive = is_active
    offerer.lastProviderId = last_provider_id
    offerer.name = name
    offerer.postalCode = postal_code
    offerer.siren = siren
    offerer.thumbCount = thumb_count
    offerer.validationToken = validation_token

    return offerer


def create_user_offerer(user: User, offerer: Offerer, idx: int = None, validation_token: str = None) -> UserOfferer:
    user_offerer = UserOfferer()
    user_offerer.id = idx
    user_offerer.offerer = offerer
    user_offerer.user = user
    user_offerer.validationToken = validation_token

    return user_offerer


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
    venue_type_id: int = None,
) -> Venue:
    venue = Venue()
    venue.bookingEmail = booking_email
    venue.comment = comment
    venue.dateModifiedAtLastProvider = date_modified_at_last_provider
    venue.id = idx
    venue.idAtProviders = id_at_providers
    venue.isVirtual = is_virtual
    venue.lastProviderId = last_provider_id
    venue.managingOfferer = offerer
    venue.name = name
    venue.publicName = public_name
    venue.thumbCount = thumb_count
    venue.validationToken = validation_token
    venue.siret = siret
    venue.venueTypeId = venue_type_id

    if not is_virtual:
        venue.address = address
        venue.city = city
        venue.departementCode = departement_code
        venue.latitude = latitude
        venue.longitude = longitude
        venue.postalCode = postal_code

    return venue


def create_product_with_event_type(
    event_name: str = "Test event",
    event_type: EventType = EventType.SPECTACLE_VIVANT,
    description: str = None,
    duration_minutes: Optional[int] = 60,
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
    product.type = str(event_type)
    product.description = description

    return product


def create_offer_with_event_product(
    venue: Venue = None,
    booking_email: str = "booking@example.net",
    date_created: datetime = datetime.utcnow(),
    description: Optional[str] = None,
    duration_minutes: Optional[int] = 60,
    event_name: str = "Test event",
    event_type: EventType = EventType.SPECTACLE_VIVANT,
    id_at_providers: str = None,
    idx: int = None,
    is_active: bool = True,
    is_duo: bool = False,
    is_national: bool = False,
    last_provider_id: int = None,
    product: Product = None,
    last_provider: Provider = None,
    thumb_count: int = 0,
    withdrawal_details: Optional[str] = None,
) -> Offer:
    offer = Offer()
    if product is None:
        product = create_product_with_event_type(
            event_name=event_name,
            event_type=event_type,
            duration_minutes=duration_minutes,
            thumb_count=thumb_count,
            is_national=is_national,
        )
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
    offer.withdrawalDetails = withdrawal_details

    return offer


def create_stock(
    quantity: int = None,
    booking_limit_datetime: datetime = None,
    beginning_datetime: datetime = None,
    date_created: datetime = datetime.utcnow(),
    date_modified: datetime = datetime.utcnow(),
    date_modified_at_last_provider: datetime = None,
    idx: int = None,
    id_at_providers: str = None,
    is_soft_deleted: bool = False,
    last_provider_id: int = None,
    offer: Offer = None,
    price: float = 10,
) -> Stock:
    stock = Stock()
    stock.quantity = quantity
    stock.beginningDatetime = beginning_datetime
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.dateCreated = date_created
    stock.dateModified = date_modified
    stock.dateModifiedAtLastProvider = date_modified_at_last_provider
    stock.id = idx
    stock.idAtProviders = id_at_providers
    stock.isSoftDeleted = is_soft_deleted
    stock.lastProviderId = last_provider_id
    stock.offer = offer
    stock.price = price

    return stock


def create_product_with_thing_type(
    thing_name: str = "Test Book",
    thing_type: ThingType = ThingType.LIVRE_EDITION,
    author_name: str = "Test Author",
    is_national: bool = False,
    id_at_providers: str = None,
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
    product.type = str(thing_type)
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
        product.type = str(ThingType.CINEMA_ABO)

    return product


def create_offer_with_thing_product(
    venue: Venue,
    author_name: str = "Test Author",
    booking_email: Optional[str] = "booking@example.net",
    date_created: datetime = datetime.utcnow(),
    description: Optional[str] = None,
    id_at_providers: str = None,
    idx: int = None,
    is_active: bool = True,
    is_digital: bool = False,
    is_national: bool = False,
    is_offline_only: bool = False,
    media_urls: Iterable[str] = ("test/urls",),
    product: Product = None,
    thing_name: str = "Test Book",
    thing_type: ThingType = ThingType.AUDIOVISUEL,
    thumb_count: int = 0,
    url: Optional[str] = None,
    last_provider_id: int = None,
    last_provider: Provider = None,
    extra_data: dict = None,
    withdrawal_details: Optional[str] = None,
) -> Offer:
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
            url = "fake/url"
        if is_offline_only:
            thing_type = ThingType.CINEMA_ABO

        offer.product = create_product_with_thing_type(
            thing_name=thing_name,
            thing_type=thing_type,
            media_urls=media_urls,
            author_name=author_name,
            url=url,
            thumb_count=thumb_count,
            is_national=is_national,
            description=description,
        )
        offer.name = thing_name
        offer.type = str(thing_type)
        offer.mediaUrls = media_urls
        offer.extraData = {"author": author_name}
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
    offer.withdrawalDetails = withdrawal_details

    if extra_data:
        offer.extraData = extra_data

    if id_at_providers:
        offer.idAtProviders = id_at_providers
    elif venue is not None:
        offer.idAtProviders = "%s@%s" % (offer.product.idAtProviders, venue.siret or venue.id)

    return offer


def create_booking(
    user: User,
    amount: int = None,
    date_created: datetime = datetime.utcnow(),
    date_used: datetime = None,
    idx: int = None,
    is_cancelled: bool = False,
    is_used: bool = False,
    quantity: int = 1,
    stock: Stock = None,
    token: str = None,
    venue: Venue = None,
) -> Booking:
    booking = Booking()
    offerer = create_offerer(
        siren="987654321", address="Test address", city="Test city", postal_code="93000", name="Test name"
    )
    if venue is None:
        venue = create_venue(
            offerer=offerer,
            name="Test offerer",
            booking_email="reservations@test.fr",
            address="123 rue test",
            postal_code="93000",
            city="Test city",
            departement_code="93",
        )
    if stock is None:
        price = amount if amount is not None else 10
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=price)

    if not stock.offer:
        stock.offer = create_offer_with_thing_product(venue)

    booking.user = user
    booking.amount = stock.price
    booking.dateCreated = date_created
    booking.dateUsed = date_used
    booking.id = idx
    booking.isCancelled = is_cancelled
    booking.isUsed = is_used
    booking.quantity = quantity
    booking.stock = stock
    booking.token = token if token is not None else random_token()
    booking.userId = user.id
    booking.cancellationLimitDate = bookings_api.compute_cancellation_limit_date(stock.beginningDatetime, date_created)

    return booking


def create_payment_message(checksum: str = None, idx: int = None, name: str = "ABCD123") -> PaymentMessage:
    payment_message = PaymentMessage()
    payment_message.checksum = checksum if checksum else sha256(name.encode("utf-8")).digest()
    payment_message.id = idx
    payment_message.name = name

    return payment_message


def create_payment(
    booking: Booking,
    offerer: Offerer,
    amount: int = 10,
    author: str = "test author",
    bic: str = None,
    comment: str = None,
    iban: str = None,
    idx: int = None,
    payment_message: PaymentMessage = None,
    payment_message_name: str = None,
    reimbursement_rate: float = 0.5,
    reimbursement_rule: str = "remboursement à 100%",
    status: TransactionStatus = TransactionStatus.PENDING,
    detail: str = None,
    status_date: datetime = datetime.utcnow(),
    transaction_end_to_end_id: str = None,
    transaction_label: str = None,
) -> Payment:
    payment_status = PaymentStatus()
    payment_status.status = status
    payment_status.date = status_date
    payment_status.detail = detail

    payment = Payment()
    payment.amount = amount
    payment.author = author
    payment.bic = bic
    payment.booking = booking
    payment.comment = comment
    payment.iban = iban
    payment.id = idx
    if payment_message_name:
        payment.paymentMessage = create_payment_message(name=payment_message_name)
    elif payment_message:
        payment.paymentMessage = payment_message
    payment.recipientName = offerer.name
    payment.recipientSiren = offerer.siren
    payment.reimbursementRate = reimbursement_rate
    payment.reimbursementRule = reimbursement_rule
    payment.statuses = [payment_status]
    payment.transactionEndToEndId = transaction_end_to_end_id
    payment.transactionLabel = transaction_label

    return payment
