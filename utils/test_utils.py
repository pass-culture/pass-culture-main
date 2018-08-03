import json
import random
import string
from datetime import datetime, timedelta, timezone
from os import path
from pathlib import Path
from unittest.mock import MagicMock

import requests as req

from models import Thing, Deposit
from models.booking import Booking
from models.event import Event
from models.event_occurrence import EventOccurrence
from models.offer import Offer
from models.stock import Stock
from models.offerer import Offerer
from models.user import User
from models.venue import Venue

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
    r = req.Session()
    if email is None:
        r.auth = ('pctest.admin@btmx.fr', 'pctestadmin')
    elif password is not None:
        r.auth = (email, password)
    else:
        json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

        with open(json_path) as json_file:
            for user_json in json.load(json_file):
                print('user_json', user_json)
                if email == user_json['email']:
                    r.auth = (user_json['email'], user_json['password'])
                    break
                raise ValueError("Utilisateur inconnu: " + email)
    return r


def create_booking_for_booking_email_test(user, stock, is_cancellation=False):
    booking = Booking()
    booking.stock = stock
    booking.user = user
    booking.token = '56789'
    if not is_cancellation:
        stock.bookings = [booking]
    return booking


def create_user_for_booking_email_test():
    user = User()
    user.publicName = 'Test'
    user.email = 'test@email.com'
    return user


def create_stock_with_event_offer(price=10, beginning_datetime_future=True):
    stock = Stock()
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
    stock.eventOccurrence.offer.venue = _create_venue_for_booking_email_test()
    stock.isActive = True
    return stock


def create_stock_with_thing_offer(price=10):
    stock = Stock()
    stock.price = price
    stock.offer = create_thing_offer()
    stock.offer.venue = _create_venue_for_booking_email_test()
    stock.isActive = True
    return stock

def create_stock_with_thing_offer(price=10):
    stock = Stock()
    stock.price = price
    stock.offer = create_thing_offer()
    stock.offer.venue = _create_venue_for_booking_email_test()
    stock.isActive = True
    return stock


def create_thing_offer():
    offer = Offer()
    offer.thing = Thing()
    offer.thing.type = 'Book'
    offer.thing.name = 'Test Book'
    offer.thing.mediaUrls = 'test/urls'
    offer.thing.idAtProviders = ''.join(random.choices(string.digits, k=13))
    offer.thing.extraData = {'author': 'Test Author'}
    return offer


def create_offerer():
    offerer = Offerer()
    offerer.isActive = True
    offerer.address = '123 rue test'
    offerer.postalCode = '93000'
    offerer.city = 'Test city'
    offerer.name = 'Test offerer'
    return offerer


def _create_venue_for_booking_email_test():
    venue = Venue()
    venue.bookingEmail = 'reservations@test.fr'
    venue.address = '123 rue test'
    venue.postalCode = '93000'
    venue.city = 'Test city'
    venue.name = 'Test offerer'
    venue.departementCode = '93'
    venue.managingOfferer = create_offerer()
    return venue


def create_deposit(user, amount=50):
    deposit = Deposit()
    deposit.user = user
    deposit.source = "Test money"
    deposit.amount = amount
    return deposit


def get_mocked_response_status_200():
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response

def get_mocked_response_status_400():
    response = MagicMock(status_code=400, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response
