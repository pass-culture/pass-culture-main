from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_patch_publish_offer_unaccessible(self, client):
        stock = offers_factories.StockFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )
        other_stock = offers_factories.StockFactory()

        response = client.with_session_auth("user@example.com").patch(
            "/offers/publish", json={"id": humanize(other_stock.offer.id)}
        )
        assert response.status_code == 403


@patch("pcapi.core.search.async_index_offer_ids")
@pytest.mark.usefixtures("db_session")
class Returns204Test:
    @patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_patch_publish_offer(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mocked_offer_creation_notification_to_admin,
        mock_async_index_offer_ids,
        client,
    ):
        stock = offers_factories.StockFactory(offer__isActive=False, offer__validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )
        response = client.with_session_auth("user@example.com").patch(
            "/offers/publish", json={"id": humanize(stock.offer.id)}
        )
        assert response.status_code == 204
        offer = offers_models.Offer.query.get(stock.offer.id)
        assert offer.isActive == True
        assert offer.validation == OfferValidationStatus.APPROVED
        mock_async_index_offer_ids.assert_called_once()
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer)
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)
