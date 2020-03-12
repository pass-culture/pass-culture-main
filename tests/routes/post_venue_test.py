from unittest.mock import patch

from models import Venue
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from utils.human_ids import humanize, dehumanize


class Post:
    class Returns201:
        @clean_database
        def when_user_has_rights_on_managing_offerer_and_has_siret(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            venue_data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@btmx.fr',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': 48.82387,
                'longitude': 2.35284,
                'publicName': 'Ma venue publique'
            }

            # when
            response = auth_request.post('/venues', json=venue_data)

            # then
            assert response.status_code == 201
            id = response.json['id']

            venue = Venue.query.filter_by(id=dehumanize(id)).one()
            assert venue.name == 'Ma venue'
            assert venue.publicName == 'Ma venue publique'
            assert venue.siret == '30255917810045'
            assert venue.isValidated

        @clean_database
        def when_user_has_rights_on_managing_offerer_does_not_have_siret_and_has_comment(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            repository.save(user_offerer)
            venue_data = {
                'name': 'Ma venue',
                'comment': 'Je ne mets pas de SIRET pour une bonne raison',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@btmx.fr',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': 48.82387,
                'longitude': 2.35284
            }
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post('/venues', json=venue_data)

            # Then
            assert response.status_code == 201
            venue = Venue.query.first()
            assert not venue.isValidated
            json = response.json
            assert json['isValidated'] == False
            assert 'validationToken' not in json

        @clean_database
        @patch('routes.venues.link_venue_to_iris_if_valid')
        def when_offerer_is_validated_and_venue_with_siret_add_to_iris_venue(self, mock_link_venue_to_iris_if_valid,
                                                                             app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            venue_data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@btmx.fr',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': 48.82387,
                'longitude': 2.35284,
                'publicName': 'Ma venue publique'
            }

            # when
            response = auth_request.post('/venues', json=venue_data)
            id = response.json['id']
            venue = Venue.query.filter_by(id=dehumanize(id)).one()

            # then
            mock_link_venue_to_iris_if_valid.assert_called_once_with(venue)

    class Returns400:
        @clean_database
        def when_posting_a_virtual_venue_for_managing_offerer_with_preexisting_virtual_venue(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, name='L\'encre et la plume', is_virtual=True, siret=None)
            repository.save(venue, user_offerer)

            venue_data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@btmx.fr',
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
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer)

            data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@btmx.fr',
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
