import pytest

from models import OfferSQLEntity
from repository import repository
from tests.conftest import TestClient

from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue, API_URL
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize


class Patch:
    class Returns204:
        @pytest.mark.usefixtures("db_session")
        def when_activating_existing_offers(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue, idx=1, is_active=False)
            offer2 = create_offer_with_thing_product(venue, idx=2, is_active=False)

            repository.save(offer1, offer2, user, user_offerer)

            json = {
                'offersId': [humanize(offer1.id), humanize(offer2.id)],
            }

            # When
            response = TestClient(app.test_client()).with_auth(user.email).patch(
                f'{API_URL}/offers/activate',
                json=json)

            # Then
            assert response.status_code == 204
            assert OfferSQLEntity.query.get(offer1.id).isActive == True
            assert OfferSQLEntity.query.get(offer2.id).isActive == True
