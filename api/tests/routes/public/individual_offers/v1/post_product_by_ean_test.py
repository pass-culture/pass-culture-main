import datetime
import decimal
from unittest import mock

import freezegun
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from . import utils


@pytest.mark.usefixtures("db_session")
class PostProductByEanTest:
    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_valid_ean_with_stock(self, client):
        venue_data = {
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": False,
        }
        venue, _ = utils.create_offerer_provider_linked_to_venue(venue_data)
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id, extraData={"ean": "1234567890123"}
        )
        unknown_ean = "1234567897123"

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "products": [
                    {
                        "ean": product.extraData["ean"],
                        "stock": {
                            "bookingLimitDatetime": "2022-01-01T16:00:00+04:00",
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                    {
                        "ean": unknown_ean,
                        "stock": {
                            "bookingLimitDatetime": "2022-01-01T16:00:00+04:00",
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                ],
            },
        )

        assert response.status_code == 204

        created_offer = offers_models.Offer.query.one()
        assert created_offer.bookingEmail == venue.bookingEmail
        assert created_offer.description == product.description
        assert created_offer.extraData == product.extraData
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.name == product.name
        assert created_offer.product == product
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == product.subcategoryId
        assert created_offer.withdrawalDetails == venue.withdrawalDetails
        assert created_offer.audioDisabilityCompliant == venue.audioDisabilityCompliant
        assert created_offer.mentalDisabilityCompliant == venue.mentalDisabilityCompliant
        assert created_offer.motorDisabilityCompliant == venue.motorDisabilityCompliant
        assert created_offer.visualDisabilityCompliant == venue.visualDisabilityCompliant

        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer
        assert created_stock.bookingLimitDatetime == datetime.datetime(2022, 1, 1, 12, 0, 0)

    @mock.patch("pcapi.tasks.sendinblue_tasks.update_sib_pro_attributes_task")
    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_valid_ean_without_task_autoflush(self, update_sib_pro_task_mock, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id, extraData={"ean": "1234567890123"}
        )
        finance_factories.CustomReimbursementRuleFactory(offerer=api_key.offerer, rate=0.2, offer=None)

        # the update task autoflushes the SQLAlchemy session, but is not executed synchronously in cloud
        # environments, therefore we cannot rely on its side effects
        update_sib_pro_task_mock.side_effect = None

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": product.extraData["ean"],
                        "stock": {
                            "bookingLimitDatetime": "2022-01-01T16:00:00+04:00",
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )

        assert response.status_code == 204

        assert offers_models.Offer.query.count() == 1
        assert offers_models.Stock.query.count() == 1

    def test_does_not_create_non_synchronisable_or_specific_to_an_offerer_product(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product = offers_factories.ProductFactory(extraData={"ean": "1234567890123"}, isGcuCompatible=False)
        # Theis product should not exists in our database (but they do). They are not synchronisable and are specific to an offerer.
        # They are created at the same time as an offer.
        product = offers_factories.ProductFactory(
            extraData={"ean": "1234567890123"}, isGcuCompatible=False, owningOfferer=venue.managingOfferer
        )

        client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": product.extraData["ean"],
                        "stock": {
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )
        assert offers_models.Offer.query.all() == []

    def test_400_when_ean_wrong_format(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product = offers_factories.ProductFactory(extraData={"ean": "123456789"})

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": product.extraData["ean"],
                        "stock": {
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )

        assert response.status_code == 400
        assert response.json == {"products.0.ean": ["ensure this value has at least 13 characters"]}

    def test_update_offer_when_ean_already_exists(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id, extraData={"ean": "1234567890123"}
        )

        client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": product.extraData["ean"],
                        "stock": {
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )
        client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": product.extraData["ean"],
                        "stock": {
                            "price": 7890,
                            "quantity": 3,
                        },
                    }
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )

        assert offers_models.Offer.query.one()
        created_stock = offers_models.Stock.query.one()
        assert created_stock.price == decimal.Decimal("78.90")
        assert created_stock.quantity == 3

    def test_create_and_update_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        ean_to_update = "1234567890123"
        ean_to_create = "1234567897123"
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id, extraData={"ean": ean_to_update}
        )
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id, extraData={"ean": ean_to_create}
        )

        client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": ean_to_update,
                        "stock": {
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )

        client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/products/ean",
            json={
                "products": [
                    {
                        "ean": ean_to_update,
                        "stock": {
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                    {
                        "ean": ean_to_create,
                        "stock": {
                            "price": 9876,
                            "quantity": 22,
                        },
                    },
                ],
                "location": {"type": "physical", "venueId": venue.id},
            },
        )

        [updated_offer, created_offer] = offers_models.Offer.query.order_by(offers_models.Offer.id).all()
        assert updated_offer.extraData["ean"] == ean_to_update
        assert updated_offer.activeStocks[0].price == decimal.Decimal("12.34")
        assert updated_offer.activeStocks[0].quantity == 3

        assert created_offer.extraData["ean"] == ean_to_create
        assert created_offer.activeStocks[0].price == decimal.Decimal("98.76")
        assert created_offer.activeStocks[0].quantity == 22
