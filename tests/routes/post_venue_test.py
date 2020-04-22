from unittest.mock import patch

from models import Venue
from repository import repository
from tests.conftest import TestClient, clean_database
from tests.model_creators.generic_creators import create_offerer, create_user, \
    create_user_offerer, create_venue, create_venue_type
from utils.human_ids import dehumanize, humanize


class Post:
    class Returns201:
        @clean_database
        def test_should_register_new_venue(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
            venue_type = create_venue_type(label='Musée')
            repository.save(user_offerer, venue_type)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            venue_data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@example.com',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': 48.82387,
                'longitude': 2.35284,
                'publicName': 'Ma venue publique',
                'venueTypeId': humanize(venue_type.id),
            }

            # when
            response = auth_request.post('/venues', json=venue_data)

            # then
            assert response.status_code == 201
            idx = response.json['id']

            venue = Venue.query.filter_by(id=dehumanize(idx)).one()
            assert venue.name == 'Ma venue'
            assert venue.publicName == 'Ma venue publique'
            assert venue.siret == '30255917810045'
            assert venue.isValidated
            assert venue.venueTypeId == venue_type.id

    class Returns400:
        @clean_database
        def when_posting_a_virtual_venue_for_managing_offerer_with_preexisting_virtual_venue(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, name='L\'encre et la plume', is_virtual=True, siret=None)
            repository.save(venue, user_offerer)

            venue_data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@example.com',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': 48.82387,
                'longitude': 2.35284,
                'isVirtual': True
            }

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post('/venues', json=venue_data)

            # then
            assert response.status_code == 400
            assert response.json == {
                'isVirtual': ['Un lieu pour les offres numériques existe déjà pour cette structure']}

        @clean_database
        def when_latitude_out_of_range_and_longitude_wrong_format(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer)

            data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@example.com',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': -98.82387,
                'longitude': '112°3534',
                'isVirtual': False
            }

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post('/venues', json=data)

            # then
            assert response.status_code == 400
            assert response.json['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
            assert response.json['longitude'] == ['Format incorrect']
