from decimal import Decimal
from unittest import mock

from freezegun.api import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.providers import api
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.models import ApiErrors
from pcapi.models.product import Product
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody


class CreateVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_prevent_creation_for_non_existing_provider(self):
        # Given
        providerId = "AE"
        venueId = "AE"
        venue_provider = PostVenueProviderBody(providerId=providerId, venueId=venueId)

        # When
        with pytest.raises(ApiErrors) as error:
            api.create_venue_provider(venue_provider)

        # Then
        assert error.value.errors["provider"] == ["Cette source n'est pas disponible"]


def create_product(isbn, **kwargs):
    return factories.ProductFactory(
        idAtProviders=isbn,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"prix_livre": 12},
        **kwargs,
    )


def create_offer(isbn, siret):
    return factories.OfferFactory(product=create_product(isbn), idAtProviders=f"{isbn}@{siret}")


def create_stock(isbn, siret, **kwargs):
    return factories.StockFactory(offer=create_offer(isbn, siret), idAtProviders=f"{isbn}@{siret}", **kwargs)


class SynchronizeStocksTest:
    @pytest.mark.usefixtures("db_session")
    @freeze_time("2020-10-15 09:00:00")
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_execution(self, mock_async_index_offer_ids):
        # Given
        spec = [
            {"ref": "3010000101789", "available": 6},
            {"ref": "3010000101797", "available": 4},
            {"ref": "3010000103769", "available": 18},
            {"ref": "3010000107163", "available": 12},
            {"ref": "3010000108123", "available": 17},
            {"ref": "3010000108124", "available": 17},
            {"ref": "3010000108125", "available": 17},
        ]
        offerers_factories.APIProviderFactory(apiUrl="https://provider_url", authToken="fake_token")
        venue = VenueFactory()
        siret = venue.siret
        provider = offerers_factories.ProviderFactory()
        stock_details = synchronize_provider_api._build_stock_details_from_raw_stocks(spec, siret, provider)

        stock = create_stock(
            spec[0]["ref"],
            siret,
            quantity=20,
        )
        offer = create_offer(spec[1]["ref"], siret)
        product = create_product(spec[2]["ref"])
        create_product(spec[4]["ref"])
        create_product(spec[6]["ref"], isGcuCompatible=False)

        stock_with_booking = create_stock(spec[5]["ref"], siret, quantity=20)
        BookingFactory(stock=stock_with_booking)
        BookingFactory(stock=stock_with_booking, quantity=2)

        # When
        api.synchronize_stocks(stock_details, venue, provider_id=provider.id)

        # Then
        # Test updates stock if already exists
        assert stock.quantity == 6
        assert stock.rawProviderQuantity == 6

        # Test creates stock if does not exist
        assert len(offer.stocks) == 1
        created_stock = offer.stocks[0]
        assert created_stock.quantity == 4
        assert created_stock.rawProviderQuantity == 4

        # Test creates offer if does not exist
        created_offer = Offer.query.filter_by(idAtProviders=f"{spec[2]['ref']}@{siret}").one()
        assert created_offer.stocks[0].quantity == 18

        # Test doesn't create offer if product does not exist or not gcu compatible
        assert Offer.query.filter_by(idAtProviders=f"{spec[3]['ref']}@{siret}").count() == 0
        assert Offer.query.filter_by(idAtProviders=f"{spec[6]['ref']}@{siret}").count() == 0

        # Test second page is actually processed
        second_created_offer = Offer.query.filter_by(idAtProviders=f"{spec[4]['ref']}@{siret}").one()
        assert second_created_offer.stocks[0].quantity == 17

        # Test existing bookings are added to quantity
        assert stock_with_booking.quantity == 17 + 1 + 2
        assert stock_with_booking.rawProviderQuantity == 17

        # Test fill stock attributes
        assert created_stock.price == Decimal("12.00")
        assert created_stock.idAtProviders == f"{spec[1]['ref']}@{siret}"

        # Test fill offers attributes
        assert created_offer.bookingEmail == venue.bookingEmail
        assert created_offer.description == product.description
        assert created_offer.extraData == product.extraData
        assert created_offer.name == product.name
        assert created_offer.productId == product.id
        assert created_offer.venueId == venue.id
        assert created_offer.type == product.type
        assert created_offer.idAtProviders == f"{spec[2]['ref']}@{siret}"
        assert created_offer.lastProviderId == provider.id

        # Test offer reindexation
        mock_async_index_offer_ids.assert_called_with(
            {stock.offer.id, offer.id, stock_with_booking.offer.id, created_offer.id, second_created_offer.id}
        )

    def test_build_new_offers_from_stock_details(self, db_session):
        # Given
        spec = [
            {  # known offer, must be ignored
                "offers_provider_reference": "offer_ref1",
            },
            {  # new one, will be created
                "available_quantity": 17,
                "offers_provider_reference": "offer_ref_2",
                "price": 28.989,
                "products_provider_reference": "isbn_product_ref",
                "stocks_provider_reference": "stock_ref",
            },
            {  # no quantity, must be ignored
                "available_quantity": 0,
                "offers_provider_reference": "offer_ref_3",
                "price": 28.989,
                "products_provider_reference": "isbn_product_ref",
                "stocks_provider_reference": "stock_ref",
            },
        ]

        existing_offers_by_provider_reference = {"offer_ref1"}
        provider = offerers_factories.APIProviderFactory(apiUrl="https://provider_url", authToken="fake_token")
        venue = VenueFactory(bookingEmail="booking_email", withdrawalDetails="My withdrawal details")
        product = Product(
            id=456,
            name="product_name",
            description="product_desc",
            extraData="extra",
            type="ThingType.LIVRE_EDITION",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        products_by_provider_reference = {"isbn_product_ref": product}

        # When
        new_offers = api._build_new_offers_from_stock_details(
            spec,
            existing_offers_by_provider_reference,
            products_by_provider_reference,
            venue,
            provider_id=provider.id,
        )

        # Then
        assert new_offers == [
            Offer(
                bookingEmail="booking_email",
                description="product_desc",
                extraData="extra",
                idAtProviders="offer_ref_2",
                lastProviderId=provider.id,
                name="product_name",
                productId=456,
                venueId=venue.id,
                type="ThingType.LIVRE_EDITION",
                subcategoryId=subcategories.LIVRE_PAPIER.id,
                withdrawalDetails=venue.withdrawalDetails,
            ),
        ]
        new_offer = new_offers[0]
        assert new_offer.bookingEmail == "booking_email"
        assert new_offer.description == "product_desc"
        assert new_offer.extraData == "extra"
        assert new_offer.idAtProviders == "offer_ref_2"
        assert new_offer.idAtProvider == "isbn_product_ref"
        assert new_offer.lastProviderId == provider.id
        assert new_offer.name == "product_name"
        assert new_offer.productId == 456
        assert new_offer.venueId == venue.id
        assert new_offer.type == "ThingType.LIVRE_EDITION"
        assert new_offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert new_offer.withdrawalDetails == venue.withdrawalDetails

    def test_get_stocks_to_upsert(self):
        # Given
        spec = [
            {  # existing, will update
                "offers_provider_reference": "offer_ref1",
                "available_quantity": 15,
                "price": 15.78,
                "products_provider_reference": "product_ref1",
                "stocks_provider_reference": "stock_ref1",
            },
            {  # new, will be added
                "available_quantity": 17,
                "offers_provider_reference": "offer_ref2",
                "price": 28.989,
                "products_provider_reference": "product_ref2",
                "stocks_provider_reference": "stock_ref2",
            },
            {  # no quantity, must be ignored
                "available_quantity": 0,
                "offers_provider_reference": "offer_ref3",
                "price": 28.989,
                "products_provider_reference": "product_ref3",
                "stocks_provider_reference": "stock_ref3",
            },
            {  # existing, will update but set product's price
                "offers_provider_reference": "offer_ref4",
                "available_quantity": 15,
                "price": None,
                "products_provider_reference": "product_ref4",
                "stocks_provider_reference": "stock_ref4",
            },
        ]

        stocks_by_provider_reference = {
            "stock_ref1": {"id": 1, "booking_quantity": 3, "price": 18.0, "quantity": 2},
            "stock_ref4": {"id": 2, "booking_quantity": 3, "price": 18.0, "quantity": 2},
        }
        offers_by_provider_reference = {"offer_ref1": 123, "offer_ref2": 134, "offer_ref4": 123}
        products_by_provider_reference = {
            "product_ref1": Product(extraData={"prix_livre": 7.01}),
            "product_ref2": Product(extraData={"prix_livre": 9.02}),
            "product_ref3": Product(extraData={"prix_livre": 11.03}),
            "product_ref4": Product(extraData={"prix_livre": 7.01}),
        }
        provider_id = 1

        # When
        update_stock_mapping, new_stocks, offer_ids = api._get_stocks_to_upsert(
            spec,
            stocks_by_provider_reference,
            offers_by_provider_reference,
            products_by_provider_reference,
            provider_id,
        )

        assert update_stock_mapping == [
            {
                "id": 1,
                "quantity": 15 + 3,
                "price": 15.78,
                "rawProviderQuantity": 15,
                "lastProviderId": 1,
            },
            {
                "id": 2,
                "quantity": 15 + 3,
                "price": 7.01,
                "rawProviderQuantity": 15,
                "lastProviderId": 1,
            },
        ]

        new_stock = new_stocks[0]
        assert new_stock.quantity == 17
        assert new_stock.bookingLimitDatetime is None
        assert new_stock.offerId == 134
        assert new_stock.price == 28.989
        assert new_stock.idAtProviders == "stock_ref2"
        assert new_stock.lastProviderId == 1

        assert offer_ids == set([123, 134])

    @pytest.mark.parametrize(
        "new_quantity,new_price,existing_stock,expected_result",
        [
            (1, 18.01, {"price": 18.02, "quantity": 4, "booking_quantity": 2}, True),
            (2, 18.01, {"price": 18.01, "quantity": 1, "booking_quantity": 1}, True),
            (0, 18.01, {"price": 18.01, "quantity": 2, "booking_quantity": 1}, True),
            (3, 18.01, {"price": 18.01, "quantity": 2, "booking_quantity": 1}, False),
            (2, 18.01, {"price": 18.01, "quantity": 3, "booking_quantity": 1}, False),
        ],
    )
    def should_reindex_offers(self, new_quantity, new_price, existing_stock, expected_result):
        assert api._should_reindex_offer(new_quantity, new_price, existing_stock) == expected_result
