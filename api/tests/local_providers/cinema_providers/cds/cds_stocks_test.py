from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import PriceCategoryLabel
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.core.testing import override_features
from pcapi.local_providers.cinema_providers.cds.cds_stocks import CDSStocks
from pcapi.repository import transaction
from pcapi.utils.human_ids import humanize

import tests

from . import fixtures


def setup_cinema() -> tuple[providers_models.CDSCinemaDetails, providers_models.VenueProvider]:
    cds_provider = providers_models.Provider.query.filter(
        providers_models.Provider.localClass == "CDSStocks",
    ).one()
    venue_provider = providers_factories.VenueProviderFactory(
        provider=cds_provider,
        isDuoOffers=True,
        venueIdAtOfferProvider="cinema_id_test",
    )
    cinema_provider_pivot = providers_factories.CDSCinemaProviderPivotFactory(
        venue=venue_provider.venue,
        idAtProvider=venue_provider.venueIdAtOfferProvider,
    )
    cds_details = providers_factories.CDSCinemaDetailsFactory(
        cinemaProviderPivot=cinema_provider_pivot,
        accountId="account_id",
        cinemaApiToken="token",
    )
    return cds_details, venue_provider


@pytest.mark.usefixtures("db_session")
class CDSStocksTest:
    def _create_products(self):
        offers_factories.ProductFactory(
            name="Coupez !",
            description="Description du produit allociné 1",
            durationMinutes=111,
            extraData={"allocineId": 291483},
        )
        offers_factories.ProductFactory(
            name="Top Gun",
            description="Description du produit allociné 2",
            durationMinutes=222,
            extraData={"allocineId": 2133},
        )

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_get_venue_movies(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        cds_details, venue_provider = setup_cinema()
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [{"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5}]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get(
            f"https://{cds_details.accountId}.fakeurl/mediaoptions?api_token={cds_details.cinemaApiToken}",
            json=fixtures.MEDIA_OPTIONS,
        )
        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_movies = list(cds_stocks.movies)

        # Then
        mock_get_venue_movies.assert_called_once()
        assert len(cds_movies) == 2

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_return_providable_info_on_next(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        cds_details, venue_provider = setup_cinema()
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 5},
        ]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get(
            f"https://{cds_details.accountId}.fakeurl/mediaoptions?api_token={cds_details.cinemaApiToken}",
            json=fixtures.MEDIA_OPTIONS,
        )
        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert len(providable_infos) == 2

        offer_providable_info = providable_infos[0]
        stock_providable_info = providable_infos[1]

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == f"123%{venue_provider.venue.id}%CDS"
        assert offer_providable_info.new_id_at_provider == f"123%{venue_provider.venue.id}%CDS"

        assert stock_providable_info.type == Stock
        assert stock_providable_info.id_at_providers == f"123%{venue_provider.venue.id}%CDS#1/2022-06-20 11:00:00"
        assert stock_providable_info.new_id_at_provider == f"123%{venue_provider.venue.id}%CDS#1/2022-06-20 11:00:00"

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    @override_features(WIP_SYNCHRONIZE_CINEMA_STOCKS_WITH_ALLOCINE_PRODUCTS=True)
    def should_return_empty_providable_info_on_next_if_product_doesnt_exist(
        self, mock_get_venue_movies, mock_get_shows, requests_mock
    ):
        # Given
        cds_details, venue_provider = setup_cinema()
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 5},
        ]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get(
            f"https://{cds_details.accountId}.fakeurl/mediaoptions?api_token={cds_details.cinemaApiToken}",
            json=fixtures.MEDIA_OPTIONS,
        )

        assert Product.query.count() == 0

        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert len(providable_infos) == 0

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    @override_features(WIP_SYNCHRONIZE_CINEMA_STOCKS_WITH_ALLOCINE_PRODUCTS=False)
    def should_create_offers_with_allocine_id_and_visa_if_products_dont_exist(
        self, mock_get_venue_movies, mock_get_shows, requests_mock
    ):
        # Given
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)

        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 5, "price_label": "pass Culture"},
        ]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        assert Product.query.count() == 0

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offers = Offer.query.order_by(Offer.id).all()
        assert len(created_offers) == 2

        assert created_offers[0].name == "Coupez !"
        assert not created_offers[0].product
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert created_offers[0].description == "Ca tourne mal"
        assert created_offers[0].durationMinutes == 120
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"allocineId": 291483, "visa": "123456"}

        assert created_offers[1].name == "Top Gun"
        assert not created_offers[1].product
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Film sur les avions"
        assert created_offers[1].durationMinutes == 150
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"allocineId": 2133, "visa": "333333"}

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_not_return_providable_info_on_next_when_no_stocks_for_movies(
        self, mock_get_venue_movies, mock_get_shows, requests_mock
    ):
        # Given
        cds_details, venue_provider = setup_cinema()
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        requests_mock.get(
            f"https://{cds_details.accountId}.fakeurl/mediaoptions?api_token={cds_details.cinemaApiToken}",
            json=fixtures.MEDIA_OPTIONS,
        )

        # these shows are not matching movies (by mediaid)
        mocked_shows = [
            {"show_information": fixtures.MOVIE_OTHER_SHOW_1, "price": 5},
            {"show_information": fixtures.MOVIE_OTHER_SHOW_2, "price": 5},
        ]
        mock_get_shows.return_value = mocked_shows
        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert providable_infos == []

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_create_offers_for_each_movie(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)

        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 5, "price_label": "pass Culture"},
        ]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        assert Offer.query.count() == 2

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_fill_offer_and_stock_informations_for_each_movie(self, mock_get_venue_movies, requests_mock):
        # Given
        self._create_products()
        _cds_details, venue_provider = setup_cinema()
        get_cinemas_adapter = requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[fixtures.SHOW_1, fixtures.SHOW_2])
        get_voucher_types_adapter = requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[fixtures.VOUCHER_TYPE_PC_1, fixtures.VOUCHER_TYPE_PC_2],
        )

        Product.query.filter(Product.extraData["allocineId"] == "2133").delete(synchronize_session=False)

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offers = Offer.query.order_by(Offer.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2

        # Information fetched from exisiting product
        assert created_offers[0].name == "Coupez !"
        assert created_offers[0].product
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert created_offers[0].description == "Description du produit allociné 1"
        assert created_offers[0].durationMinutes == 111
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"allocineId": 291483, "visa": "123456"}

        assert created_stocks[0].quantity == 77
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].beginningDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].features == ["VF", "3D"]

        # Product does not exist
        assert created_offers[1].name == "Top Gun"
        assert not created_offers[1].product
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Film sur les avions"
        assert created_offers[1].durationMinutes == 150
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"allocineId": 2133, "visa": "333333"}

        assert created_stocks[1].quantity == 78
        assert created_stocks[1].price == 6.5
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].bookingLimitDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].beginningDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].features == []

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "pass Culture"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

        assert get_cinemas_adapter.call_count == 1
        assert get_voucher_types_adapter.call_count == 1

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_fill_offer_and_stock_informations_for_each_movie_based_on_product(
        self, mock_get_venue_movies, requests_mock
    ):
        # Given
        self._create_products()
        _cds_details, venue_provider = setup_cinema()
        get_cinemas_adapter = requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[fixtures.SHOW_1, fixtures.SHOW_2])
        get_voucher_types_adapter = requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[fixtures.VOUCHER_TYPE_PC_1, fixtures.VOUCHER_TYPE_PC_2],
        )

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offers = Offer.query.order_by(Offer.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2

        assert created_offers[0].name == "Coupez !"
        assert created_offers[0].product
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert created_offers[0].description == "Description du produit allociné 1"
        assert created_offers[0].durationMinutes == 111
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"allocineId": 291483, "visa": "123456"}

        assert created_stocks[0].quantity == 77
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].beginningDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].features == ["VF", "3D"]

        assert created_offers[1].name == "Top Gun"
        assert created_offers[1].product
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Description du produit allociné 2"
        assert created_offers[1].durationMinutes == 222
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"allocineId": 2133, "visa": "333333"}

        assert created_stocks[1].quantity == 78
        assert created_stocks[1].price == 6.5
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].bookingLimitDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].beginningDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].features == []

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "pass Culture"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

        assert get_cinemas_adapter.call_count == 1
        assert get_voucher_types_adapter.call_count == 1

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_synchronization_should_try_to_clean_old_idatproviders_if_using_showtime(
        self, mock_get_venue_movies, requests_mock
    ):
        # Given
        _cds_details, venue_provider = setup_cinema()

        # Stock previously created with an idAtProviders built with the showtime, before the fix.
        offers_factories.StockFactory(
            beginningDatetime=datetime(2022, 6, 20, 9),
            idAtProviders=f"123%{venue_provider.venueId}%CDS#1/2022-06-20 11:00:00+02:00",
            offer__venue=venue_provider.venue,
        )
        offers_factories.StockFactory(
            beginningDatetime=datetime(2022, 7, 1, 10),
            idAtProviders=f"51%{venue_provider.venueId}%CDS#2/2022-07-01 12:00:00+02:00",
            offer__venue=venue_provider.venue,
        )

        offers_factories.StockFactory(
            beginningDatetime=datetime(2022, 6, 1, 10),
            idAtProviders=f"51%{venue_provider.venueId}%CDS#2/2022-06-01 12:00:00+02:00",
            offer__venue=venue_provider.venue,
        )

        get_cinemas_adapter = requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[fixtures.SHOW_1, fixtures.SHOW_2])
        get_voucher_types_adapter = requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[fixtures.VOUCHER_TYPE_PC_1, fixtures.VOUCHER_TYPE_PC_2],
        )

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        cds_stocks.updateObjects()

        # Then
        stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(stocks) == 3
        assert len(created_price_categories) == 2

        assert stocks[0].idAtProviders == f"123%{venue_provider.venueId}%CDS#1"

        assert stocks[1].idAtProviders == f"51%{venue_provider.venueId}%CDS#2"

        # Others stocks for which the synchronization is not about, should be left as is
        assert stocks[2].idAtProviders == f"51%{venue_provider.venueId}%CDS#2/2022-06-01 12:00:00+02:00"

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "pass Culture"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

        assert get_cinemas_adapter.call_count == 1
        assert get_voucher_types_adapter.call_count == 1

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_synchronization_shouldnt_build_idatproviders_using_showtime(self, mock_get_venue_movies, requests_mock):
        # Given
        _cds_details, venue_provider = setup_cinema()
        get_cinemas_adapter = requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[fixtures.SHOW_1, fixtures.SHOW_2])
        get_voucher_types_adapter = requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[fixtures.VOUCHER_TYPE_PC_1, fixtures.VOUCHER_TYPE_PC_2],
        )

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2

        assert created_stocks[0].idAtProviders == f"123%{venue_provider.venueId}%CDS#1"

        assert created_stocks[1].idAtProviders == f"51%{venue_provider.venueId}%CDS#2"

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "pass Culture"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

        assert get_cinemas_adapter.call_count == 1
        assert get_voucher_types_adapter.call_count == 1

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_synchronization_do_not_duplicate_stocks_when_beginning_datetime_changed(
        self, mock_get_venue_movies, requests_mock
    ):
        # Given
        _cds_details, venue_provider = setup_cinema()

        offers_factories.StockFactory(
            beginningDatetime=datetime(
                2022, 6, 20, 8
            ),  # A previous sync created this Stock with a beginningDatetime at 08:00
            idAtProviders=f"123%{venue_provider.venueId}%CDS#1",
            offer__venue=venue_provider.venue,
        )
        offers_factories.StockFactory(
            beginningDatetime=datetime(2022, 7, 1, 10),
            idAtProviders=f"51%{venue_provider.venueId}%CDS#2/2022-07-01 12:00:00+02:00",
            offer__venue=venue_provider.venue,
        )
        get_cinemas_adapter = requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )

        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[fixtures.SHOW_1, fixtures.SHOW_2])
        get_voucher_types_adapter = requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[fixtures.VOUCHER_TYPE_PC_1, fixtures.VOUCHER_TYPE_PC_2],
        )

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2

        assert created_stocks[0].idAtProviders == f"123%{venue_provider.venueId}%CDS#1"
        assert created_stocks[0].beginningDatetime == datetime(
            2022, 6, 20, 9
        )  # Now 09:00 instead of 08:00, because the provider changed is mind

        assert created_stocks[1].idAtProviders == f"51%{venue_provider.venueId}%CDS#2"
        assert created_stocks[1].beginningDatetime == datetime(2022, 7, 1, 10)  # Nothing should have changed

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "pass Culture"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

        assert get_cinemas_adapter.call_count == 1
        assert get_voucher_types_adapter.call_count == 1

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    @override_features(WIP_SYNCHRONIZE_CINEMA_STOCKS_WITH_ALLOCINE_PRODUCTS=False)
    def should_fill_stocks_and_price_categories_for_a_movie(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        self._create_products()
        _cds_details, venue_provider = setup_cinema()

        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_same_film_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5.0, "price_label": "Diffusion 2D"},
            {"show_information": fixtures.MOVIE_1_SHOW_2, "price": 6.5, "price_label": "Diffusion 3D"},
        ]
        mock_get_shows.return_value = mocked_same_film_shows

        requests_mock.get("https://example.com/coupez.png", content=bytes())

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_labels = PriceCategoryLabel.query.order_by(PriceCategoryLabel.label).all()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2
        assert len(created_price_category_labels) == 2

        assert created_offer.name == "Coupez !"
        assert created_offer.product
        assert created_offer.venue == venue_provider.venue
        assert created_offer.description == "Description du produit allociné 1"
        assert created_offer.durationMinutes == 111
        assert created_offer.isDuo
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offer.extraData == {"allocineId": 291483, "visa": "123456"}

        assert created_stocks[0].quantity == 77
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offer
        assert created_stocks[0].bookingLimitDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].beginningDatetime == datetime(2022, 6, 20, 9)

        assert created_price_categories[0].price == 5.0
        assert created_price_categories[0].priceCategoryLabel == created_price_category_labels[0]

        assert created_stocks[1].quantity == 78
        assert created_stocks[1].price == 6.5
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offer
        assert created_stocks[1].bookingLimitDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].beginningDatetime == datetime(2022, 7, 1, 10)

        assert created_price_categories[1].price == 6.5
        assert created_price_categories[1].priceCategoryLabel == created_price_category_labels[1]

        assert created_price_category_labels[0].label == "Diffusion 2D"
        assert created_price_category_labels[1].label == "Diffusion 3D"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_reuse_price_category(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 6.9, "price_label": "pass Culture"},
        ]
        mock_get_shows.return_value = mocked_shows

        requests_mock.get("https://example.com/coupez.png", content=bytes())

        # When
        CDSStocks(venue_provider=venue_provider).updateObjects()
        CDSStocks(venue_provider=venue_provider).updateObjects()

        # Then
        created_price_category = PriceCategory.query.one()
        assert created_price_category.price == Decimal("6.9")
        assert PriceCategoryLabel.query.count() == 1

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_movie_poster")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_create_offer_with_correct_thumb(
        self, mock_get_venue_movies, mocked_get_movie_poster, mock_get_shows, requests_mock
    ):
        # Given
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 6, "price_label": "pass Culture"},
        ]
        mock_get_shows.return_value = mocked_shows

        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            mocked_get_movie_poster.return_value = thumb_file.read()

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offers = Offer.query.order_by(Offer.id).all()
        created_meditations = Mediation.query.order_by(Mediation.id).all()

        assert len(created_offers) == 2
        assert len(created_meditations) == 2

        assert (
            created_offers[0].thumbUrl
            == f"http://localhost/storage/thumbs/mediations/{humanize(created_meditations[0].id)}"
        )

        assert (
            created_offers[1].thumbUrl
            == f"http://localhost/storage/thumbs/mediations/{humanize(created_meditations[1].id)}"
        )

        assert cds_stocks.createdThumbs == 2
        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_handle_error_on_movie_poster(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 6, "price_label": "pass Culture"},
        ]
        mock_get_shows.return_value = mocked_shows

        # Simulate 404 on movie poster URLs
        requests_mock.get("https://example.com/coupez.png", status_code=404)
        requests_mock.get("https://example.com/topgun.png", status_code=404)

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        offers = Offer.query.all()
        assert {offer.thumbUrl for offer in offers} == {None}

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_movie_poster")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_not_update_thumbnail_more_then_once_a_day(
        self, mock_get_venue_movies, mocked_get_movie_poster, mock_get_shows, requests_mock
    ):
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_get_movie_poster.return_value = bytes()

        mocked_shows = [{"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"}]
        mock_get_shows.return_value = mocked_shows

        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_stocks.updateObjects()

        assert mocked_get_movie_poster.call_count == 1

        cds_stocks.updateObjects()

        assert mocked_get_movie_poster.call_count == 1

    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_use_new_cache_for_each_synchronisation(self, requests_mock):
        _cds_details, venue_provider = setup_cinema()

        requests_mock.get("https://account_id.fakeurl/media?api_token=token", json=[fixtures.MOVIE_3])
        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[fixtures.SHOW_1])
        get_voucher_type_adapter = requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token", json=[fixtures.VOUCHER_TYPE_PC_1]
        )
        get_cinemas_adapter = requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        requests_mock.get("https://example.com/coupez.png", content=bytes())

        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_stocks.updateObjects()

        assert get_cinemas_adapter.call_count == 1
        assert get_voucher_type_adapter.call_count == 1

        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_stocks.updateObjects()

        assert get_cinemas_adapter.call_count == 2
        assert get_voucher_type_adapter.call_count == 2

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_link_offer_with_known_visa_to_product(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)

        mocked_movies = [fixtures.MOVIE_1, fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"},
            {"show_information": fixtures.MOVIE_2_SHOW_1, "price": 5, "price_label": "pass Culture"},
        ]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        product_1 = offers_factories.ProductFactory(name="Produit 1", extraData={"visa": "123456"})
        product_2 = offers_factories.ProductFactory(name="Produit 2", extraData={"visa": "333333"})

        cgr_stocks = CDSStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()

        created_offers = Offer.query.order_by(Offer.id).all()

        assert len(created_offers) == 2
        assert created_offers[0].product == product_1
        assert created_offers[1].product == product_2


@pytest.mark.usefixtures("db_session")
class CDSStocksQuantityTest:
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def should_update_cds_stock_with_correct_stock_quantity(self, mock_get_venue_movies, mock_get_shows, requests_mock):
        # Given
        _cds_details, venue_provider = setup_cinema()
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=fixtures.MEDIA_OPTIONS)
        mocked_movies = [fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [{"show_information": fixtures.MOVIE_1_SHOW_1, "price": 5, "price_label": "pass Culture"}]
        mock_get_shows.return_value = mocked_shows
        requests_mock.get("https://example.com/coupez.png", content=bytes())
        # When
        cds_stocks_provider = CDSStocks(venue_provider=venue_provider)
        cds_stocks_provider.updateObjects()

        created_stock = Stock.query.one()

        # make a duo booking
        bookings_factories.BookingFactory(stock=created_stock, quantity=2)

        assert created_stock.quantity == 10
        assert created_stock.dnBookedQuantity == 2

        # synchronize with sold out show
        mocked_shows = [
            {"show_information": fixtures.MOVIE_1_SHOW_1_SOLD_OUT, "price": 5, "price_label": "pass Culture"}
        ]
        mock_get_shows.return_value = mocked_shows
        cds_stocks_provider = CDSStocks(venue_provider=venue_provider)
        cds_stocks_provider.updateObjects()

        created_stock = Stock.query.one()

        # Then
        assert created_stock.quantity == 2
        assert created_stock.dnBookedQuantity == 2
