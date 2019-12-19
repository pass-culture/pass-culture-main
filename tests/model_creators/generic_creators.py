import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from hashlib import sha256

from local_providers.price_rule import PriceRule
from models import User, Recommendation, Stock, Venue, Booking, Criterion, ImportStatus, BeneficiaryImportStatus, \
    BeneficiaryImport, Offerer, Deposit, UserOfferer, RightsType, Favorite, Mediation, Payment, PaymentStatus, \
    PaymentMessage, ThingType, BankInformation, Email, VenueProvider, Provider, ApiKey, PcObject, VenueProviderPriceRule
from models.email import EmailStatus
from models.payment import PaymentDetails
from models.payment_status import TransactionStatus
from repository.provider_queries import get_provider_by_local_class
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_stock_with_thing_offer
from utils.token import random_token

USER_TEST_ADMIN_EMAIL = "pctest.admin93.0@btmx.fr"
USER_TEST_ADMIN_PASSWORD = "pctest.Admin93.0"
API_URL = "http://localhost:5000"
default_user = User()
PLAIN_DEFAULT_TESTING_PASSWORD = 'user@AZERTY123'
default_user.setPassword(PLAIN_DEFAULT_TESTING_PASSWORD)
HASHED_DEFAULT_TESTING_PASSWORD = default_user.password


def create_booking(user: User,
                   amount: int = None,
                   date_created: datetime = datetime.utcnow(),
                   date_used: datetime = None,
                   id: int = None,
                   is_cancelled: bool = False,
                   is_used: bool = False,
                   quantity: int = 1,
                   recommendation: Recommendation = None,
                   stock: Stock = None,
                   token: str = None,
                   venue: Venue = None):
    booking = Booking()
    offerer = create_offerer('987654321', 'Test address', 'Test city', '93000', 'Test name')
    if venue is None:
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
    if stock is None:
        price = amount if amount is not None else 10
        product_with_thing_type = create_offer_with_thing_product(venue)
        stock = create_stock_with_thing_offer(offerer, venue, product_with_thing_type, price=price)

    if recommendation:
        booking.recommendation = recommendation
    elif not stock.offer:
        offer = create_offer_with_thing_product(venue)
        booking.recommendation = create_recommendation(offer, user)
    else:
        booking.recommendation = create_recommendation(stock.offer, user)

    booking.user = user
    booking.amount = stock.price
    booking.dateCreated = date_created
    booking.dateUsed = date_used
    booking.id = id
    booking.isCancelled = is_cancelled
    booking.isUsed = is_used
    booking.quantity = quantity
    booking.token = token if token is not None else random_token()
    booking.stock = stock
    return booking


def create_criterion(name: str = 'best offer', description: str = None, score_delta: int = 1):
    criterion = Criterion()
    criterion.name = name
    criterion.description = description
    criterion.scoreDelta = score_delta
    return criterion


def create_user(activity: str = None,
                can_book_free_offers: bool = True,
                civility: str = None,
                cultural_survey_id: int = None,
                cultural_survey_filled_date: datetime = None,
                date_created: datetime = datetime.utcnow(),
                date_of_birth: datetime = datetime(2001, 1, 1),
                departement_code: str = '93',
                email: str = 'john.doe@example.com',
                first_name: str = 'John',
                id: int = None,
                is_admin: bool = False,
                last_name: str = 'Doe',
                needs_to_fill_cultural_survey: bool = False,
                password: str = None,
                phone_number: str = '0612345678',
                postal_code: str = '93100',
                public_name: str = 'John Doe',
                reset_password_token: str = None,
                reset_password_token_validity_limit: datetime = datetime.utcnow() + timedelta(hours=24),
                validation_token: str = None):
    user = User()
    user.activity = activity
    user.canBookFreeOffers = can_book_free_offers
    user.civility = civility
    user.cultural_survey_id = cultural_survey_id
    user.culturalSurveyFilledDate = cultural_survey_filled_date
    user.dateCreated = date_created
    user.dateOfBirth = date_of_birth
    user.departementCode = departement_code
    user.email = email
    user.firstName = first_name
    user.id = id
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
        user.clearTextPassword = PLAIN_DEFAULT_TESTING_PASSWORD
        user.password = HASHED_DEFAULT_TESTING_PASSWORD
        user.resetPasswordToken = reset_password_token
        user.resetPasswordTokenValidityLimit = reset_password_token_validity_limit
    return user


def create_beneficiary_import(
        id: int = None,
        date: datetime = datetime.utcnow(),
        detail: str = None,
        demarche_simplifiee_application_id: int = None,
        status: ImportStatus = ImportStatus.CREATED,
        user: User = None):
    import_status = BeneficiaryImportStatus()
    import_status.id = id
    import_status.date = date
    import_status.detail = detail
    import_status.status = status

    beneficiary_import = BeneficiaryImport()
    beneficiary_import.beneficiary = user
    beneficiary_import.demarcheSimplifieeApplicationId = demarche_simplifiee_application_id
    beneficiary_import.statuses = [import_status]

    return beneficiary_import


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
                          search=None, is_clicked=False,
                          date_created=None):
    recommendation = Recommendation()
    recommendation.id = idx
    recommendation.offer = offer
    recommendation.user = user
    recommendation.mediation = mediation
    recommendation.dateRead = date_read
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


def create_mediation(offer=None, author=None, date_created=datetime.utcnow(), front_text='Some front text',
                     back_text='Some back test', is_active=True, tuto_index=None, idx=None):
    mediation = Mediation()
    mediation.offer = offer
    mediation.dateCreated = date_created
    mediation.frontText = front_text
    mediation.backText = back_text
    mediation.author = author
    mediation.isActive = is_active
    mediation.tutoIndex = tuto_index
    mediation.id = idx
    return mediation


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


def create_venue_provider(venue, provider, venue_id_at_offer_provider='77567146400110', is_active=True):
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.isActive = is_active
    venue_provider.provider = provider
    venue_provider.venueIdAtOfferProvider = venue_id_at_offer_provider
    return venue_provider


def create_provider(local_class: str, is_active: bool = True, is_enable_for_pro: bool = True) -> Provider:
    provider = Provider()
    provider.localClass = local_class
    provider.isActive = is_active
    provider.name = 'My Test Provider'
    provider.enabledForPro = is_enable_for_pro
    return provider


def create_api_key(offerer, value):
    offererApiKey = ApiKey()
    offererApiKey.value = value
    offererApiKey.offererId = offerer.id

    PcObject.save(offererApiKey)

    return offererApiKey

def create_venue_provider_price_rule(venue_provider: VenueProvider,
                                     price_rule: PriceRule = PriceRule.default,
                                     price: int = 10) -> VenueProviderPriceRule:
    venue_provider_price_rule = VenueProviderPriceRule()
    venue_provider_price_rule.venueProvider = venue_provider
    venue_provider_price_rule.priceRule = price_rule
    venue_provider_price_rule.price = price
    return venue_provider_price_rule
