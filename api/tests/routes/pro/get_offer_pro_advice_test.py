import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
import pcapi.utils.date as date_utils
from pcapi.core import testing


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_offer_pro_advice(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        updated_at = date_utils.get_naive_utc_now()
        offers_factories.ProAdviceFactory(
            offer=offer, content="Une super recommendation.", author="Le libraire du coin", updatedAt=updated_at
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offer + pro_advice
        num_queries += 1  # check user has rights on offerer
        with testing.assert_num_queries(num_queries):
            response = auth_client.get(f"/offers/{offer_id}/pro_advice")
            assert response.status_code == 200

        assert response.json == {
            "proAdvice": {
                "content": "Une super recommendation.",
                "author": "Le libraire du coin",
                "updatedAt": date_utils.format_into_utc_date(updated_at),
            }
        }

    def test_offer_has_no_pro_advice(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        response = auth_client.get(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 200
        assert response.json == {"proAdvice": None}


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_unauthenticated(self, client):
        offer = offers_factories.OfferFactory()

        response = client.get(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 401


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_offer_not_found(self, client):
        pro_user = users_factories.ProFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        response = auth_client.get("/offers/99999999/pro_advice")

        assert response.status_code == 404

    def test_unauthorized_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.OfferFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        response = auth_client.get(f"/offers/{offer.id}/pro_advice")

        assert response.status_code == 404
