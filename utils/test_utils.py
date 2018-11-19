""" test utils """
import random
import string
from datetime import datetime, timedelta, timezone
from glob import glob
from inspect import isclass
from unittest.mock import Mock
import requests as req
from postgresql_audit.flask import versioning_manager

from models.pc_object import PcObject
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
                   Venue
import models
from models.payment_status import PaymentStatus, TransactionStatus
from utils.object_storage import STORAGE_DIR
from utils.token import random_token

savedCounts = {}

USER_TEST_ADMIN_EMAIL="pctest.admin.1@btmx.fr"
USER_TEST_ADMIN_PASSWORD="pctest.Admin.1"
API_URL = "http://localhost:5000"
MOCKED_SIREN_ENTREPRISES_API_RETURN = {
    'numero_tva_intra': 'FR60732075312',
    'other_etablissements_sirets': ['73207531200213',
                                    '73207531200197',
                                    '73207531200171'],
    'siege_social':
        {
            'activite_principale': '6202A',
            'activite_principale_entreprise': '6202A',
            'activite_principale_entreprise_esa': '6202A',
            'activite_principale_registre_metier': None,
            'arrondissement': '1',
            'canton': None,
            'caractere_auxiliaire': '0',
            'caractere_productif': 'O',
            'caractere_productif_entreprise': 'O',
            'categorie_entreprise': 'GE',
            'cedex': None,
            'civilite': None,
            'code_postal': '75013',
            'commune': '113',
            'created_at': '2018-08-01T04:27:08.000Z',
            'date_creation': '20030206',
            'date_creation_entreprise': '19000101',
            'date_debut_activite': '20030206',
            'date_ess': '20170430',
            'date_evenement': None,
            'date_introduction_base_diffusion': '201209',
            'date_introduction_base_diffusion_entreprise': '201209',
            'date_mise_a_jour': '2017-08-06T00:00:00',
            'date_reactivation_entreprise': None,
            'date_reactivation_etablissement': None,
            'date_validite_activite_principale': None,
            'date_validite_activite_principale_entreprise': '2011',
            'date_validite_effectif_salarie': '2016',
            'date_validite_effectif_salarie_entreprise': '2016',
            'date_validite_rubrique_niveau_entreprise_esa': '2014',
            'departement': '75',
            'departement_commune_siege': '75113',
            'departement_unite_urbaine': '00',
            'deuxieme_activite_secondaire_entreprise_esa': '6202B',
            'email': None,
            'enseigne': None,
            'etablissement_public_cooperation_intercommunale': '200054781',
            'geo_adresse': '118 Avenue de France 75013 Paris',
            'geo_id': 'ADRNIVX_0000000270816177',
            'geo_ligne': 'G',
            'geo_score': '0.84',
            'geo_type': 'housenumber',
            'id': 98709570,
            'indicateur_champ_publipostage': '1',
            'indicateur_mise_a_jour_1': None,
            'indicateur_mise_a_jour_2': None,
            'indicateur_mise_a_jour_3': None,
            'indicateur_mise_a_jour_activite_principale_entreprise': None,
            'indicateur_mise_a_jour_activite_principale_etablissement': None,
            'indicateur_mise_a_jour_adresse_etablissement': None,
            'indicateur_mise_a_jour_caractere_auxiliaire_etablissement': None,
            'indicateur_mise_a_jour_caractere_productif_entreprise': None,
            'indicateur_mise_a_jour_caractere_productif_etablissement': None,
            'indicateur_mise_a_jour_enseigne_entreprise': None,
            'indicateur_mise_a_jour_nature_juridique': None,
            'indicateur_mise_a_jour_nic_siege': None,
            'indicateur_mise_a_jour_nom_raison_sociale': None,
            'indicateur_mise_a_jour_sigle': None,
            'indice_monoactivite_entreprise': '2',
            'indice_repetition': None,
            'is_ess': 'N',
            'is_saisonnier': 'P',
            'is_siege': '1',
            'l1_declaree': 'ACCENTURE',
            'l1_normalisee': 'ACCENTURE',
            'l2_declaree': 'ACCENTURE',
            'l2_normalisee': '118 122',
            'l3_declaree': '118-122',
            'l3_normalisee': None,
            'l4_declaree': '118 AV DE FRANCE',
            'l4_normalisee': '118 AVENUE DE FRANCE',
            'l5_declaree': None,
            'l5_normalisee': None,
            'l6_declaree': '75013 PARIS 13',
            'l6_normalisee': '75636 PARIS CEDEX 13',
            'l7_declaree': None,
            'l7_normalisee': 'FRANCE',
            'latitude': '48.830899',
            'libelle_activite_principale': 'Conseil en systèmes et logiciels informatiques',
            'libelle_activite_principale_entreprise': 'Conseil en systèmes et logiciels informatiques',
            'libelle_commune': 'PARIS 13',
            'libelle_nature_entrepreneur_individuel': None,
            'libelle_nature_juridique_entreprise': 'SAS, société par actions simplifiée',
            'libelle_region': 'Île-de-France',
            'libelle_tranche_effectif_salarie': '2 000 à 4 999 salariés',
            'libelle_tranche_effectif_salarie_entreprise': '2 000 à 4 999 salariés',
            'libelle_voie': 'DE FRANCE',
            'lieu_activite': '99',
            'longitude': '2.376638',
            'modalite_activite_principale': 'S',
            'modalite_activite_principale_entreprise': 'S',
            'nature_activite': '99',
            'nature_entrepreneur_individuel': None,
            'nature_juridique_entreprise': '5710',
            'nature_mise_a_jour': None,
            'nic': '00122',
            'nic_siege': '00122',
            'nom': None,
            'nom_raison_sociale': 'ACCENTURE',
            'numero_rna': None,
            'numero_unite_urbaine': '51',
            'numero_voie': '118',
            'origine_creation': '9',
            'participation_particuliere_production': None,
            'premiere_activite_secondaire_entreprise_esa': '6202A',
            'prenom': None,
            'quatrieme_activite_secondaire_entreprise_esa': '6311Z',
            'region': '11',
            'region_siege': '11',
            'sigle': None,
            'siren': '732075312',
            'siret': '73207531200122',
            'siret_predecesseur_successeur': None,
            'statut_prospection': 'O',
            'taille_unite_urbaine': '8',
            'telephone': None,
            'tranche_chiffre_affaire_entreprise_esa': '9',
            'tranche_commune_detaillee': '80',
            'tranche_effectif_salarie': '51',
            'tranche_effectif_salarie_centaine_pret': '3200',
            'tranche_effectif_salarie_entreprise': '51',
            'tranche_effectif_salarie_entreprise_centaine_pret': '3600',
            'troisieme_activite_secondaire_entreprise_esa': '6203Z',
            'type_creation': None,
            'type_evenement': None,
            'type_magasin': None,
            'type_voie': 'AV',
            'updated_at': '2018-08-01T04:27:08.000Z',
            'zone_emploi': '1101'
        },
    'total_results': 6
}

ONE_PIXEL_PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03PLTE`\x00\x86\xebv\xd0\xef\x00\x00\x00\x01tRNS\xcc\xd24V\xfd\x00\x00\x00\nIDATx\x9ccb\x00\x00\x00\x06\x00\x0367|\xa8\x00\x00\x00\x00IEND\xaeB`\x82'


def req_with_auth(email=None, password=None, headers={'origin': 'http://localhost:3000'}):
    request = req.Session()
    request.headers = headers
    if email is None:
        request.auth = (USER_TEST_ADMIN_EMAIL, USER_TEST_ADMIN_PASSWORD)
    elif password is not None:
        request.auth = (email, password)
    return request


def create_booking(user, stock=None, venue=None, recommendation=None, quantity=1, date_created=datetime.utcnow(),
                   is_cancelled=False, is_used=False, token=None):
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
    booking.amount = stock.price
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
    return booking


def create_booking_for_thing(url=None, amount=50, quantity=1, user=None, date_created=datetime.utcnow()):
    thing = Thing(from_dict={'url': url})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.thing = thing
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    booking.user = user
    booking.dateCreated = date_created
    return booking


def create_booking_for_event(
        amount=50,
        quantity=1,
        user=None,
        isCancelled=False,
        date_created=datetime.utcnow()
):
    event = Event()
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
                date_created=datetime.utcnow()):
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
    return user


def create_stock_with_event_offer(
        offerer,
        venue,
        beginning_datetime_future=True,
        price=10,
        booking_email='offer.booking.email@test.com',
        available=10
):
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
        from_dict={'isNational': False, 'durationMinutes': 10, 'name': 'Mains, sorts et papiers'}
    )
    stock.eventOccurrence.offer.venue = venue

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


def create_stock(price=10, available=10, booking_limit_datetime=None):
    stock = Stock()
    stock.price = price
    stock.available = available
    stock.bookingLimitDatetime = booking_limit_datetime
    return stock


def create_stock_with_thing_offer(offerer, venue, thing_offer, price=10, available=50,
                                  booking_email='offer.booking.email@test.com'):
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
    if thing_offer:
        stock.offer = thing_offer
    else:
        stock.offer = create_thing_offer(venue)
    stock.offer.bookingEmail = booking_email
    stock.offer.venue = venue
    stock.available = available
    return stock


def create_thing(thing_name='Test Book', thing_type=ThingType.LIVRE_EDITION, media_urls=['test/urls'],
                 author_name='Test Author', url=None, thumb_count=1, dominant_color=None, is_national=False,
                 id_at_providers=None, description=None):
    thing = Thing()
    thing.type = str(thing_type)
    thing.name = thing_name
    thing.mediaUrls = media_urls
    if id_at_providers is None:
        id_at_providers = ''.join(random.choices(string.digits, k=13))
    thing.idAtProviders = id_at_providers
    thing.extraData = {'author': author_name}
    thing.url = url
    thing.thumbCount = thumb_count
    thing.isNational = is_national
    if thumb_count > 0:
        if dominant_color is None:
            thing.firstThumbDominantColor = b'\x00\x00\x00'
        else:
            thing.firstThumbDominantColor = dominant_color
    thing.description = description
    return thing


def create_event(event_name='Test event', event_type=EventType.SPECTACLE_VIVANT, duration_minutes=60,
                 thumb_count=0, dominant_color=None, is_national=False, description=None):
    event = Event()
    event.name = event_name
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
                       thing_type=ThingType.AUDIOVISUEL, thing_name='Test Book', media_urls=['test/urls'], author_name='Test Author',
                       thumb_count=1, dominant_color=None, url=None, is_national=False, is_active=True):
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

    if venue is not None:
        offer.idAtProviders = "%s@%s" % (offer.thing.idAtProviders, venue.siret or venue.id)
    return offer


def create_event_offer(venue, event=None, event_name='Test event', duration_minutes=60, date_created=datetime.utcnow(),
                       booking_email='booking.email@test.com', thumb_count=0, dominant_color=None,
                       event_type=EventType.SPECTACLE_VIVANT, is_national=False, is_active=True):
    offer = Offer()
    if event is None:
        event = create_event(event_name=event_name, event_type=event_type, duration_minutes=duration_minutes,
                             thumb_count=thumb_count, dominant_color=dominant_color, is_national=is_national)
    offer.event = event
    offer.venue = venue
    offer.dateCreated = date_created
    offer.bookingEmail = booking_email
    offer.isActive = is_active
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
        idx=None
):
    offerer = Offerer()
    offerer.siren = siren
    offerer.isActive = True
    offerer.address = address
    offerer.postalCode = postal_code
    offerer.city = city
    offerer.name = name
    offerer.validationToken = validation_token
    offerer.bic = bic
    offerer.iban = iban
    offerer.id = idx
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
                          valid_until_date=datetime.utcnow() + timedelta(days=7), search=None, is_favorite=False):
    recommendation = Recommendation()
    recommendation.id = idx
    recommendation.offer = offer
    recommendation.user = user
    recommendation.mediation = mediation
    recommendation.dateRead = date_read
    recommendation.validUntilDate = valid_until_date
    recommendation.search = search
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
                     back_text='Some back test', is_active=True):
    mediation = Mediation()
    mediation.offer = offer
    mediation.dateCreated = date_created
    mediation.frontText = front_text
    mediation.backText = back_text
    mediation.author = author
    mediation.isActive = is_active
    return mediation


def create_booking_activity(booking, table_name, verb, issued_at=datetime.utcnow):
    Activity = versioning_manager.activity_cls
    activity = Activity()
    activity.issued_at = issued_at
    activity.table_name = table_name
    activity.verb = verb
    variables = {"id": booking.id, "token": booking.token, "userId": booking.userId, "stockId": booking.stockId,
                 "isCancelled": booking.isCancelled, "quantity": booking.quantity,
                 "recommendationId": booking.recommendationId, "isUsed": booking.isUsed}
    activity.changed_data = variables
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


def create_mocked_bookings(num_bookings, venue_email, name='Offer name'):
    bookings = []
    for i in range(num_bookings):
        booking = Mock(spec=Booking)
        booking.user.email = 'user_email%s' % i
        booking.user.firstName = 'First %s' % i
        booking.user.lastName = 'Last %s' % i
        booking.stock.resolvedOffer.venue.bookingEmail = venue_email
        booking.stock.resolvedOffer.eventOrThing.name = name
        bookings.append(booking)
    return bookings


def create_payment(booking, offerer, amount, author='test author', recipient='recipient',
                   reimbursement_rule='remboursement à 100%', idx=None):
    payment = Payment()
    payment.booking = booking
    payment.amount = amount
    payment.author = author
    payment.iban = offerer.iban
    payment.bic = offerer.bic
    payment.recipient = recipient
    payment_status = PaymentStatus()
    payment_status.status = TransactionStatus.PENDING
    payment.statuses = [payment_status]
    payment.reimbursementRule = reimbursement_rule
    payment.id = idx
    return payment


def saveCounts(app):
    for modelName in models.__all__:
        model = getattr(models, modelName)
        if isclass(model) \
                and issubclass(model, PcObject) \
                and modelName != "PcObject":
            savedCounts[modelName] = model.query.count()


def assertCreatedCounts(app, **counts):
    for modelName in counts:
        model = getattr(models, modelName)
        assert model.query.count() - savedCounts[modelName] \
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
