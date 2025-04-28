import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_delete_price_category(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        price_category = offers_factories.PriceCategoryFactory(offer=offer)
        offers_factories.StockFactory(offer=offer, priceCategory=price_category)

        offerer = offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        response = client.with_session_auth(offerer.user.email).delete(
            f"/offers/{offer.id}/price_categories/{price_category.id}"
        )

        assert response.status_code == 204
        assert db.session.query(offers_models.PriceCategory).count() == 0
        assert db.session.query(offers_models.Stock).count() == 0


class Return400Test:
    def test_offer_not_draft(self, client):
        validated_offer = offers_factories.ThingOfferFactory()
        undeletable_price_category = offers_factories.PriceCategoryFactory(offer=validated_offer)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=validated_offer.venue.managingOfferer,
        )

        response = client.with_session_auth("user@example.com").delete(
            f"/offers/{validated_offer.id}/price_categories/{undeletable_price_category.id}"
        )

        assert response.status_code == 400
        assert db.session.query(offers_models.PriceCategory).count() == 1

    def test_user_unrelated_to_offer(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        price_category = offers_factories.PriceCategoryFactory(offer=offer)
        unrelated_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")

        response = client.with_session_auth(unrelated_offerer.user.email).delete(
            f"/offers/{offer.id}/price_categories/{price_category.id}"
        )

        assert response.status_code == 403
        assert db.session.query(offers_models.PriceCategory).count() == 1
