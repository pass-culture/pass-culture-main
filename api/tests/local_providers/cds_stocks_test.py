from pathlib import Path
from unittest.mock import patch

import pytest

from pcapi.core.booking_providers.models import Movie
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.providers.factories import CDSCinemaDetailsFactory
from pcapi.core.providers.factories import CinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider
from pcapi.local_providers.cinema_providers.cds.cds_stocks import CDSStocks
from pcapi.models.product import Product
from pcapi.utils.human_ids import humanize

import tests


@pytest.mark.usefixtures("db_session")
class CDSStocksTest:
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_get_venue_movies(self, mock_get_venue_movies):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
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

        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        cds_movies = list(cds_stocks.movies)

        # Then
        mock_get_venue_movies.assert_called_once()
        assert len(cds_movies) == 2

    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_return_providable_info_on_next(self, mock_get_venue_movies):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
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

        # When
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        providable_infos = next(cds_stocks)

        # Then
        assert len(providable_infos) == 2

        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]

        assert product_providable_info.type == Product
        assert product_providable_info.id_at_providers == "123"
        assert product_providable_info.new_id_at_provider == "123"

        assert offer_providable_info.type == Offer
        assert offer_providable_info.id_at_providers == "123"
        assert offer_providable_info.new_id_at_provider == "123"

    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_create_offers_for_each_movie(self, mock_get_venue_movies):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = CinemaProviderPivotFactory(
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
        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        assert Offer.query.count() == 2
        assert Product.query.count() == 2

    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_fill_offer_and_product_informations_for_each_movie(self, mock_get_venue_movies):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CinemaProviderPivotFactory(
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
        cds_stocks = CDSStocks(venue_provider=venue_provider)

        # When
        cds_stocks.updateObjects()

        # Then
        created_offers = Offer.query.order_by(Offer.id).all()
        created_products = Product.query.order_by(Product.id).all()

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

    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_movie_poster")
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def should_create_product_with_correct_thumb(self, mock_get_venue_movies, mocked_get_movie_poster):
        # Given
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(provider=cds_provider, isDuoOffers=True)
        cinema_provider_pivot = CinemaProviderPivotFactory(
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
