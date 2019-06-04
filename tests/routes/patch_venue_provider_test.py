from models import PcObject, Provider
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offerer, create_venue, create_user, create_venue_provider
from utils.human_ids import humanize


class Patch:
    class Returns200:
        @clean_database
        def when_editing_existing_venue_provider(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)
            humanized_venue_provider_id = humanize(venue_provider.id)

            # when
            response = auth_request.patch(API_URL + '/venueProviders/' + humanized_venue_provider_id,
                                          json={'venueIdAtOfferProvider': '12345678'})

            # then
            assert response.status_code == 200
            response_check = auth_request.get(API_URL + '/venueProviders/' + humanized_venue_provider_id)
            assert response_check.status_code == 200
            assert response_check.json()['venueIdAtOfferProvider'] == '12345678'
