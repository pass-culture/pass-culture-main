from freezegun import freeze_time
import pytest

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class OffererStatsTest:
    @freeze_time("2021-01-01")
    def test_get_offerer_stats(self, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offer_1 = offers_factories.OfferFactory(venue__managingOffererId=offerer.id)
        offer_2 = offers_factories.OfferFactory(venue__managingOffererId=offerer.id)
        offer_3 = offers_factories.OfferFactory(venue__managingOffererId=offerer.id)

        offerers_factories.OffererStatsFactory(
            offerer=offerer,
            table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            jsonData={
                "daily_views": [
                    {
                        "eventDate": "2021-01-01",
                        "numberOfViews": 1,
                    },
                    {
                        "eventDate": "2021-01-02",
                        "numberOfViews": 2,
                    },
                    {
                        "eventDate": "2021-01-03",
                        "numberOfViews": 3,
                    },
                ]
            },
        )
        offerers_factories.OffererStatsFactory(
            offerer=offerer,
            table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            jsonData={
                "top_offers": [
                    {
                        "offerId": offer_1.id,
                        "numberOfViews": 1,
                    },
                    {
                        "offerId": offer_2.id,
                        "numberOfViews": 2,
                    },
                    {
                        "offerId": offer_3.id,
                        "numberOfViews": 3,
                    },
                ]
            },
        )

        response = client.with_session_auth(pro_user.email).get(f"/offerers/{offerer.id}/stats")

        assert response.status_code == 200
        assert response.json == {
            "jsonData": {
                "dailyViews": [
                    {"eventDate": "2021-01-01", "numberOfViews": 1},
                    {"eventDate": "2021-01-02", "numberOfViews": 2},
                    {"eventDate": "2021-01-03", "numberOfViews": 3},
                ],
                "topOffers": [
                    {"image": None, "numberOfViews": 1, "offerId": offer_1.id, "offerName": offer_1.name},
                    {"image": None, "numberOfViews": 2, "offerId": offer_2.id, "offerName": offer_2.name},
                    {"image": None, "numberOfViews": 3, "offerId": offer_3.id, "offerName": offer_3.name},
                ],
            },
            "offererId": offerer.id,
            "syncDate": "2021-01-01T00:00:00",
        }
