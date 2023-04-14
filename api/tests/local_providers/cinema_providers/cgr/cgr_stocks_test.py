import datetime
import decimal
from decimal import Decimal
from pathlib import Path

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offers.models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import CGRStocks
from pcapi.utils.human_ids import humanize

import tests
from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures


@pytest.mark.usefixtures("db_session")
class CGRStocksTest:
    def should_return_providable_info_on_next(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        providable_infos = next(cgr_stocks)

        assert len(providable_infos) == 3
        product_providable_info = providable_infos[0]
        offer_providable_info = providable_infos[1]
        stock_providable_info = providable_infos[2]

        assert product_providable_info.type == offers_models.Product
        assert product_providable_info.id_at_providers == "138473%CGR"
        assert product_providable_info.new_id_at_provider == "138473%CGR"

        assert offer_providable_info.type == offers_models.Offer
        assert offer_providable_info.id_at_providers == f"138473%{venue_provider.venue.id}%CGR"
        assert offer_providable_info.new_id_at_provider == f"138473%{venue_provider.venue.id}%CGR"

        assert stock_providable_info.type == offers_models.Stock
        assert stock_providable_info.id_at_providers == f"138473%{venue_provider.venue.id}%CGR#177182"
        assert stock_providable_info.new_id_at_provider == f"138473%{venue_provider.venue.id}%CGR#177182"

    def should_fill_offer_and_product_and_stock_informations_for_each_movie(self, requests_mock):
        requests_mock.get("https://example.com/149341.jpg", content=bytes())
        requests_mock.get("https://example.com/82382.jpg", content=bytes())
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_response_template([fixtures.FILM_138473, fixtures.FILM_234099]),
        )

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, isDuoOffers=True)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()

        created_offers = offers_models.Offer.query.order_by(offers_models.Offer.id).all()
        created_products = offers_models.Product.query.order_by(offers_models.Product.id).all()
        created_stocks = offers_models.Stock.query.order_by(offers_models.Stock.id).all()
        created_price_categories = offers_models.PriceCategory.query.order_by(offers_models.PriceCategory.id).all()
        created_price_categories_labels = offers_models.PriceCategoryLabel.query.order_by(
            offers_models.PriceCategoryLabel.id
        ).all()
        assert len(created_offers) == 2
        assert len(created_products) == 2
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 2

        assert created_offers[0].name == "Venom"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert (
            created_offers[0].description
            == "Possédé par un symbiote qui agit de manière autonome, le journaliste Eddie Brock devient le protecteur létal Venom."
        )
        assert created_offers[0].durationMinutes == 112
        assert created_offers[0].isDuo
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].extraData == {"visa": "149341"}

        assert created_products[0].name == "Venom"
        assert (
            created_products[0].description
            == "Possédé par un symbiote qui agit de manière autonome, le journaliste Eddie Brock devient le protecteur létal Venom."
        )
        assert created_products[0].durationMinutes == 112
        assert created_products[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_products[0].extraData == {"visa": "149341"}

        assert created_stocks[0].quantity == 99
        assert created_stocks[0].price == Decimal("6.9")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 1, 29, 13)
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 1, 29, 13)
        assert created_stocks[0].priceCategory.price == Decimal("6.9")
        assert created_stocks[0].priceCategory.priceCategoryLabel.label == "Tarif Standard ICE"

        assert created_offers[1].name == "Super Mario Bros, Le Film"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Un film basé sur l'univers du célèbre jeu : Super Mario Bros."
        assert created_offers[1].durationMinutes == 92
        assert created_offers[1].isDuo
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].extraData == {"visa": "82382"}

        assert created_products[1].name == "Super Mario Bros, Le Film"
        assert created_products[1].description == "Un film basé sur l'univers du célèbre jeu : Super Mario Bros."
        assert created_products[1].durationMinutes == 92
        assert created_products[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_products[1].extraData == {"visa": "82382"}

        assert created_stocks[1].quantity == 168
        assert created_stocks[1].price == Decimal(11.00)
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 3, 4, 15)
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 3, 4, 15)
        assert created_stocks[1].priceCategory.price == Decimal(11.00)
        assert created_stocks[1].priceCategory.priceCategoryLabel.label == "Tarif standard 3D"

    def should_fill_stocks_and_price_categories_for_a_movie(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, isDuoOffers=True)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=fixtures.cgr_response_template([fixtures.FILM_234099_WITH_THREE_SEANCES]),
        )

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()

        created_offer = offers_models.Offer.query.one()
        created_product = offers_models.Product.query.one()
        created_stocks = offers_models.Stock.query.order_by(offers_models.Stock.id).all()
        created_price_categories = offers_models.PriceCategory.query.order_by(offers_models.PriceCategory.id).all()
        created_price_category_labels = offers_models.PriceCategoryLabel.query.order_by(
            offers_models.PriceCategoryLabel.id
        ).all()

        assert len(created_stocks) == 3
        assert len(created_price_categories) == 3
        assert len(created_price_category_labels) == 3

        assert created_offer.name == "Super Mario Bros, Le Film"
        assert created_offer.product == created_product
        assert created_offer.venue == venue_provider.venue
        assert created_offer.description == "Un film basé sur l'univers du célèbre jeu : Super Mario Bros."
        assert created_offer.durationMinutes == 92
        assert created_offer.isDuo
        assert created_offer.subcategoryId == subcategories.SEANCE_CINE.id

        assert created_product.name == "Super Mario Bros, Le Film"
        assert created_product.description == "Un film basé sur l'univers du célèbre jeu : Super Mario Bros."
        assert created_product.durationMinutes == 92
        assert created_product.extraData == {"visa": "82382"}

        assert created_stocks[0].quantity == 168
        assert created_stocks[0].price == 11.0
        assert created_stocks[0].priceCategory == created_price_categories[0]
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offer
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 3, 4, 15)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 3, 4, 15)
        assert created_price_categories[0].price == 11.0
        assert created_price_categories[0].priceCategoryLabel == created_price_category_labels[0]
        assert created_price_category_labels[0].label == "Tarif standard 3D"

        assert created_stocks[1].quantity == 56
        assert created_stocks[1].price == Decimal("7.2")
        assert created_stocks[1].priceCategory == created_price_categories[1]
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offer
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 3, 5, 15)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 3, 5, 15)
        assert created_price_categories[1].price == Decimal("7.2")
        assert created_price_categories[1].priceCategoryLabel == created_price_category_labels[1]
        assert created_price_category_labels[1].label == "Tarif Standard ICE"

        assert created_stocks[2].quantity == 132
        assert created_stocks[2].price == 11.00
        assert created_stocks[2].priceCategory == created_price_categories[2]
        assert created_stocks[2].dateCreated is not None
        assert created_stocks[2].offer == created_offer
        assert created_stocks[2].bookingLimitDatetime == datetime.datetime(2023, 3, 6, 15)
        assert created_stocks[2].beginningDatetime == datetime.datetime(2023, 3, 6, 15)
        assert created_price_categories[2].price == 11.00
        assert created_price_categories[2].priceCategoryLabel == created_price_category_labels[2]
        assert created_price_category_labels[2].label == "Tarif Standard"

    def should_reuse_price_category(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, isDuoOffers=True)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )

        CGRStocks(venue_provider=venue_provider).updateObjects()
        CGRStocks(venue_provider=venue_provider).updateObjects()

        created_price_category = offers_models.PriceCategory.query.one()
        assert created_price_category.price == decimal.Decimal("6.9")

    def should_update_stock_with_the_correct_stock_quantity(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, isDuoOffers=True)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        requests_mock.get("https://example.com/149341.jpg")

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()
        created_stock = offers_models.Stock.query.one()
        # we received quantity 99
        assert created_stock.quantity == 99

        # we manually edit the Stock
        created_stock.quantity = 150
        created_stock.dnBookedQuantity = 2

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()

        created_stocks = offers_models.Stock.query.all()

        assert len(created_stocks) == 1
        # we still receive quantity = 99, so we edit our Stock.quantity to match reality
        assert created_stocks[0].quantity == 101
        assert created_stocks[0].dnBookedQuantity == 2

    def should_create_product_with_correct_thumb(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, isDuoOffers=True)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )

        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            seagull_poster = thumb_file.read()
        requests_mock.get("https://example.com/149341.jpg", content=seagull_poster)

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()

        created_products = offers_models.Product.query.order_by(offers_models.Product.id).all()
        assert len(created_products) == 1
        assert (
            created_products[0].thumbUrl
            == f"http://localhost/storage/thumbs/products/{humanize(created_products[0].id)}"
        )
        assert created_products[0].thumbCount == 1

    def should_not_update_thumbnail_more_then_once_a_day(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider, isDuoOffers=True)
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )

        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )
        get_poster_adapter = requests_mock.get("https://example.com/149341.jpg", content=bytes())

        cgr_stocks = CGRStocks(venue_provider=venue_provider)
        cgr_stocks.updateObjects()

        assert get_poster_adapter.call_count == 1

        cgr_stocks.updateObjects()

        assert get_poster_adapter.call_count == 1
