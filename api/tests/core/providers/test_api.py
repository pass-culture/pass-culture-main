from decimal import Decimal
from unittest import mock

from freezegun.api import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.models import Offer
from pcapi.core.providers import api
from pcapi.core.providers.exceptions import ProviderNotFound
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import StockDetail
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.models.product import Product
from pcapi.models.product import UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER


class CreateVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_prevent_creation_for_non_existing_provider(self):
        # Given
        providerId = 1
        venueId = 2

        # When
        with pytest.raises(ProviderNotFound):
            api.create_venue_provider(providerId, venueId)

        # Then
        assert not VenueProvider.query.first()


def create_product(isbn, **kwargs):
    return factories.ProductFactory(
        idAtProviders=isbn,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"prix_livre": 12},
        **kwargs,
    )


def create_offer(isbn, venue: Venue):
    return factories.OfferFactory(product=create_product(isbn), idAtProvider=isbn, venue=venue)


def create_stock(isbn, siret, venue: Venue, **kwargs):
    return factories.StockFactory(offer=create_offer(isbn, venue), idAtProviders=f"{isbn}@{siret}", **kwargs)


@pytest.mark.usefixtures("db_session")
def test_reset_stock_quantity():
    offer = OfferFactory(idAtProvider="1")
    venue = offer.venue
    stock1_no_bookings = StockFactory(offer=offer, quantity=10)
    stock2_only_cancelled_bookings = StockFactory(offer=offer, quantity=10)
    CancelledBookingFactory(stock=stock2_only_cancelled_bookings)
    stock3_mix_of_bookings = StockFactory(offer=offer, quantity=10)
    BookingFactory(stock=stock3_mix_of_bookings)
    CancelledBookingFactory(stock=stock3_mix_of_bookings)
    manually_added_offer = OfferFactory(venue=venue)
    stock4_manually_added = StockFactory(offer=manually_added_offer, quantity=10)
    stock5_other_venue = StockFactory(quantity=10)

    api.reset_stock_quantity(venue)

    assert stock1_no_bookings.quantity == 0
    assert stock2_only_cancelled_bookings.quantity == 0
    assert stock3_mix_of_bookings.quantity == 1
    assert stock4_manually_added.quantity == 10
    assert stock5_other_venue.quantity == 10


@pytest.mark.usefixtures("db_session")
def test_update_last_provider_id():
    provider1 = providers_factories.ProviderFactory()
    provider2 = providers_factories.ProviderFactory()
    venue = offerers_factories.VenueFactory()
    offer1_synced = OfferFactory(venue=venue, idAtProvider=1, lastProvider=provider1)
    offer2_manual = OfferFactory(venue=venue, idAtProvider=None)
    offer3_other_venue = OfferFactory(idAtProvider=2, lastProvider=provider1)

    api.update_last_provider_id(venue, provider2.id)

    assert offer1_synced.lastProvider == provider2
    assert offer2_manual.idAtProvider is None
    assert offer3_other_venue.lastProvider == provider1


@pytest.mark.usefixtures("db_session")
@mock.patch("pcapi.core.providers.api._siret_can_be_synchronized", lambda *args: True)
def test_change_venue_provider():
    api_url = "https://example.com/provider/api"
    provider = providers_factories.APIProviderFactory()
    venue_provider = providers_factories.VenueProviderFactory(provider=provider)
    venue = venue_provider.venue
    stock = StockFactory(quantity=10, offer__venue=venue, offer__idAtProvider="1")
    BookingFactory(stock=stock)
    new_provider = providers_factories.APIProviderFactory(apiUrl=api_url)

    api.change_venue_provider(venue_provider, new_provider.id)

    # Check venue_provider has change provider and sync date reset
    assert len(venue.venueProviders) == 1
    assert venue.venueProviders[0].providerId == new_provider.id
    assert venue.venueProviders[0].lastSyncDate == None
    # Check that the quantity of existing stocks has been reset.
    assert stock.quantity == 1
    assert stock.offer.lastProviderId == new_provider.id


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
            {"ref": "3010000102735", "available": 1},
            {"ref": "3010000105566", "available": 3},
        ]
        providers_factories.APIProviderFactory(apiUrl="https://provider_url", authToken="fake_token")
        venue = offerers_factories.VenueFactory()
        siret = venue.siret
        provider = providers_factories.ProviderFactory()
        stock_details = synchronize_provider_api._build_stock_details_from_raw_stocks(spec, siret, provider, venue.id)

        stock = create_stock(
            spec[0]["ref"],
            siret,
            venue,
            quantity=20,
        )
        offer = create_offer(spec[1]["ref"], venue)
        product = create_product(spec[2]["ref"])
        create_product(spec[4]["ref"])
        create_product(spec[6]["ref"], isGcuCompatible=False)
        create_product(spec[7]["ref"], isSynchronizationCompatible=False)
        create_product(spec[8]["ref"], name=UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER)

        stock_with_booking = create_stock(spec[5]["ref"], siret, venue, quantity=20)
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
        created_offer = Offer.query.filter_by(idAtProvider=spec[2]["ref"]).one()
        assert created_offer.stocks[0].quantity == 18

        # Test doesn't creates offer if product is unrealsed or unavailable
        offer_not_created = Offer.query.filter_by(idAtProvider=spec[8]["ref"]).one_or_none()
        assert offer_not_created is None

        # Test doesn't create offer if product does not exist or not gcu compatible or not synchronization compatible
        assert Offer.query.filter_by(idAtProvider=spec[3]["ref"]).count() == 0
        assert Offer.query.filter_by(idAtProvider=spec[6]["ref"]).count() == 0
        assert Offer.query.filter_by(idAtProvider=spec[7]["ref"]).count() == 0

        # Test second page is actually processed
        second_created_offer = Offer.query.filter_by(idAtProvider=spec[4]["ref"]).one()
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
        assert created_offer.idAtProvider == spec[2]["ref"]
        assert created_offer.lastProviderId == provider.id

        # Test offer reindexation
        mock_async_index_offer_ids.assert_called_with(
            {stock.offer.id, offer.id, stock_with_booking.offer.id, created_offer.id, second_created_offer.id}
        )

    def test_build_new_offers_from_stock_details(self, db_session):
        # Given
        spec = [
            StockDetail(  # known offer, must be ignored
                available_quantity=1,
                offers_provider_reference="offer_ref1",
                venue_reference="venue_ref1",
                products_provider_reference="isbn_product_ref",
                stocks_provider_reference="stock_ref",
                price=28.989,
            ),
            StockDetail(  # new one, will be created
                available_quantity=17,
                offers_provider_reference="offer_ref_2",
                price=28.989,
                products_provider_reference="isbn_product_ref",
                stocks_provider_reference="stock_ref",
                venue_reference="venue_ref2",
            ),
            # no quantity, must be ignored
            StockDetail(
                available_quantity=0,
                offers_provider_reference="offer_ref_3",
                price=28.989,
                products_provider_reference="isbn_product_ref",
                stocks_provider_reference="stock_ref",
                venue_reference="venue_ref3",
            ),
        ]

        existing_offers_by_provider_reference = {"offer_ref1": 1}
        existing_offers_by_venue_reference = {"venue_ref1": 1}
        provider = providers_factories.APIProviderFactory(apiUrl="https://provider_url", authToken="fake_token")
        venue = offerers_factories.VenueFactory(bookingEmail="booking_email", withdrawalDetails="My withdrawal details")
        product = Product(
            id=456,
            name="product_name",
            description="product_desc",
            extraData="extra",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        products_by_provider_reference = {"isbn_product_ref": product}

        # When
        new_offers = api._build_new_offers_from_stock_details(
            spec,
            existing_offers_by_provider_reference,
            products_by_provider_reference,
            existing_offers_by_venue_reference,
            venue,
            provider_id=provider.id,
        )

        # Then
        assert len(new_offers) == 1
        new_offer = new_offers[0]
        assert new_offer.bookingEmail == "booking_email"
        assert new_offer.description == "product_desc"
        assert new_offer.extraData == "extra"
        assert new_offer.idAtProvider == "isbn_product_ref"
        assert new_offer.lastProviderId == provider.id
        assert new_offer.name == "product_name"
        assert new_offer.productId == 456
        assert new_offer.venueId == venue.id
        assert new_offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert new_offer.withdrawalDetails == venue.withdrawalDetails

    def test_get_stocks_to_upsert(self):
        # Given
        spec = [
            StockDetail(  # existing, will update
                offers_provider_reference="offer_ref1",
                available_quantity=15,
                price=15.78,
                products_provider_reference="product_ref1",
                stocks_provider_reference="stock_ref1",
                venue_reference="venue_ref1",
            ),
            StockDetail(  # new, will be added
                available_quantity=17,
                offers_provider_reference="offer_ref2",
                price=28.989,
                products_provider_reference="product_ref2",
                stocks_provider_reference="stock_ref2",
                venue_reference="venue_ref2",
            ),
            StockDetail(  # no quantity, must be ignored
                available_quantity=0,
                offers_provider_reference="offer_ref3",
                price=28.989,
                products_provider_reference="product_ref3",
                stocks_provider_reference="stock_ref3",
                venue_reference="venue_ref3",
            ),
            StockDetail(  # existing, will update but set product's price
                offers_provider_reference="offer_ref4",
                available_quantity=15,
                price=None,
                products_provider_reference="product_ref4",
                stocks_provider_reference="stock_ref4",
                venue_reference="venue_ref4",
            ),
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


class DeleteVenueProviderTest:
    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_delete_venue_provider(self, mocked_update_all_offers_active_status_job):
        venue_provider = providers_factories.VenueProviderFactory()
        venue = venue_provider.venue

        api.delete_venue_provider(venue_provider)

        assert not venue.venueProviders
        mocked_update_all_offers_active_status_job.assert_called_once_with(venue.id, venue_provider.providerId, False)
