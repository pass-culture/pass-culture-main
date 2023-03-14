from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from pcapi.connectors.serialization.cine_digital_service_serializers import IdObjectCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowTariffCDS
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.models import Movie
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import PriceCategoryLabel
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import CDSCinemaDetailsFactory
from pcapi.core.providers.factories import CDSCinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider
from pcapi.local_providers.cinema_providers.cds.cds_stocks import CDSStocks
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

import tests


@pytest.mark.usefixtures("db_session")
class CDSStocksTest:
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_get_venue_movies(self, mock_get_venue_movies, mock_get_shows):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
            Movie(
                id="51",
                title="Top Gun",
                duration=150,
                description="Film sur les avions",
                visa="333333",
                posterpath="fakeUrl/topgun.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=51),
                ),
                "price": 5,
            }
        ]
        mock_get_shows.return_value = mocked_shows
        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_movies = list(cds_stocks.movies)

        # Then
        mock_get_venue_movies.assert_called_once()
        assert len(cds_movies) == 2

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_return_providable_info_on_next(self, mock_get_venue_movies, mock_get_shows):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5,
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=51),
                ),
                "price": 5,
            },
        ]
        mock_get_shows.return_value = mocked_shows
        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert len(providable_infos) == 3

        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]
        stock_providable_info = providable_infos[2]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == f"123%{venue_provider.venue.siret}%CDS"
        assert product_providable_info.new_id_at_provider == f"123%{venue_provider.venue.siret}%CDS"

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == f"123%{venue_provider.venue.siret}%CDS"
        assert offer_providable_info.new_id_at_provider == f"123%{venue_provider.venue.siret}%CDS"

        assert stock_providable_info.type == Stock
        assert stock_providable_info.id_at_providers == f"123%{venue_provider.venue.siret}%CDS#1/2022-06-20 11:00:00"
        assert stock_providable_info.new_id_at_provider == f"123%{venue_provider.venue.siret}%CDS#1/2022-06-20 11:00:00"

    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_not_return_providable_info_on_next_when_no_stocks_for_movies(
        self, mock_get_venue_movies, mock_get_shows
    ):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        # these shows are not matching movies (by mediaid)
        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=88888),
                ),
                "price": 5,
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=88888),
                ),
                "price": 5,
            },
        ]
        mock_get_shows.return_value = mocked_shows
        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert len(providable_infos) == 0

    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=True,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_create_offers_for_each_movie(self, mock_get_venue_movies, mock_get_shows, mock_get_internet_sale_gauge):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
            Movie(
                id="51",
                title="Top Gun",
                duration=150,
                description="Film sur les avions",
                visa="333333",
                posterpath="fakeUrl/topgun.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5,
                "price_label": "pass Culture",
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=51),
                ),
                "price": 5,
                "price_label": "pass Culture",
            },
        ]
        mock_get_shows.return_value = mocked_shows

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        assert Offer.query.count() == 2
        assert Product.query.count() == 2

    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=False,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_fill_offer_and_product_and_stock_informations_for_each_movie(
        self, mock_get_venue_movies, mock_get_shows, mock_get_internet_sale_gauge, requests_mock
    ):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="http://fakeUrl/coupez.png",
            ),
            Movie(
                id="51",
                title="Top Gun",
                duration=150,
                description="Film sur les avions",
                visa="333333",
                posterpath="http://fakeUrl/topgun.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("http://fakeUrl/coupez.png", content=bytes())
        requests_mock.get("http://fakeUrl/topgun.png", content=bytes())

        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5.0,
                "price_label": "pass Culture",
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=78,
                    internet_remaining_place=11,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=51),
                ),
                "price": 6.5,
                "price_label": "pass Culture",
            },
        ]
        mock_get_shows.return_value = mocked_shows

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offers = Offer.query.order_by(Offer.id).all()
        created_products = Product.query.order_by(Product.id).all()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_label = PriceCategoryLabel.query.one()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2

        assert created_offers[0].name == "Coupez !"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].description == "Ca tourne mal"
        assert created_offers[0].durationMinutes == 120
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[0].name == "Coupez !"
        assert created_products[0].description == "Ca tourne mal"
        assert created_products[0].durationMinutes == 120
        assert created_products[0].extraData == {"visa": "123456"}

        assert created_stocks[0].quantity == 77
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].beginningDatetime == datetime(2022, 6, 20, 9)

        assert created_offers[1].name == "Top Gun"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Film sur les avions"
        assert created_offers[1].durationMinutes == 150
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id

        assert created_products[1].name == "Top Gun"
        assert created_products[1].description == "Film sur les avions"
        assert created_products[1].durationMinutes == 150
        assert created_products[1].extraData == {"visa": "333333"}

        assert created_stocks[1].quantity == 78
        assert created_stocks[1].price == 6.5
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].bookingLimitDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].beginningDatetime == datetime(2022, 7, 1, 10)

        assert all(
            (category.priceCategoryLabel == created_price_category_label for category in created_price_categories)
        )
        assert created_price_category_label.label == "pass Culture"

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=False,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_fill_stocks_and_price_categories_for_a_movie(
        self, mock_get_venue_movies, mock_get_shows, mock_get_internet_sale_gauge, requests_mock
    ):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="http://fakeUrl/coupez.png",
            )
        ]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_same_film_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5.0,
                "price_label": "Diffusion 2D",
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=78,
                    internet_remaining_place=11,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 6.5,
                "price_label": "Diffusion 3D",
            },
        ]
        mock_get_shows.return_value = mocked_same_film_shows

        requests_mock.get("http://fakeUrl/coupez.png", content=bytes())

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offer = Offer.query.one()
        created_product = Product.query.one()
        created_stocks = Stock.query.order_by(Stock.id).all()
        created_price_categories = PriceCategory.query.order_by(PriceCategory.id).all()
        created_price_category_labels = PriceCategoryLabel.query.order_by(PriceCategoryLabel.label).all()
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2
        assert len(created_price_category_labels) == 2

        assert created_offer.name == "Coupez !"
        assert created_offer.product == created_product
        assert created_offer.venue == venue_provider.venue
        assert created_offer.description == "Ca tourne mal"
        assert created_offer.durationMinutes == 120
        assert created_offer.isDuo
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id

        assert created_product.name == "Coupez !"
        assert created_product.description == "Ca tourne mal"
        assert created_product.durationMinutes == 120
        assert created_product.extraData == {"visa": "123456"}

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

    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=False,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_reuse_price_category(
        self, mock_get_venue_movies, mock_get_shows, mock_get_internet_sale_gauge, requests_mock
    ):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="http://fakeUrl/coupez.png",
            )
        ]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 6.9,
                "price_label": "pass Culture",
            },
        ]
        mock_get_shows.return_value = mocked_shows

        requests_mock.get("http://fakeUrl/coupez.png", content=bytes())

        # When
        CDSStocks(venue_provider=venue_provider).updateObjects()
        CDSStocks(venue_provider=venue_provider).updateObjects()

        # Then
        created_price_category = PriceCategory.query.one()
        assert created_price_category.price == Decimal("6.9")
        assert PriceCategoryLabel.query.count() == 1

    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=True,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_movie_poster")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_create_product_with_correct_thumb(
        self, mock_get_venue_movies, mocked_get_movie_poster, mock_get_shows, mock_get_internet_sale_gauge
    ):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
            Movie(
                id="51",
                title="Top Gun",
                duration=150,
                description="Film sur les avions",
                visa="333333",
                posterpath="fakeUrl/topgun.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5,
                "price_label": "pass Culture",
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=78,
                    internet_remaining_place=11,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=51),
                ),
                "price": 6,
                "price_label": "pass Culture",
            },
        ]
        mock_get_shows.return_value = mocked_shows

        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            mocked_get_movie_poster.return_value = thumb_file.read()

        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_products = Product.query.order_by(Product.id).all()
        assert (
            created_products[0].thumbUrl
            == f"http://localhost/storage/thumbs/products/{humanize(created_products[0].id)}"
        )
        assert created_products[0].thumbCount == 1

        assert (
            created_products[1].thumbUrl
            == f"http://localhost/storage/thumbs/products/{humanize(created_products[1].id)}"
        )
        assert created_products[1].thumbCount == 1

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=True,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_movie_poster")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_not_update_thumbnail_more_then_once_a_day(
        self, mock_get_venue_movies, mocked_get_movie_poster, mock_get_shows, mock_get_internet_sale_gauge
    ):
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5,
                "price_label": "pass Culture",
            },
        ]
        mock_get_shows.return_value = mocked_shows

        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_stocks.updateObjects()

        assert mocked_get_movie_poster.call_count == 1

        cds_stocks.updateObjects()

        assert mocked_get_movie_poster.call_count == 1


@pytest.mark.usefixtures("db_session")
class CDSStocksQuantityTest:
    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        return_value=True,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_update_cds_stock_with_correct_stock_quantity(
        self, mock_get_venue_movies, mock_get_shows, mock_get_internet_sale_gauge
    ):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        cds_venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=cds_venue_provider.venue, idAtProvider=cds_venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5,
                "price_label": "pass Culture",
            }
        ]
        mock_get_shows.return_value = mocked_shows

        # When
        cds_stocks_provider = CDSStocks(venue_provider=cds_venue_provider)
        cds_stocks_provider.updateObjects()

        created_stocks = Stock.query.order_by(Stock.beginningDatetime).all()

        first_stock = created_stocks[0]
        first_stock.fieldsUpdated = ["price"]
        first_stock.quantity = 100
        first_stock.dnBookedQuantity = 1

        repository.save(first_stock)

        # When
        cds_stocks_provider = CDSStocks(venue_provider=cds_venue_provider)
        cds_stocks_provider.updateObjects()

        # Then
        assert len(created_stocks) == 1
        assert first_stock.quantity == 11
        assert first_stock.dnBookedQuantity == 1
