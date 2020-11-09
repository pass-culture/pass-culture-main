import pytest

from pcapi.model_creators.generic_creators import create_allocine_venue_provider
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.utils.human_ids import humanize
from pcapi.utils.logger import logger

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_listing_all_venues_with_a_valid_venue_id(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = get_provider_by_local_class('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            repository.save(venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.get('/venueProviders?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            assert response.json[0].get('id') == humanize(venue_provider.id)
            assert response.json[0].get('venueId') == humanize(venue.id)

        @pytest.mark.usefixtures("db_session")
        def when_listing_all_allocine_venues_with_a_valid_venue_id(self, app):
            # given
            offerer = create_offerer()
            venue = create_venue(offerer)
            allocine_stocks_provider = get_provider_by_local_class('AllocineStocks')
            allocine_venue_provider = create_allocine_venue_provider(venue, allocine_stocks_provider)
            repository.save(allocine_venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.get('/venueProviders?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            assert response.json[0].get('id') == humanize(allocine_venue_provider.id)
            assert response.json[0].get('venueId') == humanize(venue.id)

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_listing_all_venues_without_venue_id_argument(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = get_provider_by_local_class('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            repository.save(venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.get('/venueProviders')

            # then
            assert response.status_code == 400
