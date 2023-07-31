from base64 import b64decode
import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from pcapi import settings
from pcapi.connectors import ems
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.provider_manager import synchronize_ems_venue_providers
from pcapi.utils.human_ids import humanize

import tests

from . import fixtures


@pytest.mark.usefixtures("db_session")
class EMSStocksTest:
    def test_we_log_accordingly_to_ems_api_specification(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        synchronize_ems_venue_providers()

        history_api_call = requests_mock.request_history[0]
        assert "Authorization" in history_api_call.headers
        assert history_api_call.headers["Authorization"].startswith("Basic")
        credentials = history_api_call.headers["Authorization"].split("Basic ")[1]
        assert b64decode(credentials).decode() == f"{settings.EMS_API_USER}:{settings.EMS_API_PASSWORD}"

    def should_fill_and_create_offer_and_product_and_stock_information_for_each_movie(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        venue = offerers_factories.VenueFactory(
            bookingEmail="booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997"
        )
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=ems_provider, idAtProvider="9997"
        )
        cinema_detail = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        synchronize_ems_venue_providers()

        created_offers = offers_models.Offer.query.order_by(offers_models.Offer.id).all()
        created_products = offers_models.Product.query.order_by(offers_models.Product.id).all()
        created_stocks = offers_models.Stock.query.order_by(offers_models.Stock.id).all()
        created_price_categories = offers_models.PriceCategory.query.order_by(offers_models.PriceCategory.id).all()
        created_price_categories_labels = offers_models.PriceCategoryLabel.query.order_by(
            offers_models.PriceCategoryLabel.id
        ).all()

        assert len(created_offers) == 2
        assert len(created_products) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 2

        assert created_offers[0].name == "Spider-Man : Across the Spider-Verse"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert (
            created_offers[0].description
            == "Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus."
        )

        assert created_offers[0].durationMinutes == 141
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"

        assert created_products[0].name == "Spider-Man : Across the Spider-Verse"
        assert (
            created_products[0].description
            == "Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus."
        )
        assert created_products[0].durationMinutes == 141
        assert created_products[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert not created_stocks[0].quantity
        assert created_stocks[0].price == Decimal("7.15")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 7, 11, 10)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 7, 11, 10)
        assert created_stocks[0].priceCategory.price == Decimal("7.15")
        assert created_stocks[0].priceCategory.label == "Tarif pass Culture 7.15€"
        assert created_stocks[0].features == ["VF", "3D"]

        assert not created_stocks[1].quantity
        assert created_stocks[1].price == Decimal("7.15")
        assert created_stocks[1].dateCreated
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 7, 11, 12, 30)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 7, 11, 12, 30)
        assert created_stocks[1].priceCategory.price == Decimal("7.15")
        assert created_stocks[1].priceCategory.label == "Tarif pass Culture 7.15€"
        assert created_stocks[1].features == ["VF", "3D"]

        assert created_offers[1].name == "Transformers : Rise of the Beasts"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert (
            created_offers[1].description
            == "Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons."
        )

        assert created_offers[1].durationMinutes == 127
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].bookingEmail == "booking@example.com"
        assert created_offers[1].withdrawalDetails == "Modalité de retrait"

        assert created_products[1].name == "Transformers : Rise of the Beasts"
        assert (
            created_products[1].description
            == "Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons."
        )
        assert created_products[1].durationMinutes == 127
        assert created_products[1].subcategoryId == subcategories.SEANCE_CINE.id

        assert not created_stocks[2].quantity
        assert created_stocks[2].price == Decimal("5.15")
        assert created_stocks[2].dateCreated
        assert created_stocks[2].bookingLimitDatetime == datetime.datetime(2023, 7, 11, 10)
        assert created_stocks[2].beginningDatetime == datetime.datetime(2023, 7, 11, 10)
        assert created_stocks[2].priceCategory.price == Decimal("5.15")
        assert created_stocks[2].priceCategory.label == "Tarif pass Culture 5.15€"
        assert created_stocks[2].features == ["VF"]

        # Ensuring we are keeping tracks of current version of our stocks
        assert cinema_detail.lastVersion == 0

    def should_reuse_price_category(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        venue = offerers_factories.VenueFactory(
            bookingEmail="booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997"
        )

        EMSStocks(venue_provider=venue_provider, site=ems.get_cinemas_programs().sites[0], version=0).synchronize()
        EMSStocks(venue_provider=venue_provider, site=ems.get_cinemas_programs().sites[0], version=0).synchronize()

        created_price_category = offers_models.PriceCategory.query.all()
        assert len(created_price_category) == 2

    def should_create_product_with_correct_thumb(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")

        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=poster)

        ems_stocks = EMSStocks(venue_provider=venue_provider, site=ems.get_cinemas_programs().sites[1], version=0)
        ems_stocks.synchronize()

        created_product = offers_models.Product.query.one()
        assert created_product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(created_product.id)}"
        assert created_product.thumbCount == 1

    def test_ems_is_a_provider_as_others(self):
        venue = offerers_factories.VenueFactory(
            bookingEmail="booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997"
        )

        assert ems_provider.isCinemaProvider is True
        assert venue_provider.isFromCinemaProvider is True
