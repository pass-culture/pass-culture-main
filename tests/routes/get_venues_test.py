import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_user_has_access_to_one_venue(self, app):
            # given
            offerer = create_offerer()
            venue_name = 'Theatre de la maison'
            venue = create_venue(offerer, name=('%s' % venue_name))
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)

            repository.save(user_offerer, venue)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/venues')

            # then
            assert response.status_code == 200
            assert len(response.json) == 1
            expected_venue = {
                'id': humanize(venue.id),
                'name': venue_name,
                'offererName': venue.managingOfferer.name,
                'publicName': None,
                'isVirtual': venue.isVirtual
            }
            assert response.json[0] == expected_venue

        @pytest.mark.usefixtures("db_session")
        def when_connected_user_does_not_return_unrelated_venues(self, app):
            # given
            theater_company = create_offerer(name='Shakespear company', siren='987654321')
            theater_administrator = create_user(email='user.pro@example.net')
            theater_user_offerer = create_user_offerer(theater_administrator, theater_company)
            theater_venue = create_venue(theater_company, name='National Shakespear Theater', siret='98765432112345')

            bookshop_offerer = create_offerer(name='Bookshop', siren='123456789')
            bookshop_user = create_user(email='bookshop.pro@example.net')
            bookshop_user_offerer = create_user_offerer(bookshop_user, bookshop_offerer)
            bookshop_venue = create_venue(bookshop_offerer, name='Contes et légendes', siret='12345678912345')

            repository.save(theater_user_offerer, theater_venue, bookshop_user_offerer, bookshop_venue)

            auth_request = TestClient(app.test_client()).with_auth(email=bookshop_user.email)

            # when
            response = auth_request.get('/venues')

            # then
            assert len(response.json) == 1
            first_returned_venue = response.json[0]
            assert first_returned_venue['name'] == 'Contes et légendes'


        @pytest.mark.usefixtures("db_session")
        def test_filters_by_offerer_id_when_given(self, app):
            # given
            wanted_offerer = create_offerer()
            unwanted_offerer = create_offerer(siren='234565')
            user = create_user(email='user.pro@test.com')
            create_user_offerer(user, wanted_offerer)
            create_user_offerer(user, unwanted_offerer)
            wanted_venue = create_venue(wanted_offerer)
            unwanted_venue = create_venue(unwanted_offerer, siret='54321987654321')
            repository.save(wanted_venue, unwanted_venue)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/venues?offererId=' + humanize(wanted_offerer.id))

            # then
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['id'] == humanize(wanted_venue.id)


    class Returns403:
        @pytest.mark.usefixtures("db_session")
        def when_current_user_doesnt_have_rights(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='L\'encre et la plume')
            repository.save(user, venue)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 403
            assert response.json['global'] == [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
