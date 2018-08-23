import json
import random
import string
from datetime import datetime, timedelta, timezone
from os import path
from pathlib import Path

import requests as req

from models import Thing, Deposit, UserOfferer, Recommendation, RightsType
from models.booking import Booking
from models.event import Event
from models.event_occurrence import EventOccurrence
from models.offer import Offer
from models.offerer import Offerer
from models.stock import Stock
from models.user import User
from models.venue import Venue
from utils.token import random_token

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


def req_with_auth(email=None, password=None):
    request = req.Session()
    if email is None:
        request.auth = ('pctest.admin@btmx.fr', 'pctestadmin')
    elif password is not None:
        request.auth = (email, password)
    else:
        json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

        with open(json_path) as json_file:
            for user_json in json.load(json_file):
                print('user_json', user_json)
                if email == user_json['email']:
                    request.auth = (user_json['email'], user_json['password'])
                    break
                raise ValueError("Utilisateur inconnu: " + email)
    return request


def create_booking(user, stock, venue, recommendation, is_cancellation=False, quantity=1, date_modified=datetime.utcnow()):
    booking = Booking()
    booking.stock = stock
    booking.user = user
    booking.token = random_token()
    booking.amount = stock.price
    booking.quantity = quantity
    booking.dateModified = date_modified
    if recommendation:
        booking.recommendation = recommendation
    else:
        offer = create_thing_offer(venue)
        booking.recommendation = create_recommendation(offer, user)
    if not is_cancellation:
        stock.bookings = [booking]
    return booking


def create_user(public_name='John Doe', departement_code='93', email='john.doe@test.com', can_book_free_offers=True,
                password='totallysafepsswd', validation_token=None, is_admin=False):
    user = User()
    user.publicName = public_name
    user.email = email
    user.canBookFreeOffers = can_book_free_offers
    user.departementCode = departement_code
    user.validationToken = validation_token
    user.setPassword(password)
    user.isAdmin = is_admin
    return user


def create_stock_with_event_offer(offerer, venue, beginning_datetime_future=True, price=10):
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
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
    stock.eventOccurrence.offer.event = Event(
        from_dict={'isNational': False, 'durationMinutes': 10, 'name': 'Mains, sorts et papiers'}
    )
    stock.eventOccurrence.offer.venue = venue
    stock.isActive = True
    return stock


def create_stock_with_thing_offer(offerer, venue, thing_offer, price=10, available=50):
    stock = Stock()
    stock.offerer = offerer
    stock.price = price
    if thing_offer:
        stock.offer = thing_offer
    else:
        stock.offer = create_thing_offer(venue)
    stock.offer.venue = venue
    stock.isActive = True
    stock.available = available
    return stock


def create_thing(thing_type='Book', thing_name='Test Book', media_urls='test/urls', author_name='Test Author',
                 url=None):
    thing = Thing()
    thing.type = thing_type
    thing.name = thing_name
    thing.mediaUrls = media_urls
    thing.idAtProviders = ''.join(random.choices(string.digits, k=13))
    thing.extraData = {'author': author_name}
    thing.url = url
    return thing


def create_event(event_name='Test event', duration_minutes=60):
    event = Event()
    event.name = event_name
    event.durationMinutes = duration_minutes
    return event


def create_thing_offer(venue, thing_type='Book', thing_name='Test Book', media_urls='test/urls',
                       author_name='Test Author', date_created=datetime.utcnow()):
    offer = Offer()
    offer.thing = create_thing(thing_type=thing_type, thing_name=thing_name, media_urls=media_urls,
                               author_name=author_name)
    offer.venue = venue
    offer.dateCreated = date_created
    return offer


def create_event_offer(venue, event_name='Test event', duration_minutes=60, date_created=datetime.utcnow()):
    offer = Offer()
    event = create_event(event_name=event_name, duration_minutes=duration_minutes)
    offer.event = event
    offer.venue = venue
    offer.dateCreated = date_created
    return offer


def create_n_mixed_offers_with_same_venue(venue, n=10):
    offers = []
    for i in range(n // 2, 0, -1):
        date_created = datetime.utcnow() - timedelta(days=i)
        offers.append(create_thing_offer(venue, thing_name='Thing Offer %s' % i, date_created=date_created))
        offers.append(create_event_offer(venue, event_name='Event Offer %s' % i, date_created=date_created))
    return offers


def create_offerer(siren='123456789', address='123 rue de Paris', city='Montreuil', postal_code='93100',
                   name='Test Offerer', validation_token=None):
    offerer = Offerer()
    offerer.siren = siren
    offerer.isActive = True
    offerer.address = address
    offerer.postalCode = postal_code
    offerer.city = city
    offerer.name = name
    offerer.validationToken = validation_token
    return offerer


def create_venue(offerer, name='La petite librairie', booking_email='john.doe@test.com', address='123 rue de Paris',
                 postal_code='93100', city='Montreuil', departement_code='93', is_virtual=False):
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


def create_recommendation(offer, user):
    recommendation = Recommendation()
    recommendation.offer = offer
    recommendation.user = user
    return recommendation


def create_booking_for_thing(url=None, amount=50, quantity=1):
    thing = Thing(from_dict={'url': url})
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.thing = thing
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    return booking


def create_booking_for_event(amount=50, quantity=1):
    event = Event()
    offer = Offer()
    stock = Stock()
    booking = Booking(from_dict={'amount': amount})
    offer.event = event
    stock.offer = offer
    booking.stock = stock
    booking.quantity = quantity
    return booking


def create_event_occurrence(offer, beginning_datetime, end_datetime):
    event_occurrence = EventOccurrence()
    event_occurrence.offer = offer
    event_occurrence.beginningDatetime = beginning_datetime
    event_occurrence.endDatetime = end_datetime
    return event_occurrence
