import pytest

from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_recommendation
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


RECOMMENDATION_URL = "/recommendations"


class Patch:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def test_patch_recommendations_returns_is_clicked_true(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
            offer = create_offer_with_thing_product(venue, thumb_count=0)
            mediation = create_mediation(offer, is_active=True)
            recommendation = create_recommendation(offer=offer, user=user, mediation=mediation, is_clicked=False)
            repository.save(recommendation)

            # when
            response = (
                TestClient(app.test_client())
                .with_auth(user.email)
                .patch("/recommendations/%s" % humanize(recommendation.id), json={"isClicked": True})
            )

            # then
            assert response.status_code == 200
            assert response.json["isClicked"] is True
