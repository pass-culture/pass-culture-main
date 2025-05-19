from unittest.mock import patch

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.core import testing
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer exists
    num_queries += 1  # select offerer_address
    num_queries += 1  # count active offers
    num_queries += 1  # count active collective_offers
    num_queries += 1  # count pending offers
    num_queries += 1  # count collective_offers

    def test_get_offerer_stats(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        offer = offers_factories.OfferFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
        )
        offers_factories.StockFactory.create_batch(3, offer=offer)

        collective_offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
        )
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock, status=CollectiveBookingStatus.PENDING
        )

        collective_offer2 = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
        )
        collective_stock2 = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer2)

        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock2, status=CollectiveBookingStatus.CONFIRMED
        )

        collective_offer3 = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
        )
        collective_stock3 = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer3)
        educational_factories.CollectiveBookingFactory(
            collectiveStock=collective_stock3, status=CollectiveBookingStatus.REIMBURSED
        )

        offers_factories.OfferFactory.create_batch(
            3, venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.PENDING
        )
        educational_factories.CollectiveOfferFactory.create_batch(
            2, venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.PENDING
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.PENDING
        )
        educational_factories.CollectiveOfferFactory(
            venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.REJECTED
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id

        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/v2/stats")
            assert response.status_code == 200

        assert response.json == {
            "publishedPublicOffers": 1,
            "publishedEducationalOffers": 1,
            "pendingPublicOffers": 3,
            "pendingEducationalOffers": 3,
        }

    def test_get_offerer_stats_with_no_public_offers(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveOfferFactory.create_batch(
            2, venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
        )
        educational_factories.CollectiveOfferFactory.create_batch(
            2, venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.PENDING
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/v2/stats")
            assert response.status_code == 200

        assert response.json == {
            "publishedPublicOffers": 0,
            "publishedEducationalOffers": 2,
            "pendingPublicOffers": 0,
            "pendingEducationalOffers": 2,
        }

    def test_get_offerer_stats_with_no_collective_offers(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        for _ in range(2):
            offer = offers_factories.OfferFactory(
                venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.APPROVED
            )
            offers_factories.StockFactory(offer=offer)
        offers_factories.OfferFactory.create_batch(
            3, venue__managingOfferer=user_offerer.offerer, validation=OfferValidationStatus.PENDING
        )

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/v2/stats")
            assert response.status_code == 200

        assert response.json == {
            "publishedPublicOffers": 2,
            "publishedEducationalOffers": 0,
            "pendingPublicOffers": 3,
            "pendingEducationalOffers": 0,
        }

    def test_get_offerer_stats_with_no_offers(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/v2/stats")

        assert response.status_code == 200
        assert response.json == {
            "publishedPublicOffers": 0,
            "publishedEducationalOffers": 0,
            "pendingPublicOffers": 0,
            "pendingEducationalOffers": 0,
        }


class TestReturn400:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer exists

    def test_get_offerer_stats_returns_403_if_user_has_no_rights_on_offerer(self, client):
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(pro_user.email)
        offerer_id = user_offerer.offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/v2/stats")
            assert response.status_code == 403

        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }

    @patch("pcapi.utils.rest.check_user_has_access_to_offerer")
    def test_get_offerer_stats_returns_404_if_offerer_is_not_found(self, check_user_has_access_to_offerer, client):
        pro_user = users_factories.ProFactory(roles=[users_models.UserRole.PRO, users_models.UserRole.ADMIN])

        check_user_has_access_to_offerer.return_value = True

        client = client.with_session_auth(pro_user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/offerers/1/v2/stats")

        assert response.status_code == 404
