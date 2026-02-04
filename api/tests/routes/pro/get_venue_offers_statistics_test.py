from unittest.mock import patch

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.core import testing
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.pro import offerers as routes


pytestmark = pytest.mark.usefixtures("db_session")


def build_mocked_venue_stats(offers):
    return offerers_api.VenueOffersStatisticsModel(
        monthly_views=[
            offerers_api.MonthlyViewsModel(month=1, views=128),
            offerers_api.MonthlyViewsModel(month=2, views=256),
        ],
        total_views_last_30_days=512,
        top_offers=[
            offerers_api.OfferViewsModel(offer_id=offer.id, views=offer.id * 2, rank=offer.id % len(offers))
            for offer in offers
        ],
    )


def assert_monthly_views_equal(json_data, mocked_stats):
    found_monthly_views = json_data["monthlyViews"]
    found_monthly_views = {(row["month"], row["views"]) for row in found_monthly_views}

    expected_monthly_views = mocked_stats.monthly_views
    expected_monthly_views = {(row.month, row.views) for row in expected_monthly_views}

    assert found_monthly_views == expected_monthly_views


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
    @patch("pcapi.routes.pro.offerers.get_offers_with_headlines_and_mediations")
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
        assert_monthly_views_equal(response.json["jsonData"], mocked_stats)
        assert_top_offers_equal(response.json["jsonData"], mocked_stats)

    @patch("pcapi.core.offerers.api.get_venue_offers_statistics")
    def test_venue_without_any_stats_is_ok(self, mock_venue_stats, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        mock_venue_stats.return_value = offerers_api.VenueOffersStatisticsModel(
            monthly_views=[],
            total_views_last_30_days=0,
            top_offers=[],
        )

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{venue.id}/offers-statistics")
        assert response.status_code == 200

        assert response.json["venueId"] == venue.id
        assert response.json["jsonData"]["totalViewsLast30Days"] == 0
        assert not response.json["jsonData"]["monthlyViews"]
        assert not response.json["jsonData"]["topOffers"]

    def test_cannot_view_venue_stats_if_account_is_not_supposed_to(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        another_venue = offerers_factories.VenueFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{another_venue.id}/offers-statistics")
        assert response.status_code == 403

    def test_cannot_view_venue_stats_if_venue_does_not_exist(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        client = client.with_session_auth(user_offerer.user.email)
        response = client.get("/venues/1/offers-statistics")
        assert response.status_code == 404


class GetOffersWithHeadlinesAndMediationsTest:
    def test_get_no_offers_if_empty_list_of_ids(self):
        assert not routes.get_offers_with_headlines_and_mediations([])

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
            res = routes.get_offers_with_headlines_and_mediations(offer_ids)
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


class Return200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select Venue
    num_queries += 1  # check user_offerer exists
    num_queries += 1  # count active offers
    num_queries += 1  # count active collective_offers
    num_queries += 1  # count pending offers
    num_queries += 1  # count collective_offers

    def test_get_offers_stats(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # 1 bookable public offers
        offers_factories.StockFactory(offer__venue=venue, offer__validation=OfferValidationStatus.APPROVED)

        # 1 published collective offers + 1 published collective offer template = 2 published collective offers
        educational_factories.create_collective_offer_by_status(CollectiveOfferDisplayedStatus.PUBLISHED, venue=venue)
        educational_factories.create_collective_offer_template_by_status(
            CollectiveOfferDisplayedStatus.PUBLISHED, venue=venue
        )

        # 1 pending public offers
        offers_factories.OfferFactory.create_batch(3, venue=venue, validation=OfferValidationStatus.PENDING)

        # 1 pending collective offers + 1 pending collective offer template = 2 pending collective offers
        educational_factories.create_collective_offer_by_status(
            CollectiveOfferDisplayedStatus.UNDER_REVIEW, venue=venue
        )
        educational_factories.create_collective_offer_template_by_status(
            CollectiveOfferDisplayedStatus.UNDER_REVIEW, venue=venue
        )

        client = client.with_session_auth(user_offerer.user.email)

        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/venue/{venue.id}/offers-statistics")
            assert response.status_code == 200

        assert response.json == {
            "publishedPublicOffers": 1,
            "publishedEducationalOffers": 2,
            "pendingPublicOffers": 3,
            "pendingEducationalOffers": 2,
        }


class Return400Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer exists
    num_queries += 2  # rollback transactions

    def test_getoffers_stats_returns_403_if_user_has_no_rights_on_venue(self, client):
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(pro_user.email)

        with testing.assert_num_queries(self.num_queries + 2):  # +2 for the authorization check
            response = client.get(f"/venue/{venue.id}/offers-statistics")
            assert response.status_code == 403

        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }

    def test_get_offers_stats_returns_404_if_venue_is_not_found(self, client):
        pro_user = users_factories.ProFactory(roles=[users_models.UserRole.PRO])

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/venue/888/offers-statistics")

        assert response.status_code == 404
