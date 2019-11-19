import random
import string
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from glob import glob
from hashlib import sha256
from inspect import isclass
from unittest.mock import Mock

import pytest
from postgresql_audit.flask import versioning_manager

import models
from local_providers.providable_info import ProvidableInfo
from models import ApiKey, \
    BankInformation, \
    Booking, \
    Criterion, \
    Deposit, \
    EventType, \
    Favorite, \
    Mediation, \
    Offer, \
    Offerer, \
    Payment, \
    PaymentMessage, \
    Product, \
    Provider, \
    Recommendation, \
    RightsType, \
    Stock, \
    ThingType, \
    User, \
    UserOfferer, \
    Venue, \
    VenueProvider
from models.beneficiary_import import BeneficiaryImport
from models.beneficiary_import_status import ImportStatus, BeneficiaryImportStatus
from models.db import db, Model
from models.email import Email, EmailStatus
from models.feature import FeatureToggle, Feature
from models.payment import PaymentDetails
from models.payment_status import PaymentStatus, TransactionStatus
from models.pc_object import PcObject
from repository.provider_queries import get_provider_by_local_class
from utils.object_storage import STORAGE_DIR
from utils.token import random_token

saved_counts = {}

USER_TEST_ADMIN_EMAIL = "pctest.admin93.0@btmx.fr"
USER_TEST_ADMIN_PASSWORD = "pctest.Admin93.0"
API_URL = "http://localhost:5000"
user = User()
PLAIN_DEFAULT_TESTING_PASSWORD = 'user@AZERTY123'
user.setPassword(PLAIN_DEFAULT_TESTING_PASSWORD)
HASHED_DEFAULT_TESTING_PASSWORD = user.password


def create_booking(user, stock=None, venue=None, recommendation=None, quantity=1, date_created=datetime.utcnow(),
                   date_used=None, is_cancelled=False, is_used=False, token=None, idx=None, amount=None):
    booking = Booking()
    if venue is None:
        offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
    if stock is None:
        product_with_thing_type = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, product_with_thing_type, price=10)
    booking.stock = stock
    booking.user = user
    if token is None:
        booking.token = random_token()
    else:
        booking.token = token

    if amount is None:
        booking.amount = stock.price
    else:
        booking.amount = amount

    booking.quantity = quantity
    booking.dateCreated = date_created
    if recommendation:
        booking.recommendation = recommendation
    elif not stock.offer:
        offer = create_offer_with_thing_product(venue)
        booking.recommendation = create_recommendation(offer, user)
    else:
        booking.recommendation = create_recommendation(stock.offer, user)
    booking.isCancelled = is_cancelled
    booking.isUsed = is_used
    booking.dateUsed = date_used
    if idx:
        booking.id = idx
    return booking


def create_booking_for_thing(
        url=None,
        amount=50,
        quantity=1,
        user=None,
        is_cancelled=False,
        product_type=ThingType.JEUX,
        date_created=datetime.utcnow()
):
    product = Product(from_dict={'url': url, 'type': str(product_type)})
    offer = Offer(from_dict={'type': str(product_type)})
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
        amount=50,
        quantity=1,
        user=None,
        isCancelled=False,
        type=EventType.CINEMA,
        date_created=datetime.utcnow()
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
    booking.isCancelled = isCancelled
    booking.token = random_token()
    booking.dateCreated = date_created
    return booking


def create_criterion(name='best offer', description=None, score_delta=1):
    criterion = Criterion()
    criterion.name = name
    criterion.description = description
    criterion.scoreDelta = score_delta
    return criterion


def create_user(public_name='John Doe', password=None, first_name='John', last_name='Doe', postal_code='93100',
                departement_code='93',
                email='john.doe@test.com', can_book_free_offers=True, needs_to_fill_cultural_survey=False,
                cultural_survey_id=None, validation_token=None, is_admin=False,
                reset_password_token=None, reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24),
                date_created=datetime.utcnow(), phone_number='0612345678', date_of_birth=datetime(2001, 1, 1),
                idx=None):
    user = User()
    user.publicName = public_name
    user.firstName = first_name
    user.lastName = last_name
    user.email = email
    user.canBookFreeOffers = can_book_free_offers
    user.postalCode = postal_code
    user.departementCode = departement_code
    user.validationToken = validation_token

    if password:
        user.setPassword(password)
    else:
        user.clearTextPassword = PLAIN_DEFAULT_TESTING_PASSWORD
        user.password = HASHED_DEFAULT_TESTING_PASSWORD

    user.isAdmin = is_admin
    user.resetPasswordToken = reset_password_token
    user.resetPasswordTokenValidityLimit = reset_password_token_validity_limit
    user.dateCreated = date_created
    user.phoneNumber = phone_number
    user.dateOfBirth = date_of_birth
    user.needsToFillCulturalSurvey = needs_to_fill_cultural_survey
    user.culturalSurveyId = cultural_survey_id
    user.id = idx
    return user


def create_beneficiary_import(
        user: User = None,
        status=ImportStatus.CREATED,
        date=datetime.utcnow(),
        detail: str = None,
        demarche_simplifiee_application_id: int = None
):
    import_status = BeneficiaryImportStatus()
    import_status.date = date
    import_status.detail = detail
    import_status.status = status

    beneficiary_import = BeneficiaryImport()
    beneficiary_import.beneficiary = user
    beneficiary_import.statuses = [import_status]
    beneficiary_import.demarcheSimplifieeApplicationId = demarche_simplifiee_application_id

    return beneficiary_import


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


def create_stock(price=10, available=10, booking_limit_datetime=None, offer=None,
                 beginning_datetime=None, end_datetime=None,
                 is_soft_deleted=False, id_at_providers=None, last_provider_id=None, date_modified=datetime.utcnow()):
    stock = Stock()
    stock.price = price
    stock.available = available
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.offer = offer
    stock.beginningDatetime = beginning_datetime
    stock.endDatetime = end_datetime
    stock.isSoftDeleted = is_soft_deleted
    stock.idAtProviders = id_at_providers
    stock.lastProviderId = last_provider_id
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
        dominant_color=None,
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

    if thumb_count and thumb_count > 0:
        if dominant_color is None:
            product.firstThumbDominantColor = b'\x00\x00\x00'
        else:
            product.firstThumbDominantColor = dominant_color
    product.description = description
    return product


def create_product_with_event_type(
        event_name='Test event',
        event_type=EventType.SPECTACLE_VIVANT,
        description=None,
        dominant_color=None,
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
    product.firstThumbDominantColor = dominant_color
    if product.thumbCount > 0 and not dominant_color:
        product.firstThumbDominantColor = b'\x00\x00\x00'
    product.description = description
    return product


def create_offer_with_thing_product(venue, product=None, date_created=datetime.utcnow(),
                                    booking_email='booking.email@test.com',
                                    thing_type=ThingType.AUDIOVISUEL, thing_name='Test Book', media_urls=['test/urls'],
                                    author_name='Test Author', description=None, thumb_count=1, dominant_color=None,
                                    url=None, is_national=False, is_active=True, id_at_providers=None, idx=None,
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
                                                       dominant_color=dominant_color, is_national=is_national,
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
                                    booking_email='booking.email@test.com', thumb_count=0, dominant_color=None,
                                    event_type=EventType.SPECTACLE_VIVANT, is_national=False, is_active=True,
                                    idx=None, last_provider_id=None, id_at_providers=None, description=None,
                                    is_duo=False) -> Offer:
    offer = Offer()
    if product is None:
        product = create_product_with_event_type(event_name=event_name, event_type=event_type,
                                                 duration_minutes=duration_minutes,
                                                 thumb_count=thumb_count, dominant_color=dominant_color,
                                                 is_national=is_national)
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


def create_offerer(
        siren='123456789',
        address='123 rue de Paris',
        city='Montreuil',
        postal_code='93100',
        name='Test Offerer',
        validation_token=None,
        idx=None,
        is_active=True,
        date_created=datetime.utcnow(),
        latitude=None,
        longitude=None
):
    offerer = Offerer()
    offerer.siren = siren
    offerer.isActive = is_active
    offerer.address = address
    offerer.postalCode = postal_code
    offerer.city = city
    offerer.name = name
    offerer.validationToken = validation_token
    offerer.id = idx
    offerer.dateCreated = date_created
    offerer.latitude = latitude
    offerer.longitude = longitude
    return offerer


def create_venue(
        offerer,
        name='La petite librairie',
        booking_email='john.doe@test.com',
        address='123 rue de Paris',
        postal_code='93100',
        city='Montreuil',
        departement_code='93',
        is_virtual=False,
        longitude='2.4002701',
        latitude='48.8363788',
        siret='12345678912345',
        validation_token=None,
        comment=None,
        idx=None,
        publicName=None
):
    venue = Venue()
    venue.bookingEmail = booking_email
    if not is_virtual:
        venue.address = address
        venue.postalCode = postal_code
        venue.city = city
        venue.departementCode = departement_code
        venue.longitude = longitude
        venue.latitude = latitude
    venue.name = name
    venue.managingOfferer = offerer
    venue.isVirtual = is_virtual
    venue.siret = siret
    venue.validationToken = validation_token
    venue.comment = comment
    venue.id = idx
    venue.publicName = publicName
    return venue


def create_deposit(user, amount=500, source='public'):
    deposit = Deposit()
    deposit.user = user
    deposit.source = source
    deposit.amount = amount
    return deposit


def create_user_offerer(user, offerer, validation_token=None, is_admin=False):
    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer
    user_offerer.validationToken = validation_token
    user_offerer.rights = RightsType.admin if is_admin else RightsType.editor
    return user_offerer


def create_recommendation(offer=None, user=None, mediation=None, idx=None, date_read=None,
                          valid_until_date=datetime.utcnow() + timedelta(days=7), search=None, is_clicked=False,
                          date_created=None):
    recommendation = Recommendation()
    recommendation.id = idx
    recommendation.offer = offer
    recommendation.user = user
    recommendation.mediation = mediation
    recommendation.dateRead = date_read
    recommendation.validUntilDate = valid_until_date
    recommendation.search = search
    recommendation.isClicked = is_clicked
    recommendation.dateCreated = date_created
    return recommendation


def create_favorite(mediation=None, offer=None, user=None) -> Favorite:
    favorite = Favorite()
    favorite.user = user
    favorite.mediation = mediation
    favorite.offer = offer
    return favorite


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


def create_mediation(offer=None, author=None, date_created=datetime.utcnow(), front_text='Some front text',
                     back_text='Some back test', is_active=True, tuto_index=None):
    mediation = Mediation()
    mediation.offer = offer
    mediation.dateCreated = date_created
    mediation.frontText = front_text
    mediation.backText = back_text
    mediation.author = author
    mediation.isActive = is_active
    mediation.tutoIndex = tuto_index
    return mediation


def create_booking_activity(booking, table_name, verb, issued_at=datetime.utcnow, data=None):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb

    base_data = {
        "id": booking.id, "token": booking.token, "userId": booking.userId, "stockId": booking.stockId,
        "isCancelled": booking.isCancelled, "quantity": booking.quantity,
        "recommendationId": booking.recommendationId, "isUsed": booking.isUsed
    }

    if verb.lower() == 'insert':
        activity.old_data = {}
        activity.changed_data = base_data
    elif verb.lower() == 'update':
        activity.old_data = base_data
        activity.changed_data = data
    elif verb.lower() == 'delete':
        activity.old_data = base_data
        activity.changed_data = {}

    return activity


def create_stock_activity(stock, verb, issued_at=datetime.utcnow, data=None):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = 'stock'
    activity.verb = verb

    base_data = {
        "id": stock.id,
        "available": stock.available
    }

    if verb.lower() == 'insert':
        activity.old_data = {}
        activity.changed_data = base_data
    elif verb.lower() == 'update':
        activity.old_data = base_data
        activity.changed_data = data
    elif verb.lower() == 'delete':
        activity.old_data = base_data
        activity.changed_data = data

    return activity


def create_user_activity(user, table_name, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb
    variables = {'email': user.email,
                 'publicName': user.publicName,
                 'offerers': user.offerers,
                 'departementCode': user.departementCode,
                 'canBookFreeOffers': user.canBookFreeOffers,
                 'isAdmin': user.isAdmin}
    activity.changed_data = variables
    return activity


def create_venue_activity(venue, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = 'venue'
    activity.verb = verb
    variables = {'id': venue.id,
                 'name': venue.name,
                 'siret': venue.siret,
                 'departementCode': venue.departementCode,
                 'postalCode': venue.postalCode}
    activity.changed_data = variables
    return activity


def create_offerer_activity(offerer, table_name, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb
    variables = {'id': offerer.id,
                 'name': offerer.name,
                 'siren': offerer.siren}
    activity.changed_data = variables
    return activity


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


def create_payment(booking, offerer, amount, author='test author', reimbursement_rule='remboursement à 100%',
                   reimbursement_rate=Decimal(0.5), payment_message=None, payment_message_name=None,
                   transaction_end_to_end_id=None,
                   transaction_label='pass Culture Pro - remboursement 2nde quinzaine 07-2018',
                   status=TransactionStatus.PENDING, idx=None, iban='FR7630007000111234567890144', bic='BDFEFR2LCCB'):
    payment = Payment()
    payment.booking = booking
    payment.amount = amount
    payment.author = author
    payment.iban = iban
    payment.bic = bic
    payment.recipientName = offerer.name
    payment.recipientSiren = offerer.siren
    payment_status = PaymentStatus()
    payment_status.status = status
    payment_status.date = datetime.utcnow()
    payment.statuses = [payment_status]
    payment.reimbursementRule = reimbursement_rule
    payment.reimbursementRate = reimbursement_rate

    if payment_message_name:
        payment.paymentMessage = create_payment_message(payment_message_name)
    elif payment_message:
        payment.paymentMessage = payment_message

    payment.transactionEndToEndId = transaction_end_to_end_id
    payment.transactionLabel = transaction_label
    payment.id = idx
    return payment


def create_payment_message(name="ABCD123", checksum=None):
    message = PaymentMessage()
    message.name = name
    if checksum:
        message.checksum = checksum
    else:
        message.checksum = sha256(name.encode('utf-8')).digest()
    return message


def create_payment_details(
        booking_user_id=1234,
        booking_user_email='john.doe@test.com',
        offerer_name='Les petites librairies',
        offerer_siren='123456789',
        venue_name='Vive les BDs',
        venue_siret='12345678912345',
        offer_name='Blake & Mortimer',
        offer_type=ThingType.LIVRE_EDITION,
        booking_date=datetime.utcnow() - timedelta(days=10),
        booking_amount=15,
        booking_used_date=datetime.utcnow() - timedelta(days=5),
        payment_iban='FR7630001007941234567890185',
        payment_message_name='AZERTY123456',
        transaction_end_to_end_id=uuid.uuid4(),
        payment_id=123,
        reimbursement_rate=Decimal(0.5),
        reimbursed_amount=Decimal(7.5)
):
    details = PaymentDetails()
    details.booking_user_id = booking_user_id
    details.booking_user_email = booking_user_email
    details.offerer_name = offerer_name
    details.offerer_siren = offerer_siren
    details.venue_name = venue_name
    details.venue_siret = venue_siret
    details.offer_name = offer_name
    details.offer_type = str(offer_type)
    details.booking_date = booking_date
    details.booking_amount = booking_amount
    details.booking_used_date = booking_used_date
    details.payment_iban = payment_iban
    details.payment_message_name = payment_message_name
    details.transaction_end_to_end_id = transaction_end_to_end_id
    details.payment_id = payment_id
    details.reimbursement_rate = reimbursement_rate
    details.reimbursed_amount = reimbursed_amount
    return details


def create_bank_information(application_id=1, bic='QSDFGH8Z555', iban='FR7630006000011234567890189',
                            id_at_providers='234567891', date_modified_at_last_provider=datetime(2019, 1, 1),
                            offerer=None, venue=None, last_provider_id=None):
    bank_information = BankInformation()
    bank_information.offerer = offerer
    bank_information.venue = venue
    bank_information.applicationId = application_id
    bank_information.bic = bic
    bank_information.iban = iban
    bank_information.idAtProviders = id_at_providers
    bank_information.dateModifiedAtLastProvider = date_modified_at_last_provider
    bank_information.lastProviderId = get_provider_by_local_class('BankInformationProvider').id
    return bank_information


def create_email(content, status=EmailStatus.ERROR, time=datetime.utcnow()):
    email_failed = Email()
    email_failed.content = content
    email_failed.status = status
    email_failed.datetime = time
    return email_failed


def saveCounts():
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isclass(model) \
                and issubclass(model, PcObject) \
                and modelName != "PcObject":
            saved_counts[modelName] = model.query.count()


def assertCreatedCounts(**counts):
    for modelName in counts:
        model = getattr(models, modelName)
        all_records_count = model.query.count()
        previous_records_count = saved_counts[modelName]
        last_created_count = all_records_count - previous_records_count
        assert last_created_count == counts[modelName], \
            'Model [%s], Actual [%s], Expected [%s]' % (modelName, last_created_count, counts[modelName])


def assertEmptyDb():
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isinstance(model, PcObject):
            if modelName == 'Mediation':
                assert model.query.count() == 2
            else:
                assert model.query.count() == 0


def assert_created_thumbs():
    assert len(glob(str(STORAGE_DIR / "thumbs" / "*"))) == 1


def provider_test(app, provider, venue_provider, **counts):
    if venue_provider is None:
        provider_object = provider()
    else:
        provider_object = provider(venue_provider)
    provider_object.provider.isActive = True
    PcObject.save(provider_object.provider)
    saveCounts()
    provider_object.updateObjects()

    for countName in ['updatedObjects',
                      'createdObjects',
                      'checkedObjects',
                      'erroredObjects',
                      'createdThumbs',
                      'updatedThumbs',
                      'checkedThumbs',
                      'erroredThumbs']:
        assert getattr(provider_object, countName) == counts[countName]
        del counts[countName]
    assertCreatedCounts(**counts)


def save_all_activities(*objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()


def get_occurrence_short_name(concatened_names_with_a_date):
    splitted_names = concatened_names_with_a_date.split(' / ')
    if len(splitted_names) > 0:
        return splitted_names[0]
    else:
        return None


def get_price_by_short_name(occurrence_short_name=None):
    if occurrence_short_name is None:
        return 0
    else:
        return sum(map(ord, occurrence_short_name)) % 50


def create_venue_provider(venue, provider, venue_id_at_offer_provider='77567146400110', is_active=True):
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.isActive = is_active
    venue_provider.provider = provider
    venue_provider.venueIdAtOfferProvider = venue_id_at_offer_provider
    return venue_provider


def activate_provider(provider_classname: str) -> Provider:
    provider = get_provider_by_local_class(provider_classname)
    provider.isActive = True
    provider.enabledForPro = True
    PcObject.save(provider)
    return provider


def deactivate_feature(feature_toggle: FeatureToggle):
    feature = Feature.query.filter_by(name=feature_toggle.name).one()
    feature.isActive = False
    PcObject.save(feature)


def create_provider(local_class: str, is_active: bool = True, is_enable_for_pro: bool = True) -> Provider:
    provider = Provider()
    provider.localClass = local_class
    provider.isActive = is_active
    provider.name = 'My Test Provider'
    provider.enabledForPro = is_enable_for_pro
    return provider


def create_providable_info(model_name: Model = Product,
                           id_at_providers: str = '1',
                           date_modified: datetime = None) -> ProvidableInfo:
    providable_info = ProvidableInfo()
    providable_info.type = model_name
    providable_info.id_at_providers = id_at_providers
    if date_modified:
        providable_info.date_modified_at_provider = date_modified
    else:
        providable_info.date_modified_at_provider = datetime.utcnow()
    return providable_info


def create_api_key(offerer, value):
    offererApiKey = ApiKey()
    offererApiKey.value = value
    offererApiKey.offererId = offerer.id

    PcObject.save(offererApiKey)

    return offererApiKey


def assert_iterator_is_empty(custom_iterator: iter):
    with pytest.raises(StopIteration):
        next(custom_iterator)
