import copy
import decimal
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.categories import subcategories
from pcapi.local_providers import AllocineStocks
from pcapi.models import db
from pcapi.repository import repository

import tests
from tests.domain import fixtures


class AllocineStocksTest:
    class InitTest:
        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_call_allocine_api(self, mock_call_allocine_api, app):
            # Given
            theater_token = "test"

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464", name="Cinéma Allociné", siret="77567146400110"
            )
            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
                venue=venue, venueIdAtOfferProvider=theater_token
            )

            # When
            AllocineStocks(allocine_venue_provider)

            # Then
            mock_call_allocine_api.assert_called_once_with(theater_token)

    class NextTest:
        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @time_machine.travel("2023-12-15 09:00:00", tick=False)
        @pytest.mark.usefixtures("db_session")
        def test_should_return_providable_infos_for_each_movie(self, mock_call_allocine_api, app):
            # Given
            mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )
            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

            # When
            allocine_providable_infos = next(allocine_stocks_provider)

            # Then
            assert len(allocine_providable_infos) == 5

            offer_providable_info = allocine_providable_infos[0]
            stock_providable_info = allocine_providable_infos[1]

            assert offer_providable_info.type == offers_models.Offer
            assert offer_providable_info.id_at_providers == "TW92aWU6MTMxMTM2%77567146400110"
            assert offer_providable_info.new_id_at_provider == "TW92aWU6MTMxMTM2%77567146400110"
            assert offer_providable_info.date_modified_at_provider == datetime(year=2023, month=12, day=15, hour=9)

            assert stock_providable_info.type == offers_models.Stock
            assert stock_providable_info.id_at_providers == "TW92aWU6MTMxMTM2%77567146400110#LOCAL/2023-12-18T14:00:00"
            assert (
                stock_providable_info.new_id_at_provider == "TW92aWU6MTMxMTM2%77567146400110#LOCAL/2023-12-18T14:00:00"
            )
            assert stock_providable_info.date_modified_at_provider == datetime(year=2023, month=12, day=15, hour=9)


class UpdateObjectsTest:
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_offer_with_movie_info(self, mock_call_allocine_api, mock_api_poster):
        # Given
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        mock_api_poster.return_value = bytes()

        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="775671464",
            name="Cinema Allocine",
            siret="77567146400110",
            bookingEmail="toto@example.com",
            withdrawalDetails="Modalités",
        )
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=venue, internalId="PXXXXX", isDuo=False
        )
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.bookingEmail == "toto@example.com"
        assert created_offer._description is None
        assert (
            created_offer.description
            == "Alors que la Premi\u00e8re Guerre Mondiale a \u00e9clat\u00e9, et en r\u00e9ponse aux propos des intellectuels allemands de l'\u00e9poque, Sacha Guitry filme les grands artistes de l'\u00e9poque qui contribuent au rayonnement culturel de la France.\n"
            "Tous les détails du film sur AlloCiné:"
            " https://www.allocine.fr/film/fichefilm_gen_cfilm=131136.html"
        )
        assert created_offer.durationMinutes == 21
        assert created_offer.extraData == {
            "cast": ["Sacha Guitry", "Sarah Bernhardt", "Anatole France"],
            "type": "FEATURE_FILM",
            "visa": "108245",
            "title": "Ceux de chez nous",
            "genres": ["DOCUMENTARY"],
            "credits": [{"person": {"lastName": "Guitry", "firstName": "Sacha"}, "position": {"name": "DIRECTOR"}}],
            "runtime": 21,
            "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=131136.html",
            "synopsis": "Alors que la Premi\u00e8re Guerre Mondiale a \u00e9clat\u00e9, et en r\u00e9ponse aux propos des intellectuels allemands de l'\u00e9poque, Sacha Guitry filme les grands artistes de l'\u00e9poque qui contribuent au rayonnement culturel de la France.",
            "companies": [
                {"name": "Les Acacias", "activity": "Distribution"},
                {"name": "Les Acacias", "activity": "Distribution"},
            ],
            "countries": ["France"],
            "posterUrl": "https://fr.web.img2.acsta.net/medias/nmedia/18/78/15/02/19447537.jpg",
            "allocineId": 131136,
            "releaseDate": "2023-11-01",
            "originalTitle": "Ceux de chez nous",
            "stageDirector": "Sacha Guitry",
            "productionYear": 1915,
        }

        assert not created_offer.isDuo
        assert created_offer.name == "Ceux de chez nous"
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offer.withdrawalDetails == venue.withdrawalDetails

    @patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_RATE", decimal.Decimal("4.0"))
    @patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_NAME", "My awesome festival")
    @patch("pcapi.local_providers.movie_festivals.api.should_apply_movie_festival_rate")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_offer_and_stocks_with_movie_info(
        self, mock_call_allocine_api, mock_api_poster, mock_should_apply_movie_festival_rate
    ):
        # Given
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        mock_api_poster.return_value = bytes()

        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="775671464",
            name="Cinema Allocine",
            siret="77567146400110",
            bookingEmail="toto@example.com",
            withdrawalDetails="Modalités",
        )
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=venue, internalId="PXXXXX", isDuo=False
        )
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
        mock_should_apply_movie_festival_rate.return_value = True

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = db.session.query(offers_models.Offer).first()
        created_stocks = db.session.query(offers_models.Stock).all()

        assert created_offer, "No offer created"

        for created_stock in created_stocks:
            assert created_stock.price == decimal.Decimal("4.0")
            assert created_stock.priceCategory.price == decimal.Decimal("4.0")
            assert created_stock.priceCategory.priceCategoryLabel.label == "My awesome festival"

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_update_existing_offers(self, mock_call_allocine_api, mock_api_poster):
        # Given
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        mock_api_poster.return_value = bytes()

        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="775671464",
            name="Cinéma Allociné",
            siret="77567146400110",
            bookingEmail="toto@example.com",
        )
        offers_factories.OfferFactory(
            name="Test event",
            subcategoryId=subcategories.SEANCE_CINE.id,
            durationMinutes=60,
            idAtProvider="TW92aWU6MTMxMTM2%77567146400110",
            venue=venue,
        )
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        existing_offer = db.session.query(offers_models.Offer).one()
        assert existing_offer.durationMinutes == 21
        assert existing_offer.offererAddressId == venue.offererAddressId

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_new_offer_when_no_offer_exists(self, mock_call_allocine_api, mock_api_poster):
        # Given
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        mock_api_poster.return_value = bytes()

        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="775671464",
            name="Cinema Allocine",
            siret="77567146400110",
            bookingEmail="toto@example.com",
        )

        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.durationMinutes == 21
        assert created_offer.name == "Ceux de chez nous"
        assert created_offer.offererAddressId == venue.offererAddressId

    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.local_providers.allocine.allocine_stocks.AllocineStocks.get_object_thumb")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_product_mediation(self, mock_get_object_thumb, mock_call_allocine_api):
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            mock_get_object_thumb.return_value = thumb_file.read()

        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="775671464",
            name="Cinema Allocine",
            siret="77567146400110",
            bookingEmail="toto@example.com",
        )

        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        allocine_stocks_provider.updateObjects()

        existing_offer = offers_models.Offer.query.one()

        assert existing_offer.image.url == existing_offer.product.productMediations[0].url

    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_create_one_offer_and_associated_stocks(self, mock_poster_get_allocine, mock_call_allocine_api):
        # Given
        mock_poster_get_allocine.return_value = bytes()
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )

        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="775671464",
            name="Cinema Allocine",
            siret="77567146400110",
            bookingEmail="toto@example.com",
        )

        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue, quantity=None, price=10)
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        # When
        allocine_stocks_provider.updateObjects()

        # Then
        created_offer = db.session.query(offers_models.Offer).order_by("name").all()
        created_stock = db.session.query(offers_models.Stock).order_by("beginningDatetime").all()
        created_price_category = db.session.query(offers_models.PriceCategory).all()
        created_price_category_label = db.session.query(offers_models.PriceCategoryLabel).one()

        unique_offer = created_offer[0]

        first_stock = created_stock[0]
        second_stock = created_stock[1]
        third_stock = created_stock[2]

        first_price_category = created_price_category[0]

        assert len(created_offer) == 1
        assert len(created_stock) == 3
        assert len(created_price_category) == 1

        assert unique_offer.name == "Ceux de chez nous"

        assert unique_offer.durationMinutes == 21

        assert first_stock.offerId == unique_offer.id
        assert first_stock.quantity is None
        assert first_stock.price == 10
        assert first_stock.priceCategory == first_price_category
        assert first_stock.beginningDatetime == datetime(2023, 12, 18, 13, 0)
        assert first_stock.bookingLimitDatetime == datetime(2023, 12, 18, 13, 0)

        assert second_stock.offerId == unique_offer.id
        assert second_stock.quantity is None
        assert second_stock.price == 10
        assert second_stock.priceCategory == first_price_category
        assert second_stock.beginningDatetime == datetime(2023, 12, 18, 15, 0)
        assert second_stock.bookingLimitDatetime == datetime(2023, 12, 18, 15, 0)

        assert third_stock.offerId == unique_offer.id
        assert third_stock.quantity is None
        assert third_stock.price == 10
        assert third_stock.priceCategory == first_price_category
        assert third_stock.beginningDatetime == datetime(2023, 12, 18, 15, 0)
        assert third_stock.bookingLimitDatetime == datetime(2023, 12, 18, 15, 0)

        assert first_price_category.offerId == unique_offer.id
        assert first_price_category.price == 10
        assert first_price_category.priceCategoryLabel == created_price_category_label

        assert allocine_stocks_provider.erroredObjects == 0
        assert allocine_stocks_provider.erroredThumbs == 0

    class WhenAllocineStockAreSynchronizedTwiceTest:
        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_update_stocks_based_on_stock_date(self, mock_poster_get_allocine, mock_call_allocine_api):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            updated_showtimes = copy.deepcopy(fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST)
            updated_showtimes["movieShowtimeList"]["edges"][0]["node"]["showtimes"] = updated_showtimes[
                "movieShowtimeList"
            ]["edges"][0]["node"]["showtimes"][:1]
            mock_call_allocine_api.side_effect = [
                allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                    fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
                ),
                allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(updated_showtimes),
            ]

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )

            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_stocks = db.session.query(offers_models.Stock).order_by(offers_models.Stock.beginningDatetime).all()
            offer = db.session.query(offers_models.Offer).first()

            first_stock = created_stocks[0]
            second_stock = created_stocks[1]
            third_stock = created_stocks[2]

            assert len(created_stocks) == 3
            assert first_stock.offerId == offer.id
            assert first_stock.beginningDatetime == datetime(2023, 12, 18, 13, 0)

            assert second_stock.offerId == offer.id
            assert second_stock.beginningDatetime == datetime(2023, 12, 18, 15, 0)

            assert third_stock.offerId == offer.id
            assert third_stock.beginningDatetime == datetime(2023, 12, 18, 15, 0)

            assert db.session.query(offers_models.PriceCategory).count() == 1

        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_create_one_different_offer_and_stock_for_different_venues(
            self, mock_poster_get_allocine, mock_call_allocine_api
        ):
            # Given
            theater_token1 = "test1"
            theater_token2 = "test2"
            mock_result = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )
            mock_call_allocine_api.side_effect = [mock_result, mock_result]
            mock_poster_get_allocine.return_value = bytes()
            offerer = offerers_factories.OffererFactory(siren="775671464")
            venue1 = offerers_factories.VenueFactory(
                managingOfferer=offerer,
                name="Cinema Allocine 1",
                siret="77567146400110",
                bookingEmail="toto1@example.com",
            )
            venue2 = offerers_factories.VenueFactory(
                managingOfferer=offerer,
                name="Cinema Allocine 2",
                siret="98765432345677",
                bookingEmail="toto2@example.com",
            )

            venue_provider1 = providers_factories.AllocineVenueProviderFactory(
                venue=venue1, internalId="P12345", venueIdAtOfferProvider=theater_token1
            )
            venue_provider2 = providers_factories.AllocineVenueProviderFactory(
                venue=venue2, internalId="C12345", venueIdAtOfferProvider=theater_token2
            )

            allocine_stocks_provider1 = AllocineStocks(venue_provider1)
            allocine_stocks_provider1.updateObjects()

            allocine_stocks_provider2 = AllocineStocks(venue_provider2)
            # When
            allocine_stocks_provider2.updateObjects()

            # Then
            created_offer = db.session.query(offers_models.Offer).all()
            created_stock = db.session.query(offers_models.Stock).all()
            created_price_categories = db.session.query(offers_models.PriceCategory).all()
            created_price_categories_labels = db.session.query(offers_models.PriceCategoryLabel).all()

            assert mock_poster_get_allocine.call_count == 2
            assert len(created_offer) == 2
            assert len(created_price_categories) == 2
            assert len(created_price_categories_labels) == 2
            assert db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == venue1.id).count() == 1
            assert db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == venue2.id).count() == 1
            assert len(created_stock) == 6

        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_update_stocks_info_after_pro_user_modification(
            self, mock_poster_get_allocine, mock_call_allocine_api
        ):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_result = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )
            mock_call_allocine_api.side_effect = [mock_result, mock_result]
            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )

            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
                venue=venue, quantity=None, price=10
            )
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            created_stocks = db.session.query(offers_models.Stock).order_by(offers_models.Stock.beginningDatetime).all()

            first_stock = created_stocks[0]
            first_stock.fieldsUpdated = ["quantity", "price"]
            first_stock.quantity = 100
            first_stock.price = 20
            first_stock.priceCategory = offers_models.PriceCategory(
                price=20, offer=first_stock.offer, priceCategoryLabel=first_stock.priceCategory.priceCategoryLabel
            )

            second_stock = created_stocks[1]
            second_stock.fieldsUpdated = ["bookingLimitDatetime"]
            second_stock.bookingLimitDatetime = datetime(2023, 12, 4, 14, 30)

            repository.save(first_stock, second_stock)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            assert len(created_stocks) == 3
            assert len(db.session.query(offers_models.PriceCategory).all()) == 2
            assert first_stock.quantity == 100
            assert first_stock.price == 20
            assert first_stock.priceCategory.price == 20
            assert first_stock.priceCategory.label == "Tarif unique"
            assert first_stock.bookingLimitDatetime == datetime(2023, 12, 18, 13, 0)

            assert second_stock.quantity is None
            assert second_stock.price == 10
            assert second_stock.priceCategory.price == 10
            assert second_stock.priceCategory.label == "Tarif unique"
            assert second_stock.bookingLimitDatetime == datetime(2023, 12, 4, 14, 30)

    @pytest.mark.usefixtures("db_session")
    class WhenOfferHasBeenManuallyUpdatedTest:
        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        def test_should_preserve_manual_modification(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_result = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )
            mock_call_allocine_api.side_effect = [mock_result, mock_result]

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )
            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            created_offer = db.session.query(offers_models.Offer).one()
            created_offer.isDuo = True
            created_offer.fieldsUpdated = ["isDuo"]
            repository.save(created_offer)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_offer = db.session.query(offers_models.Offer).one()
            assert created_offer.isDuo is True

        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        def test_should_succeed_when_additional_price_categories_were_created(
            self, mock_poster_get_allocine, mock_call_allocine_api
        ):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )
            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)

            offer = offers_factories.OfferFactory(
                name="Test event",
                durationMinutes=60,
                idAtProvider="TW92aWU6MTMxMTM2%77567146400110",
                venue=venue,
            )
            offers_factories.PriceCategoryFactory(offer=offer, price=allocine_venue_provider.price)
            newest_price_category = offers_factories.PriceCategoryFactory(
                offer=offer, price=allocine_venue_provider.price, priceCategoryLabel__label="Nouveau tarif"
            )

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            stock = db.session.query(offers_models.Stock).first()
            assert stock.priceCategory == newest_price_category

            assert allocine_stocks_provider.erroredObjects == 0
            assert allocine_stocks_provider.erroredThumbs == 0

        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        def test_should_only_update_default_price_category(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )

            offer = offers_factories.OfferFactory(
                name="Test event",
                durationMinutes=60,
                idAtProvider="TW92aWU6MTMxMTM2%77567146400110",
                venue=venue,
            )
            default_price_category = offers_factories.PriceCategoryFactory(offer=offer, price=decimal.Decimal("10.1"))
            stock_with_price_to_edit = offers_factories.EventStockFactory(
                offer=offer,
                idAtProviders="TW92aWU6MTMxMTM2%77567146400110#LOCAL/2023-12-18T14:00:00",
                priceCategory=default_price_category,
            )

            manually_created_price_category = offers_factories.PriceCategoryFactory(
                offer=offer, price=decimal.Decimal("10.1"), priceCategoryLabel__label="price should not change"
            )
            stock_with_unchanging_price = offers_factories.EventStockFactory(
                offer=offer,
                idAtProviders="TW92aWU6MTMxMTM2%77567146400110#ORIGINAL/2023-12-18T16:00:00",
                priceCategory=manually_created_price_category,
            )

            new_price = decimal.Decimal("1.2")
            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue, price=new_price)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            assert stock_with_price_to_edit.price == new_price
            assert default_price_category.price == new_price

            assert manually_created_price_category.price != new_price
            assert stock_with_unchanging_price.price != new_price

            assert allocine_stocks_provider.erroredObjects == 0
            assert allocine_stocks_provider.erroredThumbs == 0

    class WhenStockHasBeenManuallyDeletedTest:
        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_deletion(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_result = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )
            mock_call_allocine_api.side_effect = [mock_result, mock_result]

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464", name="Cinema Allocine", siret="77567146400110"
            )

            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)

            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            created_stock = db.session.query(offers_models.Stock).order_by(offers_models.Stock.id).first()
            created_stock.isSoftDeleted = True

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_stock = db.session.query(offers_models.Stock).order_by(offers_models.Stock.id).first()
            assert created_stock.isSoftDeleted is True

    class WhenSettingDefaultValuesAtImportTest:
        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_is_duo_default_value(self, mock_poster_get_allocine, mock_call_allocine_api):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_result = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )
            mock_call_allocine_api.side_effect = [mock_result, mock_result]

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )

            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            created_offer = db.session.query(offers_models.Offer).one()
            assert created_offer.isDuo

        @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
        @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
        @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
        @pytest.mark.usefixtures("db_session")
        def test_should_preserve_quantity_default_value(self, mock_poster_get_allocine, mock_call_allocine_api, app):
            # Given
            mock_poster_get_allocine.return_value = bytes()
            mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
                fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
            )

            venue = offerers_factories.VenueFactory(
                managingOfferer__siren="775671464",
                name="Cinema Allocine",
                siret="77567146400110",
                bookingEmail="toto@example.com",
            )

            allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(venue=venue, quantity=50)

            # When
            allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
            allocine_stocks_provider.updateObjects()

            # Then
            stock = db.session.query(offers_models.Stock).first()
            assert stock.quantity == 50

    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.local_providers.allocine.allocine_stocks.AllocineStocks.get_object_thumb")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def should_not_update_thumbnail_more_then_once_a_day(
        self, mock_get_object_thumb, mock_call_allocine_api, mock_api_poster
    ):
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            mock_get_object_thumb.return_value = thumb_file.read()

        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()
        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)

        allocine_stocks_provider.updateObjects()

        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.thumbUrl == created_offer.product.productMediations[0].url
        assert len(created_offer.product.productMediations) == 1
        assert mock_get_object_thumb.call_count == 1

        allocine_stocks_provider.updateObjects()
        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.thumbUrl == created_offer.product.productMediations[0].url
        assert len(created_offer.product.productMediations) == 1
        assert mock_get_object_thumb.call_count == 1


class GetObjectThumbTest:
    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_get_movie_poster_if_poster_url_exist(self, mock_poster_get_allocine, mock_call_allocine_api, app):
        # Given
        mock_call_allocine_api.return_value = allocine_serializers.AllocineMovieShowtimeListResponse.model_validate(
            fixtures.ALLOCINE_MOVIE_SHOWTIME_LIST
        )
        mock_poster_get_allocine.return_value = "poster_thumb"
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
        allocine_stocks_provider.movie = next(iter(allocine_stocks_provider.movies_showtimes)).movie

        # When
        poster_thumb = allocine_stocks_provider.get_object_thumb()

        # Then
        mock_poster_get_allocine.assert_called_once_with(
            "https://fr.web.img2.acsta.net/medias/nmedia/18/78/15/02/19447537.jpg"
        )
        assert poster_thumb == "poster_thumb"

    @patch("pcapi.connectors.api_allocine.get_movies_showtimes_from_allocine")
    @patch("pcapi.local_providers.allocine.allocine_stocks.get_movie_poster")
    @patch("pcapi.settings.ALLOCINE_API_KEY", "token")
    @pytest.mark.usefixtures("db_session")
    def test_should_return_empty_thumb_if_poster_does_not_exist(self, mock_poster_get_allocine, mock_call_allocine_api):
        # Given
        mock_poster_get_allocine.return_value = "poster_thumb"
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        allocine_stocks_provider = AllocineStocks(allocine_venue_provider)
        allocine_stocks_provider.movie = None

        # When
        poster_thumb = allocine_stocks_provider.get_object_thumb()

        # Then
        mock_poster_get_allocine.assert_not_called()
        assert poster_thumb == bytes()
