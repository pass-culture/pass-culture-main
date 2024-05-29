import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.models.offer_mixin import OfferValidationStatus


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
            "/offers/publish", json={"id": other_stock.offer.id}
        )
        assert response.status_code == 403


@patch("pcapi.core.search.async_index_offer_ids")
@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @patch("pcapi.core.mails.transactional.send_first_venue_approved_offer_email_to_pro")
    def test_patch_publish_offer(
        self,
        mocked_send_first_venue_approved_offer_email_to_pro,
        mock_async_index_offer_ids,
        client,
    ):
        stock = offers_factories.StockFactory(offer__isActive=False, offer__validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        response = client.patch("/offers/publish", json={"id": stock.offerId})

        assert response.status_code == 200
        content = response.json
        offer = offers_models.Offer.query.filter_by(id=stock.offer.id).one()
        assert offer.validation == OfferValidationStatus.APPROVED
        assert offer.lastValidationPrice == stock.price
        assert content["isActive"] is True
        assert content["isNonFreeOffer"] is True
        mock_async_index_offer_ids.assert_called_once()
        mocked_send_first_venue_approved_offer_email_to_pro.assert_called_once_with(offer)


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_patch_publish_offer(
        self,
        client,
    ):
        offer = offers_factories.OfferFactory(isActive=False, validation=OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        response = client.patch("/offers/publish", json={"id": offer.id})

        assert response.status_code == 400
        assert response.json["offer"] == "Cette offre n’a pas de stock réservable"
        offer = offers_models.Offer.query.filter_by(id=offer.id).one()
        assert offer.validation == OfferValidationStatus.DRAFT

    def test_patch_publish_offer_with_non_bookable_stock(
        self,
        client,
    ):
        stock = offers_factories.StockFactory(
            offer__isActive=False,
            offer__validation=OfferValidationStatus.DRAFT,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=stock.offer.venue.managingOfferer,
        )

        client = client.with_session_auth("user@example.com")
        response = client.patch("/offers/publish", json={"id": stock.offerId})

        assert response.status_code == 400
        assert response.json["offer"] == "Cette offre n’a pas de stock réservable"
        offer = offers_models.Offer.query.filter_by(id=stock.offerId).one()
        assert offer.validation == OfferValidationStatus.DRAFT
