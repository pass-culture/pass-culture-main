import datetime

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core import testing
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class OffererStatsTest:
    @time_machine.travel("2021-01-01")
    def test_get_offerer_stats(self, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        product = offers_factories.ProductFactory()
        product_mediation = offers_factories.ProductMediationFactory(product=product, uuid="my_id")
        offer_1 = offers_factories.OfferFactory(venue__managingOffererId=offerer.id, product=product)
        offer_2 = offers_factories.OfferFactory(venue__managingOffererId=offerer.id)
        mediation = offers_factories.MediationFactory(offer=offer_2)
        offer_3 = offers_factories.OfferFactory(venue__managingOffererId=offerer.id)
        offers_factories.HeadlineOfferFactory(
            offer=offer_2, venue=offer_2.venue, timespan=(datetime.datetime.utcnow(),), without_mediation=True
        )

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
                "total_views_last_30_days": 6,
                "top_offers": [
                    {
                        "offerId": offer_1.id,
                        "numberOfViews": 3,
                    },
                    {
                        "offerId": offer_2.id,
                        "numberOfViews": 1,
                    },
                    {
                        "offerId": offer_3.id,
                        "numberOfViews": 2,
                    },
                ],
            },
        )
        offerer_id = offerer.id
        client = client.with_session_auth(pro_user.email)
        queries = testing.AUTHENTICATION_QUERIES
        queries += 1  # check user_offerer exists
        queries += 1  # select offerer_stats
        queries += 1  # select offers with images, join on headline offer & stocks
        queries += 1  # FF WIP_REFACTO_FUTURE_OFFER
        with testing.assert_num_queries(queries):
            response = client.get(f"/offerers/{offerer_id}/stats")
            assert response.status_code == 200

        assert response.json == {
            "jsonData": {
                "dailyViews": [
                    {"eventDate": "2021-01-01", "numberOfViews": 1},
                    {"eventDate": "2021-01-02", "numberOfViews": 2},
                    {"eventDate": "2021-01-03", "numberOfViews": 3},
                ],
                "topOffers": [
                    {
                        "image": {
                            "credit": None,
                            "url": product_mediation.url,
                        },
                        "isHeadlineOffer": False,
                        "numberOfViews": 3,
                        "offerId": offer_1.id,
                        "offerName": offer_1.name,
                    },
                    {
                        "image": None,
                        "isHeadlineOffer": False,
                        "numberOfViews": 2,
                        "offerId": offer_3.id,
                        "offerName": offer_3.name,
                    },
                    {
                        "image": {
                            "credit": None,
                            "url": f"http://localhost/storage/thumbs/mediations/{humanize(mediation.id)}",
                        },
                        "isHeadlineOffer": True,
                        "numberOfViews": 1,
                        "offerId": offer_2.id,
                        "offerName": offer_2.name,
                    },
                ],
                "totalViewsLast30Days": 6,
            },
            "offererId": offerer.id,
            "syncDate": "2021-01-01T00:00:00",
        }

    @time_machine.travel("2021-01-01")
    def test_get_offerer_stats_if_no_top_offers(self, client):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

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

        offerer_id = offerer.id
        client = client.with_session_auth(pro_user.email)
        queries = testing.AUTHENTICATION_QUERIES
        queries += 1  # check user_offerer exists
        queries += 1  # select offerer_stats
        with testing.assert_num_queries(queries):
            response = client.get(f"/offerers/{offerer_id}/stats")

        assert response.status_code == 200
        assert response.json == {
            "jsonData": {
                "dailyViews": [
                    {"eventDate": "2021-01-01", "numberOfViews": 1},
                    {"eventDate": "2021-01-02", "numberOfViews": 2},
                    {"eventDate": "2021-01-03", "numberOfViews": 3},
                ],
                "topOffers": [],
                "totalViewsLast30Days": 0,
            },
            "offererId": offerer.id,
            "syncDate": "2021-01-01T00:00:00",
        }
