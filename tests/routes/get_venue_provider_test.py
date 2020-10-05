from repository import repository
from repository.provider_queries import get_provider_by_local_class
import pytest
from tests.conftest import TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_venue_provider
from utils.human_ids import humanize


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_venue_provider_exists(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            titelive_things_provider = get_provider_by_local_class('TiteLiveThings')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            repository.save(venue_provider)

            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            humanized_venue_provider_id = humanize(venue_provider.id)

            # when
            response = auth_request.get('/venueProviders/' + humanized_venue_provider_id)

            # then
            assert response.status_code == 200

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_venue_provider_id_does_not_exist(self, app):
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
            non_existing_venue_provider_id = 'ABCDEF'

            # when
            response = auth_request.get('/venueProviders/' + non_existing_venue_provider_id)

            # then
            assert response.status_code == 404
