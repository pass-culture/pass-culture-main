import pytest

from models import PcObject, Venue
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_venue, create_offerer, create_user, create_user_offerer, \
    create_bank_information
from utils.human_ids import humanize, dehumanize


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_user_has_rights_on_managing_offerer(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='L\'encre et la plume')
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user_offerer, venue)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json={'name': 'Ma librairie'})

            # then
            assert response.status_code == 200
            db.session.refresh(venue)
            assert venue.name == 'Ma librairie'
            json = response.json()
            assert json['isValidated'] == True
            assert 'validationToken' not in json
            assert venue.isValidated

    class Returns400:
        @clean_database
        def when_trying_to_patch_siret(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            siret = offerer.siren + '11111'
            venue = create_venue(offerer, siret=siret)
            PcObject.check_and_save(user_offerer, venue)
            venue_data = {
                'siret': offerer.siren + '12345',
            }
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json=venue_data)

            # Then
            assert response.status_code == 400
            assert response.json()['siret'] == ['Vous ne pouvez pas modifier le siret d\'un lieu']

        @clean_database
        def when_editing_is_virtual_and_managing_offerer_already_has_virtual_venue(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue1 = create_venue(offerer, name='Les petits papiers', is_virtual=True, siret=None)
            venue2 = create_venue(offerer, name='L\'encre et la plume', is_virtual=False)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user_offerer, venue1, venue2)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue2.id), json={'isVirtual': True})

            # then
            assert response.status_code == 400
            assert response.json() == {
                'isVirtual': ['Un lieu pour les offres numériques existe déjà pour cette structure']}

        @clean_database
        def when_latitude_out_of_range_and_longitude_wrong_format(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='Les petits papiers', is_virtual=False)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user_offerer, venue)
            auth_request = TestClient().with_auth(email=user.email)
            data = {'latitude': -98.82387, 'longitude': '112°3534'}

            # when
            response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json=data)

            # then
            assert response.status_code == 400
            assert response.json()['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
            assert response.json()['longitude'] == ['Format incorrect']

        @clean_database
        def when_trying_to_edit_managing_offerer(self, app):
            # Given
            offerer = create_offerer(siren='123456789')
            other_offerer = create_offerer(siren='987654321')
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='Les petits papiers', is_virtual=False)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user_offerer, venue, other_offerer)
            auth_request = TestClient().with_auth(email=user.email)

            # When
            response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id),
                                          json={'managingOffererId': humanize(other_offerer.id)})

            # Then
            assert response.status_code == 400
            assert response.json()['managingOffererId'] == ['Vous ne pouvez pas changer la structure d\'un lieu']


class Post:
    class Returns201:
        @clean_database
        def when_user_has_rights_on_managing_offerer_and_has_siret(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user_offerer)
            auth_request = TestClient().with_auth(email=user.email)
            venue_data = {
                'name': 'Ma venue',
                'siret': '30255917810045',
                'address': '75 Rue Charles Fourier, 75013 Paris',
                'postalCode': '75200',
                'bookingEmail': 'toto@btmx.fr',
                'city': 'Paris',
                'managingOffererId': humanize(offerer.id),
                'latitude': 48.82387,
                'longitude': 2.35284
            }

            # when
            response = auth_request.post(API_URL + '/venues/', json=venue_data)

            # then
            assert response.status_code == 201
            id = response.json()['id']

            venue = Venue.query.filter_by(id=dehumanize(id)).one()
            assert venue.name == 'Ma venue'
            assert venue.siret == '30255917810045'
            assert venue.isValidated

        @clean_database
        def when_user_has_rights_on_managing_offerer_does_not_have_siret_and_has_comment(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            PcObject.check_and_save(user_offerer)
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
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.post(API_URL + '/venues/', json=venue_data)

            # Then
            assert response.status_code == 201
            venue = Venue.query.first()
            assert not venue.isValidated
            json = response.json()
            assert json['isValidated'] == False
            assert 'validationToken' not in json

    class Returns400:
        @clean_database
        def when_posting_a_virtual_venue_for_managing_offerer_with_preexisting_virtual_venue(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, name='L\'encre et la plume', is_virtual=True, siret=None)
            PcObject.check_and_save(venue, user_offerer)

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

            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.post(API_URL + '/venues/', json=venue_data)

            # then
            assert response.status_code == 400
            assert response.json() == {
                'isVirtual': ['Un lieu pour les offres numériques existe déjà pour cette structure']}

        @clean_database
        def when_latitude_out_of_range_and_longitude_wrong_format(self, app):
            # given
            offerer = create_offerer(siren='302559178')
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user_offerer)

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

            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.post(API_URL + '/venues/', json=data)

            # then
            assert response.status_code == 400
            assert response.json()['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
            assert response.json()['longitude'] == ['Format incorrect']


class Get:
    class Returns200:
        @clean_database
        def when_user_has_rights_on_managing_offerer(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, name='L\'encre et la plume')
            bank_information = create_bank_information(bic='QSDFGH8Z555', iban='FR7630006000011234567890189', venue=venue)
            PcObject.check_and_save(user_offerer, bank_information)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 200
            response_json = response.json()
            assert response_json['bic'] == 'QSDFGH8Z555'
            assert response_json['iban'] == 'FR7630006000011234567890189'
            assert 'validationToken' not in response_json

    class Returns403:
        @clean_database
        def when_current_user_doesnt_have_rights(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='L\'encre et la plume')
            PcObject.check_and_save(user, venue)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 403
            assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]
