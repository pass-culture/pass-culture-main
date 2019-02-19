""" test utils """
import random
import requests as req
import string
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from glob import glob
from hashlib import sha256
from inspect import isclass
from postgresql_audit.flask import versioning_manager
from unittest.mock import Mock

import models
from models import Booking, \
    Deposit, \
    Event, \
    EventOccurrence, \
    EventType, \
    Mediation, \
    Offer, \
    Offerer, \
    Payment, \
    Recommendation, \
    RightsType, \
    Stock, \
    Thing, \
    ThingType, \
    User, \
    UserOfferer, \
    Venue, PaymentTransaction, BankInformation
from models.db import db
from models.payment import PaymentDetails
from models.payment_status import PaymentStatus, TransactionStatus
from models.pc_object import PcObject
from utils.object_storage import STORAGE_DIR
from utils.token import random_token

saved_counts = {}

USER_TEST_ADMIN_EMAIL = "pctest.admin93.0@btmx.fr"
USER_TEST_ADMIN_PASSWORD = "pctest.Admin93.0"
API_URL = "http://localhost:5000"


def req_with_auth(email=None, password=None, headers={'origin': 'http://localhost:3000'}):
    request = req.Session()
    request.headers = headers
    if email is None:
        request.auth = (USER_TEST_ADMIN_EMAIL, USER_TEST_ADMIN_PASSWORD)
    elif password is not None:
        request.auth = (email, password)
    return request


def create_booking(user, stock=None, venue=None, recommendation=None, quantity=1, date_created=datetime.utcnow(),
                   is_cancelled=False, is_used=False, token=None, idx=None, amount=None):

    booking = Booking()
    if venue is None:
        offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
    if stock is None:
        thing_offer = create_thing_offer(venue)
        stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
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
        offer = create_thing_offer(venue)
        booking.recommendation = create_recommendation(offer, user)
    else:
        booking.recommendation = create_recommendation(stock.offer, user)
    booking.isCancelled = is_cancelled
    booking.isUsed = is_used
    booking.id = idx
    return booking


def create_booking_for_thing(
        url=None,
        amount=50,
        quantity=1,
        user=None,
        isCancelled=False,
        type=ThingType.JEUX,
        date_created=datetime.utcnow()
):
    thing = Thing(from_dict={'url': url, 'type': str(type)})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.thing = thing
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    booking.user = user
    booking.isCancelled = isCancelled
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
    event = Event(from_dict={'type': str(type)})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.event = event
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    booking.user = user
    booking.isCancelled = isCancelled
    booking.token = random_token()
    booking.dateCreated = date_created
    return booking


def create_user(public_name='John Doe', first_name='John', last_name='Doe', postal_code='93100', departement_code='93',
                email='john.doe@test.com', can_book_free_offers=True, password='totallysafepsswd',
                validation_token=None, is_admin=False, reset_password_token=None,
                reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24),
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
    user.setPassword(password)
    user.isAdmin = is_admin
    user.resetPasswordToken = reset_password_token
    user.resetPasswordTokenValidityLimit = reset_password_token_validity_limit
    user.dateCreated = date_created
    user.phoneNumber = phone_number
    user.dateOfBirth = date_of_birth
    user.id = idx
    return user


def create_stock_with_event_offer(
        offerer,
        venue,
        beginning_datetime_future=True,
        price=10,
        booking_email='offer.booking.email@test.com',
        available=10,
        is_soft_deleted=False,
        event_type=EventType.JEUX,
        name='Mains, sorts et papiers',
        offer_id=None):
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
    stock.available = available

    stock.eventOccurrence = EventOccurrence()
    if beginning_datetime_future:
        stock.eventOccurrence.beginningDatetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        stock.eventOccurrence.endDatetime = datetime(2019, 7, 20, 12, 10, 0, tzinfo=timezone.utc)
        stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    else:
        stock.eventOccurrence.beginningDatetime = datetime(2017, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        stock.eventOccurrence.endDatetime = datetime(2017, 7, 20, 12, 10, 0, tzinfo=timezone.utc)
        stock.bookingLimitDatetime = datetime.utcnow() - timedelta(days=800)
    stock.eventOccurrence.offer = Offer()
    stock.eventOccurrence.offer.bookingEmail = booking_email
    stock.eventOccurrence.offer.event = Event(
        from_dict={
            'isNational': False,
            'durationMinutes': 10,
            'name': name,
            'type': str(event_type)}
    )
    stock.eventOccurrence.offer.id = offer_id
    stock.eventOccurrence.offer.venue = venue
    stock.isSoftDeleted = is_soft_deleted

    return stock


def create_stock_from_event_occurrence(event_occurrence, price=10, available=10, soft_deleted=False, recap_sent=False,
                                       booking_limit_date=None):
    stock = Stock()
    stock.eventOccurrence = event_occurrence
    stock.price = price
    stock.available = available
    stock.isSoftDeleted = soft_deleted
    if recap_sent:
        stock.bookingRecapSent = datetime.utcnow()
    if booking_limit_date is None:
        stock.bookingLimitDatetime = event_occurrence.beginningDatetime
    else:
        stock.bookingLimitDatetime = booking_limit_date
    return stock


def create_stock_from_offer(offer, price=10, available=10, soft_deleted=False, booking_limit_datetime=None):
    stock = Stock()
    stock.offer = offer
    stock.price = price
    stock.available = available
    stock.isSoftDeleted = soft_deleted
    stock.bookingLimitDatetime = booking_limit_datetime
    return stock


def create_stock(price=10, available=10, booking_limit_datetime=None, offer=None):
    stock = Stock()
    stock.price = price
    stock.available = available
    stock.bookingLimitDatetime = booking_limit_datetime
    stock.offer = offer
    return stock


def create_stock_with_thing_offer(offerer, venue, thing_offer=None, price=10, available=50,
                                  booking_email='offer.booking.email@test.com', soft_deleted=False,
                                  booking_limit_datetime=None):
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
    if thing_offer:
        stock.offer = thing_offer
    else:
        stock.offer = create_thing_offer(venue)
    stock.offer.bookingEmail = booking_email
    stock.bookingLimitDatetime = booking_limit_datetime

    stock.offer.venue = venue
    stock.available = available
    stock.isSoftDeleted = soft_deleted
    return stock


def create_thing(
        thing_name='Test Book',
        thing_type=ThingType.LIVRE_EDITION,
        author_name='Test Author',
        is_national=False,
        id_at_providers=None,
        media_urls=['test/urls'],
        description=None,
        dominant_color=None,
        thumb_count=1,
        url=None
):
    thing = Thing()
    thing.type = str(thing_type)
    thing.name = thing_name
    thing.description = description
    thing.extraData = {'author': author_name}
    thing.isNational = is_national
    if id_at_providers is None:
        id_at_providers = ''.join(random.choices(string.digits, k=13))
    thing.idAtProviders = id_at_providers
    thing.mediaUrls = media_urls
    thing.thumbCount = thumb_count
    thing.url = url

    if thumb_count > 0:
        if dominant_color is None:
            thing.firstThumbDominantColor = b'\x00\x00\x00'
        else:
            thing.firstThumbDominantColor = dominant_color
    thing.description = description
    return thing


def create_event(
        event_name='Test event',
        event_type=EventType.SPECTACLE_VIVANT,
        description=None,
        dominant_color=None,
        duration_minutes=60,
        is_national=False,
        thumb_count=0,
):
    event = Event()
    event.name = event_name
    event.description = description
    event.durationMinutes = duration_minutes
    event.thumbCount = thumb_count
    event.isNational = is_national
    event.type = str(event_type)
    event.firstThumbDominantColor = dominant_color
    if event.thumbCount > 0 and not dominant_color:
        event.firstThumbDominantColor = b'\x00\x00\x00'
    event.description = description
    return event


def create_thing_offer(venue, thing=None, date_created=datetime.utcnow(), booking_email='booking.email@test.com',
                       thing_type=ThingType.AUDIOVISUEL, thing_name='Test Book', media_urls=['test/urls'],
                       author_name='Test Author',
                       thumb_count=1, dominant_color=None, url=None, is_national=False, is_active=True,
                       id_at_providers=None, idx=None):
    offer = Offer()
    if thing:
        offer.thing = thing
    else:
        offer.thing = create_thing(thing_name=thing_name, thing_type=thing_type, media_urls=media_urls,
                                   author_name=author_name, url=url, thumb_count=thumb_count,
                                   dominant_color=dominant_color, is_national=is_national)
    offer.venue = venue
    offer.dateCreated = date_created
    offer.bookingEmail = booking_email
    offer.isActive = is_active

    if id_at_providers:
        offer.id_at_providers = id_at_providers
    elif venue is not None:
        offer.idAtProviders = "%s@%s" % (offer.thing.idAtProviders, venue.siret or venue.id)
    offer.id = idx

    return offer


def create_event_offer(venue, event=None, event_name='Test event', duration_minutes=60, date_created=datetime.utcnow(),
                       booking_email='booking.email@test.com', thumb_count=0, dominant_color=None,
                       event_type=EventType.SPECTACLE_VIVANT, is_national=False, is_active=True, idx=None):
    offer = Offer()
    if event is None:
        event = create_event(event_name=event_name, event_type=event_type, duration_minutes=duration_minutes,
                             thumb_count=thumb_count, dominant_color=dominant_color, is_national=is_national)
    offer.event = event
    offer.venue = venue
    offer.dateCreated = date_created
    offer.bookingEmail = booking_email
    offer.isActive = is_active
    offer.id = idx
    return offer


def create_n_mixed_offers_with_same_venue(venue, n=10):
    offers = []
    for i in range(n // 2, 0, -1):
        date_created = datetime.utcnow() - timedelta(days=i)
        offers.append(create_thing_offer(venue, date_created=date_created, thing_name='Thing Offer %s' % i))
        offers.append(create_event_offer(venue, event_name='Event Offer %s' % i, date_created=date_created))
    return offers


def create_offerer(
        siren='123456789',
        address='123 rue de Paris',
        city='Montreuil',
        postal_code='93100',
        name='Test Offerer',
        validation_token=None,
        iban=None,
        bic=None,
        idx=None,
        is_active=True,
        date_created=datetime.utcnow()
):
    offerer = Offerer()
    offerer.siren = siren
    offerer.isActive = is_active
    offerer.address = address
    offerer.postalCode = postal_code
    offerer.city = city
    offerer.name = name
    offerer.validationToken = validation_token
    offerer.bic = bic
    offerer.iban = iban
    offerer.id = idx
    offerer.dateCreated = date_created
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
        iban=None,
        bic=None,
        longitude='2.4002701',
        latitude='48.8363788',
        siret='12345678912345',
        validation_token=None,
        comment=None,
        idx=None
):
    venue = Venue()
    venue.bookingEmail = booking_email
    if not is_virtual:
        venue.address = address
        venue.postalCode = postal_code
        venue.city = city
        venue.departementCode = departement_code
    venue.name = name
    venue.managingOfferer = offerer
    venue.isVirtual = is_virtual
    venue.iban = iban
    venue.bic = bic
    venue.longitude = longitude
    venue.latitude = latitude
    venue.siret = siret
    venue.validationToken = validation_token
    venue.comment = comment
    venue.id = idx
    return venue


def create_deposit(user, date, amount=50, source='public'):
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
                          valid_until_date=datetime.utcnow() + timedelta(days=7), search=None,
                          is_clicked=False, is_favorite=False):
    recommendation = Recommendation()
    recommendation.id = idx
    recommendation.offer = offer
    recommendation.user = user
    recommendation.mediation = mediation
    recommendation.dateRead = date_read
    recommendation.validUntilDate = valid_until_date
    recommendation.search = search
    recommendation.isClicked = is_clicked
    recommendation.isFavorite = is_favorite
    return recommendation


def create_event_occurrence(
        offer,
        beginning_datetime=datetime.utcnow() + timedelta(hours=2),
        end_datetime=datetime.utcnow() + timedelta(hours=5)
):
    event_occurrence = EventOccurrence()
    event_occurrence.offer = offer
    event_occurrence.beginningDatetime = beginning_datetime
    event_occurrence.endDatetime = end_datetime
    return event_occurrence


def create_mediation(offer, author=None, date_created=datetime.utcnow(), front_text='Some front text',
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


def create_venue_activity(venue, table_name, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
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
        booking.stock.resolvedOffer.eventOrThing.name = name
        bookings.append(booking)
    return bookings


def create_payment(booking, offerer, amount, author='test author', reimbursement_rule='remboursement à 100%',
                   reimbursement_rate=Decimal(0.5),
                   transaction_message_id=None,
                   transaction_end_ot_end_id=None,
                   custom_message='pass Culture Pro - remboursement 2nde quinzaine 07-2018',
                   status=TransactionStatus.PENDING,
                   idx=None):
    payment = Payment()
    payment.booking = booking
    payment.amount = amount
    payment.author = author
    payment.iban = offerer.iban
    payment.bic = offerer.bic
    payment.recipientName = offerer.name
    payment.recipientSiren = offerer.siren
    payment_status = PaymentStatus()
    payment_status.status = status
    payment_status.date = datetime.utcnow()
    payment.statuses = [payment_status]
    payment.reimbursementRule = reimbursement_rule
    payment.reimbursementRate = reimbursement_rate

    if transaction_message_id:
        payment.transaction = create_payment_transaction(transaction_message_id)

    payment.transactionEndToEndId = transaction_end_ot_end_id
    payment.customMessage = custom_message
    payment.id = idx
    return payment


def create_payment_transaction(transaction_message_id="ABCD123", checksum=None):
    transaction = PaymentTransaction()
    transaction.messageId = transaction_message_id
    if checksum:
        transaction.checksum = checksum
    else:
        transaction.checksum = sha256(transaction_message_id.encode('utf-8')).digest()
    return transaction


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
        transaction_message_id='AZERTY123456',
        transaction_end_to_end_id=uuid.uuid4(),
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
    details.transaction_message_id = transaction_message_id
    details.transaction_end_to_end_id = transaction_end_to_end_id
    details.reimbursement_rate = reimbursement_rate
    details.reimbursed_amount = reimbursed_amount
    return details


def create_bank_information(application_id=1, bic='QSDFGH8Z555', iban='CF13QSDFGH456789', id_at_providers='234567891',
                            date_modified_at_last_provider=datetime(2019, 1, 1), offerer_id=None,
                            venue_id=None):
    bank_information = BankInformation()
    bank_information.venueId = venue_id
    bank_information.offererId = offerer_id
    bank_information.applicationId = application_id
    bank_information.bic = bic
    bank_information.iban = iban
    bank_information.idAtProviders = id_at_providers
    bank_information.dateModifiedAtLastProvider = date_modified_at_last_provider
    return bank_information


def saveCounts(app):
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isclass(model) \
                and issubclass(model, PcObject) \
                and modelName != "PcObject":
            saved_counts[modelName] = model.query.count()


def assertCreatedCounts(app, **counts):
    for modelName in counts:
        model = getattr(models, modelName)
        assert model.query.count() - saved_counts[modelName] \
               == counts[modelName]


def assertEmptyDb(app):
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isinstance(model, PcObject):
            if modelName == 'Mediation':
                assert model.query.count() == 2
            else:
                assert model.query.count() == 0


def assert_created_thumbs():
    assert len(glob(str(STORAGE_DIR / "thumbs" / "*"))) == 1


def provider_test(app, provider, venueProvider, **counts):
    providerObj = provider(venueProvider, mock=True)
    providerObj.dbObject.isActive = True
    PcObject.check_and_save(providerObj.dbObject)
    saveCounts(app)
    providerObj.updateObjects()

    for countName in ['updatedObjects',
                      'createdObjects',
                      'checkedObjects',
                      'erroredObjects',
                      'createdThumbs',
                      'updatedThumbs',
                      'checkedThumbs',
                      'erroredThumbs']:
        assert getattr(providerObj, countName) == counts[countName]
        del counts[countName]
    assertCreatedCounts(app, **counts)


def provider_test_without_mock(app, provider, **counts):
    providerObj = provider()
    providerObj.dbObject.isActive = True
    PcObject.check_and_save(providerObj.dbObject)
    saveCounts(app)
    providerObj.updateObjects()

    for countName in ['updatedObjects',
                      'createdObjects',
                      'checkedObjects',
                      'erroredObjects',
                      'createdThumbs',
                      'updatedThumbs',
                      'checkedThumbs',
                      'erroredThumbs']:
        assert getattr(providerObj, countName) == counts[countName]
        del counts[countName]
    assertCreatedCounts(app, **counts)


def save_all_activities(*objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()


def check_open_agenda_api_is_down():
    response = req.get('https://openagenda.com/agendas/86585975/events.json?limit=1')
    response_json = response.json()
    unsuccessful_request = ('success' in response_json) and not response_json['success']
    status_code_not_200 = (response.status_code != 200)
    return unsuccessful_request or status_code_not_200

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
