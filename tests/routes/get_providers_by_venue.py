from repository import repository
import pytest
from tests.conftest import TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_allocine_pivot
from tests.model_creators.provider_creators import activate_provider
from utils.human_ids import humanize


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_venue_has_known_allocine_id(self, app):
            # Given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            allocine_pivot = create_allocine_pivot(siret='12345678912345', theater_id='XXXXXXXXXXXXXXXXXX==')
            repository.save(user, venue, allocine_pivot)

            titelive_stocks = activate_provider('TiteLiveStocks')
            allocine_stocks = activate_provider('AllocineStocks')

            # When
            response = TestClient(app.test_client()).with_auth(email='user@test.com') \
                .get(f'/providers/{humanize(venue.id)}')

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == [
                {
                    'enabledForPro': True,
                    'id': humanize(allocine_stocks.id),
                    'isActive': True,
                    'localClass': 'AllocineStocks',
                    'modelName': 'Provider',
                    'name': 'Allociné',
                    'requireProviderIdentifier': True
                },
                {
                    'enabledForPro': True,
                    'id': humanize(titelive_stocks.id),
                    'isActive': True,
                    'localClass': 'TiteLiveStocks',
                    'modelName': 'Provider',
                    'name': 'TiteLive Stocks (Epagine / Place des libraires.com)',
                    'requireProviderIdentifier': True
                }
            ]

        @pytest.mark.usefixtures("db_session")
        def when_venue_has_no_allocine_id(self, app):
            # Given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            repository.save(user, venue)

            titelive_stocks = activate_provider('TiteLiveStocks')
            activate_provider('AllocineStocks')

            # When
            response = TestClient(app.test_client()).with_auth(email='user@test.com') \
                .get(f'/providers/{humanize(venue.id)}')

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == [
                {
                    'enabledForPro': True,
                    'id': humanize(titelive_stocks.id),
                    'isActive': True,
                    'localClass': 'TiteLiveStocks',
                    'modelName': 'Provider',
                    'name': 'TiteLive Stocks (Epagine / Place des libraires.com)',
                    'requireProviderIdentifier': True
                }
            ]

        class Returns404:
            @pytest.mark.usefixtures("db_session")
            def when_venue_does_not_exists(self, app):
                # Given
                user = create_user(email='user@test.com')
                offerer = create_offerer()
                venue = create_venue(offerer)
                allocine_pivot = create_allocine_pivot()
                repository.save(user, venue, allocine_pivot)

                activate_provider('TiteLiveStocks')
                activate_provider('AllocineStocks')

                # When
                response = TestClient(app.test_client()).with_auth(email='user@test.com') \
                    .get('/providers/AZER')

                # Then
                assert response.status_code == 404

        class Returns401:
            @pytest.mark.usefixtures("db_session")
            def when_user_is_not_logged_in(self, app):
                # when
                response = TestClient(app.test_client()).get('/providers/AZER')

                # then
                assert response.status_code == 401
