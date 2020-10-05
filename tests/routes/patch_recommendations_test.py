from repository import repository
import pytest
from tests.conftest import TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_recommendation, \
    create_mediation
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize

RECOMMENDATION_URL = '/recommendations'


class Patch:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def test_patch_recommendations_returns_is_clicked_true(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='29100', siret='12345678912341')
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            repository.save(recommendation)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .patch('/recommendations/%s' % humanize(recommendation.id), json={'isClicked': True})

            # then
            assert response.status_code == 200
            assert response.json['isClicked'] is True
