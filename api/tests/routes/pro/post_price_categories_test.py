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
        assert price_category.label == "Behind a post"

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

    def test_edit_one_price_category(self, client):
        offer = offers_factories.OfferFactory()
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "priceCategories": [
                {"price": 200.54, "label": "Behind a post", "id": price_category.id},
            ],
        }

        client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)
        price_category = offers_models.PriceCategory.query.one()
        assert price_category.price == decimal.Decimal("200.54")
        assert price_category.label == "Behind a post"

    def test_edit_part_of_price_category(self, client):
        offer = offers_factories.OfferFactory()
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Do not change", venue=offer.venue),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "priceCategories": [
                {"price": 200, "id": price_category.id},
            ],
        }

        client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)
        price_category = offers_models.PriceCategory.query.one()
        assert price_category.price == decimal.Decimal("200")
        assert price_category.label == "Do not change"

    def test_update_part_of_price_category(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Already exists", venue=offer.venue),
        )
        data = {
            "priceCategories": [
                {"price": 25.12, "id": price_category.id},
            ],
        }
        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)

        assert response.status_code == 200
        price_category = offers_models.PriceCategory.query.one()
        assert price_category.price == decimal.Decimal("25.12")
        assert offers_models.PriceCategoryLabel.query.count() == 1

    def test_create_and_update_multiple_price_categories(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Already exists", venue=offer.venue),
        )

        data = {
            "priceCategories": [
                {"price": 20, "label": "Already exists"},  # Create
                {"price": 25, "label": "Does not exists"},  # Create
                {"price": 25, "label": "Five people", "id": price_category.id},  # Edit
            ],
        }

        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)

        assert response.status_code == 200
        assert offers_models.PriceCategory.query.count() == 3
        assert offers_models.PriceCategoryLabel.query.count() == 3


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

    def test_update_price_category_not_found(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Do not change", venue=offer.venue),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "priceCategories": [
                {"price": 350, "label": "Behind a post", "id": price_category.id + 1},
            ],
        }

        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)

        assert response.status_code == 400
        assert response.json == {
            "price_category_id": [f"La catégorie de prix avec l'id {price_category.id + 1} n'existe pas"]
        }

    def test_update_unreachable_price_category(self, client):
        offer = offers_factories.ThingOfferFactory(isActive=False, validation=offers_models.OfferValidationStatus.DRAFT)
        offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Do not change", venue=offer.venue),
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        unreachable_offer = offers_factories.ThingOfferFactory(
            isActive=False, validation=offers_models.OfferValidationStatus.DRAFT
        )
        unreachable_price_category = offers_factories.PriceCategoryFactory(
            offer=unreachable_offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Do not change"),
        )
        offerers_factories.UserOffererFactory(
            user__email="unreachable@example.com",
            offerer=unreachable_offer.venue.managingOfferer,
        )

        data = {
            "priceCategories": [
                {"price": 350, "label": "Behind a post", "id": unreachable_price_category.id},
            ],
        }
        response = client.with_session_auth("user@example.com").post(f"/offers/{offer.id}/price_categories", json=data)
        assert response.status_code == 400
        assert response.json == {
            "price_category_id": [f"La catégorie de prix avec l'id {unreachable_price_category.id} n'existe pas"]
        }
