import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers import repository as offers_repository
from pcapi.core.testing import assert_num_queries
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE


pytestmark = pytest.mark.usefixtures("db_session")


def build_mocked_venue_stats(offers):
    return offerers_api.VenueOffersStatisticsModel(
        daily_views=[
            offerers_api.DailyViewsModel(day=datetime.date(2026, 1, 1), views=128),
            offerers_api.DailyViewsModel(day=datetime.date(2026, 1, 2), views=256),
        ],
        total_views_last_30_days=512,
        top_offers=[
            offerers_api.OfferViewsModel(offer_id=offer.id, views=offer.id * 2, rank=offer.id % len(offers))
            for offer in offers
        ],
    )


def assert_daily_views_equal(json_data, mocked_stats):
    found_daily_views = json_data["dailyViews"]
    found_daily_views = {(row["day"], row["views"]) for row in found_daily_views}

    expected_daily_views = mocked_stats.daily_views
    expected_daily_views = {(row.day.isoformat(), row.views) for row in expected_daily_views}

    assert found_daily_views == expected_daily_views


def assert_top_offers_equal(json_data, mocked_stats):
    found_top_offers = json_data["topOffers"]
    found_top_offers = {(o["offerId"], o["numberOfViews"]) for o in found_top_offers}

    expected_top_offers = mocked_stats.top_offers
    expected_top_offers = {(o.offer_id, o.views) for o in expected_top_offers}

    # all fields from json_data are not compared. They are more that
    # comes from the related offer, but it will add to much code for not
    # so much. The goal here is to check that the expected top offers
    # have been serialized.
    assert found_top_offers == expected_top_offers


# Sorry for this one but for some reason we have two routes that computes
# a venue's offers statistics, with almost the same path: one that
# starts with /venues and one that starts with /venue (singular)
# They do compute statistics... but not the same.
# So keep in mind that this class does not test the same route as the
# others below. Yes, it is confusing.
# TODO(jbaudet - 02/2026) - move this class or the others to a more
# appropriate module once this whole two venue statistics routes mess
# has been taken care of.
class GetVenueOfferStatisticsTest:
    @patch("pcapi.core.offers.repository.get_offers_with_headlines_and_mediations")
    @patch("pcapi.core.offerers.api.get_venue_offers_statistics")
    def test_venue_with_some_fake_stats_serializes_them(self, mock_venue_stats, mock_get_offers, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offers = offers_factories.OfferFactory.create_batch(3, venue=venue)

        mocked_stats = build_mocked_venue_stats(offers)
        mock_venue_stats.return_value = mocked_stats
        mock_get_offers.return_value = offers

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{venue.id}/offers-statistics")
        assert response.status_code == 200

        assert response.json["venueId"] == venue.id
        assert response.json["jsonData"]["totalViewsLast30Days"] == mocked_stats.total_views_last_30_days
        assert_daily_views_equal(response.json["jsonData"], mocked_stats)
        assert_top_offers_equal(response.json["jsonData"], mocked_stats)

    @patch("pcapi.core.offerers.api.get_venue_offers_statistics")
    def test_venue_without_any_stats_is_ok(self, mock_venue_stats, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        mock_venue_stats.return_value = offerers_api.VenueOffersStatisticsModel(
            daily_views=[],
            total_views_last_30_days=0,
            top_offers=[],
        )

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{venue.id}/offers-statistics")
        assert response.status_code == 200

        assert response.json["venueId"] == venue.id
        assert response.json["jsonData"]["totalViewsLast30Days"] == 0
        assert not response.json["jsonData"]["dailyViews"]
        assert not response.json["jsonData"]["topOffers"]

    def test_cannot_view_venue_stats_if_account_is_not_supposed_to(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        another_venue = offerers_factories.VenueFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{another_venue.id}/offers-statistics")
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}

    def test_cannot_view_venue_stats_if_venue_does_not_exist(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        client = client.with_session_auth(user_offerer.user.email)
        response = client.get("/venues/1/offers-statistics")
        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}


class GetOffersWithHeadlinesAndMediationsTest:
    def test_get_offers_with_their_mediations_and_headline_offers(self):
        offer_with_mediation_and_headline = offers_factories.OfferFactory()
        # builds both headline offer and mediation
        offers_factories.HeadlineOfferFactory(offer=offer_with_mediation_and_headline)

        product_mediation = offers_factories.ProductMediationFactory()
        offer_with_product_mediation = offers_factories.OfferFactory(product=product_mediation.product)

        offer_with_nothing_more = offers_factories.OfferFactory()

        offers = {offer_with_mediation_and_headline, offer_with_product_mediation, offer_with_nothing_more}
        offer_ids = {o.id for o in offers}

        # fetch offers
        # fetch offers' mediations
        # fetch offers' products' mediations
        # fetch offers' headline offers information
        with assert_num_queries(4):
            res = offers_repository.get_offers_with_headlines_and_mediations(offer_ids)
            assert {o.id for o in res} == offer_ids
            assert len(res) == len(offers)

            for offer in res:
                if offer.id == offer_with_mediation_and_headline.id:
                    assert len(offer.headlineOffers) == 1
                    assert len(offer.mediations) == 1
                elif offer.id == offer_with_product_mediation.id:
                    assert not offer.headlineOffers
                    assert not offer.mediations
                    assert len(offer.product.productMediations) == 1
                    assert offer.product.productMediations[0].id == product_mediation.id
                else:
                    assert not offer.headlineOffers
                    assert not offer.mediations
