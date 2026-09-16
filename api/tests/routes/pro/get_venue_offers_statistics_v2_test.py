import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @patch("pcapi.core.offerers.api.get_venue_offers_statistics_v2")
    def test_statistics_are_computed_for_the_venue(self, mock_venue_stats, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{venue.id}/offers-statistics-v2")
        assert response.status_code == 200

        mock_venue_stats.assert_called_once_with(venue.id)

    @patch("pcapi.core.offerers.api.get_venue_offers_statistics_v2")
    def test_statistics_are_serialized(self, mock_venue_stats, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue, name="Infusions")
        mock_venue_stats.return_value = offerers_api.VenueOffersStatisticsV2Model(
            venue_id=venue.id,
            last_3_months=offerers_api.VenueOffersPeriodStatisticsModel(
                top_offers=[offerers_api.TopOfferModel(offer=offer, views=30, rank=1)],
                cumulated_views=42,
                views_by_month=[
                    offerers_api.MonthlyViewsModel(month=datetime.date(2026, 8, 1), views=12),
                    offerers_api.MonthlyViewsModel(month=datetime.date(2026, 9, 1), views=30),
                ],
            ),
            last_6_months=offerers_api.VenueOffersPeriodStatisticsModel(
                top_offers=[], cumulated_views=0, views_by_month=[]
            ),
        )

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{venue.id}/offers-statistics-v2")
        assert response.status_code == 200

        assert response.json == {
            "venueId": venue.id,
            "last3Months": {
                "topOffers": [
                    {
                        "offerId": offer.id,
                        "name": "Infusions",
                        "views": 30,
                        "isHeadlineOffer": False,
                        "image": None,
                    }
                ],
                "cumulatedViews": 42,
                "viewsByMonth": [
                    {"month": "2026-08-01", "views": 12},
                    {"month": "2026-09-01", "views": 30},
                ],
            },
            "last6Months": {"topOffers": [], "cumulatedViews": 0, "viewsByMonth": []},
        }


class Returns404Test:
    def test_cannot_view_venue_stats_if_user_has_no_access(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        another_venue = offerers_factories.VenueFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{another_venue.id}/offers-statistics-v2")
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_cannot_view_venue_stats_if_venue_does_not_exist(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        client = client.with_session_auth(user_offerer.user.email)
        response = client.get("/venues/1/offers-statistics-v2")
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
