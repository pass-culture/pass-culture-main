import datetime
import decimal
import logging
from unittest import mock

import pytest
import time_machine

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.utils import date as date_utils

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PostProductByEanTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products/ean"
    endpoint_method = "post"

    @staticmethod
    def _get_base_product(ean: str | None = None) -> tuple[str, offers_models.Product]:
        ean = ean or "1234567890123"
        product_provider = providers_factories.ProviderFactory()
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean=ean,
            lastProviderId=product_provider.id,
        )

        return ean, product

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "products": [
                    {
                        "ean": "1234567890123",
                        "stock": {
                            "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
            },
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        venue = venue_provider.venue

        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "products": [
                    {
                        "ean": "1234567890123",
                        "stock": {
                            "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
            },
        )
        assert response.status_code == 404

    @time_machine.travel(datetime.datetime(2025, 7, 15), tick=False)
    def test_valid_ean_with_stock(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue

        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="1234567890123",
            lastProviderId=venue_provider.provider.id,
        )
        unknown_ean = "1234567897123"

        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue.id},
                "products": [
                    {
                        "ean": product.ean,
                        "stock": {
                            "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                    {
                        "ean": unknown_ean,
                        "stock": {
                            "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                ],
            },
        )

        assert response.status_code == 204

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.bookingEmail == venue.bookingEmail
        assert created_offer._description is None
        assert created_offer.description == product.description
        assert created_offer.ean == product.ean
        assert created_offer.extraData == product.extraData
        assert created_offer.lastProvider.name == venue_provider.provider.name
        assert created_offer.name == product.name
        assert created_offer.product == product
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == product.subcategoryId
        assert created_offer.withdrawalDetails == venue.withdrawalDetails
        assert created_offer.audioDisabilityCompliant == venue.audioDisabilityCompliant
        assert created_offer.mentalDisabilityCompliant == venue.mentalDisabilityCompliant
        assert created_offer.motorDisabilityCompliant == venue.motorDisabilityCompliant
        assert created_offer.visualDisabilityCompliant == venue.visualDisabilityCompliant
        assert created_offer.offererAddressId == venue.offererAddressId
        assert created_offer.publicationDatetime == datetime.datetime(2025, 7, 15)
        assert created_offer.bookingAllowedDatetime == None

        created_stock = db.session.query(offers_models.Stock).one()
        assert created_stock.price == decimal.Decimal("12.34")
        assert created_stock.quantity == 3
        assert created_stock.offer == created_offer
        assert created_stock.bookingLimitDatetime == in_ten_minutes

    @time_machine.travel(datetime.datetime(2025, 7, 15), tick=False)
    @pytest.mark.parametrize(
        "input_product_stock_dict,expected_publication_datetime",
        [
            (  # no `publicationDatetime` should default to "now"
                {"ean": "1234567890123", "stock": {"price": 1234, "quantity": 3}},
                datetime.datetime(2025, 7, 15),
            ),
            (  # `publicationDatetime="now"`
                {"ean": "1234567890123", "publicationDatetime": "now", "stock": {"price": 1234, "quantity": 3}},
                datetime.datetime(2025, 7, 15),
            ),
            (  # `publicationDatetime` in the future
                {
                    "ean": "1234567890123",
                    "publicationDatetime": date_utils.utc_datetime_to_department_timezone(
                        datetime.datetime(2025, 7, 17, 10), "75"
                    ).isoformat(),
                    "stock": {"price": 1234, "quantity": 3},
                },
                datetime.datetime(2025, 7, 17, 10),
            ),
            (  # unset `publicationDatetime`
                {"ean": "2461567890123", "publicationDatetime": None, "stock": {"price": 1234, "quantity": 3}},
                None,
            ),
        ],
    )
    def test_publication_datetime_behavior(self, input_product_stock_dict, expected_publication_datetime, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue

        offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="1234567890123",
            lastProviderId=venue_provider.provider.id,
        )
        product_with_existing_offer = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="2461567890123",
            lastProviderId=venue_provider.provider.id,
        )
        offers_factories.ThingOfferFactory(
            product=product_with_existing_offer,
            ean=product_with_existing_offer.ean,
            venue=venue,
            lastProvider=venue_provider.provider,
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={"location": {"type": "physical", "venueId": venue.id}, "products": [input_product_stock_dict]},
        )

        assert response.status_code == 204

        offer_1 = db.session.query(offers_models.Offer).filter_by(ean=input_product_stock_dict["ean"]).one()
        assert offer_1.publicationDatetime == expected_publication_datetime

    @time_machine.travel(datetime.datetime(2025, 7, 15), tick=False)
    @pytest.mark.parametrize(
        "input_product_stock_dict,expected_booking_allowed_datetime",
        [
            (  # no `bookingAllowedDatetime` should default to None
                {"ean": "1234567890123", "stock": {"price": 1234, "quantity": 3}},
                None,
            ),
            (  # `bookingAllowedDatetime=None`
                {"ean": "1234567890123", "bookingAllowedDatetime": None, "stock": {"price": 1234, "quantity": 3}},
                None,
            ),
            (  # `bookingAllowedDatetime` in the future
                {
                    "ean": "1234567890123",
                    "bookingAllowedDatetime": date_utils.utc_datetime_to_department_timezone(
                        datetime.datetime(2025, 7, 17, 10), "75"
                    ).isoformat(),
                    "stock": {"price": 1234, "quantity": 3},
                },
                datetime.datetime(2025, 7, 17, 10),
            ),
            (  # unset `bookingAllowedDatetime`
                {"ean": "2461567890123", "bookingAllowedDatetime": None, "stock": {"price": 1234, "quantity": 3}},
                None,
            ),
        ],
    )
    def test_booking_allowed_datetime_behavior(
        self, input_product_stock_dict, expected_booking_allowed_datetime, client
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue

        offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="1234567890123",
            lastProviderId=venue_provider.provider.id,
        )
        product_with_existing_offer = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="2461567890123",
            lastProviderId=venue_provider.provider.id,
        )
        offers_factories.ThingOfferFactory(
            product=product_with_existing_offer,
            ean=product_with_existing_offer.ean,
            venue=venue,
            lastProvider=venue_provider.provider,
            bookingAllowedDatetime=datetime.datetime(2025, 8, 15),
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={"location": {"type": "physical", "venueId": venue.id}, "products": [input_product_stock_dict]},
        )

        assert response.status_code == 204

        offer_1 = db.session.query(offers_models.Offer).filter_by(ean=input_product_stock_dict["ean"]).one()
        assert offer_1.bookingAllowedDatetime == expected_booking_allowed_datetime

    def test_update_stock_quantity_with_previous_bookings(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )
        offer = offers_factories.ThingOfferFactory(
            product=product, venue=venue_provider.venue, lastProvider=venue_provider.provider
        )
        stock = offers_factories.ThingStockFactory(offer=offer, quantity=10, price=100)
        bookings_factories.BookingFactory(stock=stock, quantity=2, user__deposit__amount=300)

        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "products": [
                    {
                        "ean": product.ean,
                        "stock": {
                            "bookingLimitDatetime": date_utils.format_into_utc_date(tomorrow),
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
            },
        )

        assert response.status_code == 204
        assert stock.quantity == 5
        assert stock.price == decimal.Decimal("12.34")

    def test_update_last_provider_for_existing_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        old_provider = providers_factories.ProviderFactory()
        product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )
        offer = offers_factories.ThingOfferFactory(
            product=product, venue=venue_provider.venue, lastProvider=old_provider, isActive=False
        )
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "products": [{"ean": product.ean, "stock": {"price": 1234, "quantity": 0}}],
            },
        )
        assert response.status_code == 204
        assert offer.lastProvider == venue_provider.provider
        assert offer.isActive == True

    def test_no_new_offer_created_if_ean_exists(self, client):
        """Test that no new offer is created if the ean exists either
        inside offer.ean
        """
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        ean = "1234567890123"
        product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean=ean
        )

        offer = offers_factories.ThingOfferFactory(
            product=product, venue=venue_provider.venue, lastProvider=venue_provider.provider, ean=ean
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
                "products": [{"ean": ean, "stock": {"price": 1234, "quantity": 2}}],
            },
        )

        assert response.status_code == 204

        offer = db.session.query(offers_models.Offer).one()
        assert len(offer.stocks) == 1

        stock = offer.stocks[0]
        assert stock.quantity == 2
        assert stock.price == decimal.Decimal("12.34")

    def test_update_multiple_stocks_with_one_rejected(self, client, caplog):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue

        cd_product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )
        book_product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id, ean="1234527890123"
        )

        cd_offer = offers_factories.ThingOfferFactory(product=cd_product, venue=venue)
        book_offer = offers_factories.ThingOfferFactory(
            product=book_product,
            venue=venue,
            validation=offers_models.OfferValidationStatus.REJECTED,
        )

        cd_stock = offers_factories.ThingStockFactory(offer=cd_offer, quantity=10, price=100)
        book_stock = offers_factories.ThingStockFactory(offer=book_offer, quantity=10, price=100)

        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")
        with caplog.at_level(logging.INFO):
            response = client.with_explicit_token(plain_api_key).post(
                self.endpoint_url,
                json={
                    "location": {"type": "physical", "venueId": venue.id},
                    "products": [
                        {
                            "ean": cd_product.ean,
                            "stock": {
                                "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                                "price": 1234,
                                "quantity": 0,
                            },
                        },
                        {
                            "ean": book_product.ean,
                            "stock": {
                                "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                                "price": 2345,
                                "quantity": 25,
                            },
                        },
                    ],
                },
            )

        log = next(record for record in caplog.records if "Error while creating offer by ean" == record.message)

        assert log.extra == {
            "ean": book_product.ean,
            "venue_id": venue.id,
            "exc": "OfferException",
            "provider_id": venue_provider.provider.id,
        }
        assert response.status_code == 204
        assert cd_stock.quantity == 0
        assert cd_stock.price == decimal.Decimal("12.34")
        assert book_stock.quantity == 10
        assert book_stock.price == decimal.Decimal("100.00")

    @mock.patch("pcapi.tasks.sendinblue_tasks.update_sib_pro_attributes_task")
    def test_valid_ean_without_task_autoflush(self, update_sib_pro_task_mock, client):
        product_provider = providers_factories.ProviderFactory()
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="1234567890123",
            lastProviderId=product_provider.id,
        )
        finance_factories.CustomReimbursementRuleFactory(
            offerer=venue_provider.provider.offererProvider.offerer, rate=0.2, offer=None
        )

        # the update task autoflushes the SQLAlchemy session, but is not executed synchronously in cloud
        # environments, therefore we cannot rely on its side effects
        update_sib_pro_task_mock.side_effect = None

        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        in_ten_minutes_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(in_ten_minutes, "973")
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [
                    {
                        "ean": product.ean,
                        "stock": {
                            "bookingLimitDatetime": in_ten_minutes_in_non_utc_tz.isoformat(),
                            "price": 1234,
                            "quantity": 3,
                        },
                    }
                ],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        assert response.status_code == 204

        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(offers_models.Stock).count() == 1

    @pytest.mark.parametrize(
        "gcu_compatibility_type",
        [
            offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
            offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE,
        ],
    )
    def test_does_not_create_an_offer_of_non_compatible_product(self, client, gcu_compatibility_type):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ProductFactory(ean="1234567890123", gcuCompatibilityType=gcu_compatibility_type)

        client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": product.ean, "stock": {"price": 1234, "quantity": 3}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )
        assert db.session.query(offers_models.Offer).all() == []

    def test_400_when_quantity_is_too_big(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": product.ean, "stock": {"price": 1234, "quantity": 1_000_001}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        assert response.status_code == 400
        assert response.json == {"products.0.stock.quantity": ["Value must be less than 1000000"]}

    @pytest.mark.parametrize(
        "product_json, expected_response_json",
        [
            # `publicationDatetime` in the past
            (
                {
                    "stock": {"price": 10, "quantity": 10},
                    "ean": "1234567890123",
                    "publicationDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)
                    ).isoformat(),
                },
                {"products.0.publicationDatetime": ["The datetime must be in the future."]},
            ),
            # `publicationDatetime` missing tz
            (
                {
                    "stock": {"price": 10, "quantity": 10},
                    "ean": "1234567890123",
                    "publicationDatetime": (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(),
                },
                {"products.0.publicationDatetime": ["The datetime must be timezone-aware."]},
            ),
            # `bookingAllowedDatetime` in the past
            (
                {
                    "stock": {"price": 10, "quantity": 10},
                    "ean": "1234567890123",
                    "bookingAllowedDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)
                    ).isoformat(),
                },
                {"products.0.bookingAllowedDatetime": ["The datetime must be in the future."]},
            ),
            # `bookingAllowedDatetime` missing tz
            (
                {
                    "stock": {"price": 10, "quantity": 10},
                    "ean": "1234567890123",
                    "bookingAllowedDatetime": (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(),
                },
                {"products.0.bookingAllowedDatetime": ["The datetime must be timezone-aware."]},
            ),
            # `stock.bookingLimitDatetime` and `publicationDatetime` not coherent
            (
                {
                    "stock": {
                        "bookingLimitDatetime": (
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
                        ).isoformat(),
                        "price": 10,
                        "quantity": 10,
                    },
                    "ean": "1234567890123",
                    "publicationDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)
                    ).isoformat(),
                },
                {"products.0.__root__": ["`stock.bookingLimitDatetime` must be after `publicationDatetime`"]},
            ),
            # `stock.bookingLimitDatetime` and `bookingLimitDatetime` not coherent
            (
                {
                    "stock": {
                        "bookingLimitDatetime": (
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
                        ).isoformat(),
                        "price": 10,
                        "quantity": 10,
                    },
                    "ean": "1234567890123",
                    "bookingAllowedDatetime": (
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=100)
                    ).isoformat(),
                },
                {"products.0.__root__": ["`stock.bookingLimitDatetime` must be after `bookingAllowedDatetime`"]},
            ),
        ],
    )
    def test_400_when_dates_are_incorrect_or_incoherent(self, product_json, expected_response_json, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={"products": [product_json], "location": {"type": "physical", "venueId": venue_provider.venue.id}},
        )

        assert response.status_code == 400
        assert response.json == expected_response_json

    def test_400_when_ean_wrong_format(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers_factories.ProductFactory(ean="1234567890123")

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": "123456789", "stock": {"price": 1234, "quantity": 3}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        assert response.status_code == 400
        assert response.json == {"products.0.ean": ["ensure this value has at least 13 characters"]}

    def test_400_when_price_too_high(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": product.ean, "stock": {"price": 300000, "quantity": 3}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        assert response.status_code == 400

    def test_update_offer_when_ean_already_exists(self, client):
        product_provider = providers_factories.ProviderFactory()
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean="1234567890123",
            lastProviderId=product_provider.id,
        )

        client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": product.ean, "stock": {"price": 1234, "quantity": 3}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )
        client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": product.ean, "stock": {"price": 7890, "quantity": 3}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        assert db.session.query(offers_models.Offer).one()
        created_stock = db.session.query(offers_models.Stock).one()
        assert created_stock.price == decimal.Decimal("78.90")
        assert created_stock.quantity == 3

    def test_with_custom_address(self, client):
        address = geography_factories.AddressFactory()
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offerer_address = offerers_factories.OffererAddressFactory(
            address=address,
            offerer=venue_provider.venue.managingOfferer,
            label="My beautiful address no one knows about",
        )
        ean, _ = self._get_base_product()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": address.id,
                    "addressLabel": "My beautiful address no one knows about",
                },
                "products": [{"ean": ean, "stock": {"price": 1234, "quantity": 3}}],
            },
        )
        assert response.status_code == 204
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.offererAddress == offerer_address

    def test_with_custom_address_should_create_offerer_address(self, client):
        address = geography_factories.AddressFactory()
        ean, _ = self._get_base_product()
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": address.id,
                    "addressLabel": "My beautiful address no one knows about",
                },
                "products": [{"ean": ean, "stock": {"price": 1234, "quantity": 3}}],
            },
        )

        assert response.status_code == 204
        created_offer = db.session.query(offers_models.Offer).one()
        offerer_address = (
            db.session.query(offerers_models.OffererAddress)
            .filter(
                offerers_models.OffererAddress.addressId == address.id,
                offerers_models.OffererAddress.label == "My beautiful address no one knows about",
            )
            .one()
        )
        assert created_offer.offererAddress == offerer_address

    def test_event_with_custom_address_should_raise_404_because_address_does_not_exist(self, client):
        ean, _ = self._get_base_product()
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "address", "venueId": venue_provider.venueId, "addressId": -1},
                "products": [{"ean": ean, "stock": {"price": 1234, "quantity": 3}}],
            },
        )

        assert response.status_code == 404
        assert response.json == {"location.AddressLocation.addressId": ["There is no address with id -1"]}

    def test_update_offerer_address_for_existing_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product = offers_factories.ThingProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, ean="1234567890123"
        )
        offer = offers_factories.ThingOfferFactory(
            product=product,
            venue=venue_provider.venue,
            lastProvider=venue_provider.provider,
            isActive=False,
        )
        address = geography_factories.AddressFactory()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {"type": "address", "venueId": venue_provider.venue.id, "addressId": address.id},
                "products": [{"ean": product.ean, "stock": {"price": 1234, "quantity": 0}}],
            },
        )
        assert response.status_code == 204
        assert offer.offererAddress.addressId == address.id
        assert offer.isActive == True

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_create_and_update_offer(self, async_index_offer_ids, client):
        product_provider = providers_factories.ProviderFactory()
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        ean_to_update = "1234567890123"
        ean_to_create = "1234567897123"
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean=ean_to_update,
            lastProviderId=product_provider.id,
        )
        offers_factories.ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            ean=ean_to_create,
            lastProviderId=product_provider.id,
        )

        client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [{"ean": ean_to_update, "stock": {"price": 234, "quantity": 12}}],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "products": [
                    {"ean": ean_to_update, "stock": {"price": 1234, "quantity": 3}},
                    {"ean": ean_to_create, "stock": {"price": 9876, "quantity": 22}},
                ],
                "location": {"type": "physical", "venueId": venue_provider.venue.id},
            },
        )

        [updated_offer, created_offer] = db.session.query(offers_models.Offer).order_by(offers_models.Offer.id).all()
        assert updated_offer.ean == ean_to_update
        assert updated_offer.activeStocks[0].price == decimal.Decimal("12.34")
        assert updated_offer.activeStocks[0].quantity == 3

        assert created_offer.ean == ean_to_create
        assert created_offer.activeStocks[0].price == decimal.Decimal("98.76")
        assert created_offer.activeStocks[0].quantity == 22

    def test_invalid_json_raise_syntax_error(self, client):
        plain_api_key, _ = self.setup_provider()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            raw_json="""{
                "location": {"type": "physical", "venueId": venue.id},
                "products": [
                    {
                        "ean": product.ean,
                        "idAtProvider": "id",
                        "stock": {
                            "bookingLimitDatetime": "2022-01-01T16:00:00+04:00",
                            "price": 1234,
                            "quantity": 3,
                        },
                    } // The error is HERE, it misses a comma
                    {
                        "ean": unknown_ean,
                        "stock": {
                            "bookingLimitDatetime": "2022-01-01T16:00:00+04:00",
                            "price": 1234,
                            "quantity": 3,
                        },
                    },
                ],
            },""",
        )

        assert response.status_code == 400
        assert "global" in response.json

    def test_valid_ean_with_missing_stock_price_returns_an_error(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue_provider.venue.managingOfferer)
        ean, _ = self._get_base_product()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": offerer_address.address.id,
                },
                "products": [{"ean": ean, "stock": {"quantity": 3}}],
            },
        )

        assert response.status_code == 400
        assert response.json == {"products.0.stock.price": ["field required"]}

    def test_valid_ean_with_null_stock_price_returns_an_error(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue_provider.venue.managingOfferer)
        ean, _ = self._get_base_product()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": offerer_address.address.id,
                },
                "products": [{"ean": ean, "stock": {"quantity": 3, "price": None}}],
            },
        )

        assert response.status_code == 400
        assert response.json == {"products.0.stock.price": ["none is not an allowed value"]}

    def test_valid_ean_and_free_stock_is_created(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue_provider.venue.managingOfferer)
        ean, _ = self._get_base_product()

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": offerer_address.address.id,
                },
                "products": [{"ean": ean, "stock": {"quantity": 3, "price": 0}}],
            },
        )

        assert response.status_code == 204

        created_product = db.session.query(offers_models.Offer).one()
        created_stock = created_product.stocks[0]

        assert created_stock.price == 0

    def test_valid_ean_and_free_stock_is_updated(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue_provider.venue.managingOfferer)

        ean, product = self._get_base_product()

        stock = offers_factories.ThingStockFactory(
            offer__product=product,
            offer__venue=venue_provider.venue,
            offer__lastProvider=venue_provider.provider,
            quantity=10,
            price=100,
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url,
            json={
                "location": {
                    "type": "address",
                    "venueId": venue_provider.venueId,
                    "addressId": offerer_address.address.id,
                },
                "products": [{"ean": ean, "stock": {"quantity": 3, "price": 0}}],
            },
        )

        assert response.status_code == 204

        updated_stock = db.session.get(offers_models.Stock, stock.id)
        assert updated_stock.price == 0
        assert updated_stock.quantity == 3
