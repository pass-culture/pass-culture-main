import decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_create_one_price_category(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {"priceCategories": [{"price": 20.34, "label": "Behind a post"}]}

        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)
        assert response.status_code == 200
        price_category = offers_models.PriceCategory.query.one()
        assert price_category.offerId == offer.id
        assert price_category.price == decimal.Decimal("20.34")
        assert price_category.priceCategoryLabel.label == "Behind a post"

    def test_create_multiple_price_categories(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "priceCategories": [
                {"price": 20, "label": "Behind a post"},
                {"price": 12.3, "label": "On your friend knees"},
                {"price": 28.71, "label": "The throne"},
            ],
        }

        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)

        assert response.status_code == 200
        assert offers_models.PriceCategory.query.count() == 3

    def test_does_not_duplicate_price_categories_label_when_label_exists(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Already exists", venue=offer.venue),
        )

        data = {
            "priceCategories": [
                {"price": 20, "label": "Already exists"},
            ],
        }

        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)

        assert response.status_code == 200
        assert offers_models.PriceCategory.query.count() == 2
        assert offers_models.PriceCategoryLabel.query.count() == 1


class Returns400Test:
    def test_create_too_expensive_price_category(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "priceCategories": [
                {"price": 350, "label": "Behind a post"},
            ],
        }

        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)

        assert response.status_code == 400
        assert offers_models.PriceCategory.query.count() == 0
        assert response.json == {"price300": ["Le prix d’une offre ne peut excéder 300 euros."]}
