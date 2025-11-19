import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.core import testing
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


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
