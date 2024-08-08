from base64 import b64decode
from csv import DictReader
import datetime
from decimal import Decimal
import logging
from pathlib import Path
from unittest import mock

import pytest

from pcapi import settings
from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import override_features
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.provider_manager import collect_elligible_venues_and_activate_ems_sync
from pcapi.local_providers.provider_manager import synchronize_ems_venue_providers
from pcapi.utils.human_ids import humanize

import tests
from tests.local_providers.provider_test_utils import create_finance_event_to_update

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

    def should_fill_and_create_offer_and_stock_information_for_each_movie_if_product_doesnt_exist(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        venue = offerers_factories.VenueFactory(
            bookingEmail="seyne-sur-mer-booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997", isDuoOffers=True
        )
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=ems_provider, idAtProvider="9997"
        )
        cinema_detail = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        assert offers_models.Product.query.count() == 0

        synchronize_ems_venue_providers()

        self._assert_seyne_sur_mer_initial_sync(venue, venue_provider, cinema_detail, 86400)

    def should_fill_and_create_offer_and_stock_information_for_each_movie_based_on_product(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        offers_factories.ProductFactory(
            name="Produit allociné 1",
            description="Description du produit allociné 1",
            durationMinutes=111,
            extraData={"allocineId": 269975},
        )
        offers_factories.ProductFactory(
            name="Produit allociné 2",
            description="Description du produit allociné 2",
            durationMinutes=222,
            extraData={"allocineId": 241065},
        )

        venue = offerers_factories.VenueFactory(
            bookingEmail="seyne-sur-mer-booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997", isDuoOffers=True
        )
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=ems_provider, idAtProvider="9997"
        )
        cinema_detail = providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        synchronize_ems_venue_providers()

        self._assert_seyne_sur_mer_initial_sync_based_on_product(venue, venue_provider, cinema_detail, 86400)

    def should_update_finance_event_when_stock_beginning_datetime_is_updated(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        venue = offerers_factories.VenueFactory(
            bookingEmail="seyne-sur-mer-booking@example.com",
            withdrawalDetails="Modalité de retrait",
            pricing_point="self",
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997"
        )
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=ems_provider, idAtProvider="9997"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            synchronize_ems_venue_providers()
        mock_update_finance_event.assert_not_called()

        # synchronize with show with same date
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            synchronize_ems_venue_providers()
        mock_update_finance_event.assert_not_called()

        # synchronize with show with new date
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0_WITH_NEW_DATE)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        # targeting specific stock whith idAtprovider
        stock = offers_models.Stock.query.where(offers_models.Stock.idAtProviders.like("%999700079243")).first()
        assert stock is not None
        event_created = create_finance_event_to_update(stock=stock, venue_provider=venue_provider)
        last_pricingOrderingDate = event_created.pricingOrderingDate
        synchronize_ems_venue_providers()
        assert event_created.pricingOrderingDate != last_pricingOrderingDate

    def should_reuse_price_category(self, requests_mock):
        connector = EMSScheduleConnector()
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

        EMSStocks(
            connector=connector,
            venue_provider=venue_provider,
            site=connector.get_schedules().sites[0],
        ).synchronize()
        EMSStocks(
            connector=connector,
            venue_provider=venue_provider,
            site=connector.get_schedules().sites[0],
        ).synchronize()

        created_price_category = offers_models.PriceCategory.query.all()
        assert len(created_price_category) == 2

    def should_create_offer_with_correct_thumb(self, requests_mock):
        connector = EMSScheduleConnector()
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=poster)

        ems_stocks = EMSStocks(
            connector=connector,
            venue_provider=venue_provider,
            site=connector.get_schedules().sites[1],
        )
        ems_stocks.synchronize()

        created_offer = offers_models.Offer.query.one()
        assert (
            created_offer.image.url
            == f"http://localhost/storage/thumbs/mediations/{humanize(created_offer.activeMediation.id)}"
        )
        assert len(created_offer.mediations) == 1

    def should_create_offer_even_if_thumb_is_incorrect(self, requests_mock):
        connector = EMSScheduleConnector()
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        # Image that should raise a `pcapi.core.offers.exceptions.UnidentifiedImage`
        file_path = Path(tests.__path__[0]) / "files" / "mouette_fake_jpg.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=poster)

        ems_stocks = EMSStocks(
            connector=connector,
            venue_provider=venue_provider,
            site=connector.get_schedules().sites[1],
        )
        ems_stocks.synchronize()

        created_offer = offers_models.Offer.query.one()
        assert len(created_offer.mediations) == 0

    def test_handle_error_on_movie_poster(self, requests_mock):
        connector = EMSScheduleConnector()
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", status_code=404)

        ems_stocks = EMSStocks(
            connector=connector,
            venue_provider=venue_provider,
            site=connector.get_schedules().sites[1],
        )
        ems_stocks.synchronize()

        created_offer = offers_models.Offer.query.one()
        assert created_offer.image is None

    def test_successive_version_syncs(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/311D01C8/600/HIJIC.jpg", content=bytes())
        requests_mock.get("https://fake_url.com?version=86400", json=fixtures.DATA_VERSION_86400)

        ems_provider = get_provider_by_local_class("EMSStocks")

        ormeaux_venue = offerers_factories.VenueFactory(
            bookingEmail="ormeaux-booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ormeaux_venue_provider = providers_factories.VenueProviderFactory(
            venue=ormeaux_venue, provider=ems_provider, venueIdAtOfferProvider="0063", isDuoOffers=False
        )
        ormeaux_cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=ormeaux_venue, provider=ems_provider, idAtProvider="0063"
        )
        ormeaux_cinema_detail = providers_factories.EMSCinemaDetailsFactory(
            cinemaProviderPivot=ormeaux_cinema_provider_pivot
        )

        ems_cine_venue = offerers_factories.VenueFactory(
            bookingEmail="seyne-sur-mer-booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_cine_venue_provider = providers_factories.VenueProviderFactory(
            venue=ems_cine_venue, provider=ems_provider, venueIdAtOfferProvider="9997", isDuoOffers=True
        )
        ems_cine_cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=ems_cine_venue, provider=ems_provider, idAtProvider="9997"
        )
        ems_cine_cinema_detail = providers_factories.EMSCinemaDetailsFactory(
            cinemaProviderPivot=ems_cine_cinema_provider_pivot
        )

        # Everything is in place, so let’s first try an initial synchronization which will populate some data.
        # Day one
        synchronize_ems_venue_providers()
        self._assert_seyne_sur_mer_initial_sync(
            ems_cine_venue,
            ems_cine_venue_provider,
            ems_cine_cinema_detail,
            86400,
        )
        self._assert_ormeaux_initial_sync(
            ormeaux_venue,
            ormeaux_venue_provider,
            ormeaux_cinema_detail,
            86400,
        )
        # Our day one synchronization occured well, we now have some data.

        # Day two
        # Let’s try to retrieve some additionnal data that were added by our provider during the night
        synchronize_ems_venue_providers(from_last_version=True)
        # Nothing should change for this VenueProvider, except for the sync version, as there is no additional data to handle for it
        self._assert_seyne_sur_mer_initial_sync(
            ems_cine_venue,
            ems_cine_venue_provider,
            ems_cine_cinema_detail,
            172800,
        )
        # However, for this one, a new movie and session is available, let's check it !
        self._assert_ormeaux_version_sync(
            ormeaux_venue,
            ormeaux_venue_provider,
            ormeaux_cinema_detail,
            172800,
        )

    def _assert_ormeaux_initial_sync(
        self,
        venue: Venue,
        venue_provider: providers_models.VenueProvider,
        cinema_detail: providers_models.EMSCinemaDetails,
        version: int,
    ):
        created_offers = offers_models.Offer.query.filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        created_stocks = (
            offers_models.Stock.query.filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            offers_models.PriceCategory.query.filter(
                offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers)
            )
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            offers_models.PriceCategoryLabel.query.filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 1
        assert len(created_stocks) == 1
        assert len(created_price_categories) == 1
        assert len(created_price_categories_labels) == 1

        assert created_offers[0].name == "Mon voisin Totoro"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert (
            created_offers[0].description
            == "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro."
        )

        assert created_offers[0].durationMinutes == 87
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "ormeaux-booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"
        assert not created_offers[0].isDuo

        assert not created_stocks[0].quantity
        assert created_stocks[0].price == Decimal("7.00")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 7, 27, 8)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 7, 27, 8)
        assert created_stocks[0].priceCategory.price == Decimal("7.00")
        assert created_stocks[0].priceCategory.label == "Tarif pass Culture 7€"
        assert created_stocks[0].features == ["VF"]

        # Ensuring we are keeping tracks of current version of our stocks
        assert cinema_detail.lastVersion == version

    def _assert_seyne_sur_mer_initial_sync(
        self,
        venue: Venue,
        venue_provider: providers_models.VenueProvider,
        cinema_detail: providers_models.EMSCinemaDetails,
        version: int,
    ):
        created_offers = offers_models.Offer.query.filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        created_stocks = (
            offers_models.Stock.query.filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            offers_models.PriceCategory.query.filter(
                offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers)
            )
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            offers_models.PriceCategoryLabel.query.filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 2

        assert created_offers[0].name == "Spider-Man : Across the Spider-Verse"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert (
            created_offers[0].description
            == "Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus."
        )

        assert created_offers[0].durationMinutes == 141
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "seyne-sur-mer-booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"
        assert created_offers[0].isDuo

        assert not created_stocks[0].quantity
        assert created_stocks[0].price == Decimal("7.15")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 7, 11, 8)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 7, 11, 8)
        assert created_stocks[0].priceCategory.price == Decimal("7.15")
        assert created_stocks[0].priceCategory.label == "Tarif pass Culture 7.15€"
        assert created_stocks[0].features == ["VF", "3D"]

        assert not created_stocks[1].quantity
        assert created_stocks[1].price == Decimal("7.15")
        assert created_stocks[1].dateCreated
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 7, 11, 10, 30)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 7, 11, 10, 30)
        assert created_stocks[1].priceCategory.price == Decimal("7.15")
        assert created_stocks[1].priceCategory.label == "Tarif pass Culture 7.15€"
        assert created_stocks[1].features == ["VF", "3D"]

        assert created_offers[1].name == "Transformers : Rise of the Beasts"
        assert created_offers[1].venue == venue_provider.venue
        assert (
            created_offers[1].description
            == "Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons."
        )

        assert created_offers[1].durationMinutes == 127
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].bookingEmail == "seyne-sur-mer-booking@example.com"
        assert created_offers[1].withdrawalDetails == "Modalité de retrait"
        assert created_offers[1].isDuo

        assert not created_stocks[2].quantity
        assert created_stocks[2].price == Decimal("5.15")
        assert created_stocks[2].dateCreated
        assert created_stocks[2].bookingLimitDatetime == datetime.datetime(2023, 7, 11, 8)
        assert created_stocks[2].beginningDatetime == datetime.datetime(2023, 7, 11, 8)
        assert created_stocks[2].priceCategory.price == Decimal("5.15")
        assert created_stocks[2].priceCategory.label == "Tarif pass Culture 5.15€"
        assert created_stocks[2].features == ["VF"]

        # Ensuring we are keeping tracks of current version of our stocks
        assert cinema_detail.lastVersion == version

    def _assert_seyne_sur_mer_initial_sync_based_on_product(
        self,
        venue: Venue,
        venue_provider: providers_models.VenueProvider,
        cinema_detail: providers_models.EMSCinemaDetails,
        version: int,
    ):
        created_offers = offers_models.Offer.query.filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        created_stocks = (
            offers_models.Stock.query.filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            offers_models.PriceCategory.query.filter(
                offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers)
            )
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            offers_models.PriceCategoryLabel.query.filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 2

        assert created_offers[0].name == "Produit allociné 1"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert created_offers[0].description == "Description du produit allociné 1"
        assert created_offers[0].durationMinutes == 111
        assert (
            created_offers[0].product
            == offers_models.Product.query.filter(offers_models.Product.extraData["allocineId"] == "269975").one()
        )

        assert created_offers[1].name == "Produit allociné 2"
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Description du produit allociné 2"
        assert created_offers[1].durationMinutes == 222
        assert (
            created_offers[1].product
            == offers_models.Product.query.filter(offers_models.Product.extraData["allocineId"] == "241065").one()
        )

    def _assert_ormeaux_version_sync(
        self,
        venue: Venue,
        venue_provider: providers_models.VenueProvider,
        cinema_detail: providers_models.EMSCinemaDetails,
        version: int,
    ):
        created_offers = offers_models.Offer.query.filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        created_stocks = (
            offers_models.Stock.query.filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            offers_models.PriceCategory.query.filter(
                offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers)
            )
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            offers_models.PriceCategoryLabel.query.filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 2
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 1

        assert created_offers[0].name == "Mon voisin Totoro"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddressId == venue_provider.venue.offererAddressId
        assert (
            created_offers[0].description
            == "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro."
        )

        assert created_offers[0].durationMinutes == 87
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "ormeaux-booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"

        assert not created_stocks[0].quantity
        assert created_stocks[0].price == Decimal("7.00")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 7, 27, 8)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 7, 27, 8)
        assert created_stocks[0].priceCategory.price == Decimal("7.00")
        assert created_stocks[0].priceCategory.label == "Tarif pass Culture 7€"
        assert created_stocks[0].features == ["VF"]

        assert not created_stocks[1].quantity
        assert created_stocks[1].price == Decimal("7.00")
        assert created_stocks[1].dateCreated
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 8, 14, 19)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 8, 14, 19)
        assert created_stocks[1].priceCategory.price == Decimal("7.00")
        assert created_stocks[1].priceCategory.label == "Tarif pass Culture 7€"
        assert created_stocks[1].features == ["VO"]

        assert created_offers[1].name == "Joker"
        assert created_offers[1].venue == venue_provider.venue
        assert (
            created_offers[1].description
            == "Dans les années 1980, à Gotham City, Arthur Fleck, un humoriste de stand‐up raté, bascule dans la folie et devient le Joker."
        )

        assert created_offers[1].durationMinutes == 122
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].bookingEmail == "ormeaux-booking@example.com"
        assert created_offers[1].withdrawalDetails == "Modalité de retrait"

        # Ensuring we are keeping tracks of current version of our stocks
        assert cinema_detail.lastVersion == version

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


class EMSSyncSitesTest:
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_existing_up_to_date_sync_does_nothing(self, job_mocked, requests_mock, db_session):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.SITES_DATA_VERSION_0)
        ems_provider = get_provider_by_local_class("EMSStocks")

        oceanic = offerers_factories.VenueFactory(
            bookingEmail="oceanic-booking@example.com", withdrawalDetails="Modalité de retrait", siret="33069874700160"
        )
        providers_factories.VenueProviderFactory(venue=oceanic, provider=ems_provider, venueIdAtOfferProvider="0661")
        oceanic_cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=oceanic, provider=ems_provider, idAtProvider="0661"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=oceanic_cinema_provider_pivot)

        pavillon_bleu = offerers_factories.VenueFactory(
            bookingEmail="pavillon-bleu-booking@example.com",
            withdrawalDetails="Modalité de retrait",
            siret="21060105000011",
        )
        providers_factories.VenueProviderFactory(
            venue=pavillon_bleu, provider=ems_provider, venueIdAtOfferProvider="1048"
        )
        pavillon_bleu_cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=pavillon_bleu, provider=ems_provider, idAtProvider="1048"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=pavillon_bleu_cinema_provider_pivot)

        ems_cine = offerers_factories.VenueFactory(
            bookingEmail="ems-cine-booking@example.com", withdrawalDetails="Modalité de retrait", siret="775670664"
        )
        providers_factories.VenueProviderFactory(venue=ems_cine, provider=ems_provider, venueIdAtOfferProvider="9997")
        ems_cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=ems_cine, provider=ems_provider, idAtProvider="9997"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=ems_cinema_provider_pivot)

        palace = offerers_factories.VenueFactory(
            bookingEmail="palace-booking@example.com", withdrawalDetails="Modalité de retrait", siret="42465026500012"
        )
        providers_factories.VenueProviderFactory(venue=palace, provider=ems_provider, venueIdAtOfferProvider="1290")
        palace_cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=palace, provider=ems_provider, idAtProvider="1290"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=palace_cinema_provider_pivot)

        collect_elligible_venues_and_activate_ems_sync()

        venues = Venue.query.all()
        assert len(venues) == 4

        for venue in venues:
            assert len(venue.venueProviders) == 1
            assert len(venue.cinemaProviderPivot) == 1
            assert venue.venueProviders[0].providerId == ems_provider.id

        assert providers_models.EMSCinemaDetails.query.count() == 4
        job_mocked.assert_not_called()
        assert not history_models.ActionHistory.query.count()

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_existing_allocine_sync_is_set_to_ems(self, job_mocked, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.SITES_DATA_VERSION_0)
        ems_provider = get_provider_by_local_class("EMSStocks")
        allocine_provider = get_provider_by_local_class("AllocineStocks")

        oceanic = offerers_factories.VenueFactory(
            bookingEmail="oceanic-booking@example.com", withdrawalDetails="Modalité de retrait", siret="33069874700160"
        )
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory(
            venue=oceanic, provider=allocine_provider, venueIdAtOfferProvider="1111", internalId="P1025"
        )
        providers_factories.AllocinePivotFactory(venue=oceanic)

        collect_elligible_venues_and_activate_ems_sync()

        assert not providers_models.AllocinePivot.query.all()
        assert not providers_models.AllocineVenueProvider.query.all()

        venues = Venue.query.all()
        assert len(venues) == 1
        venue = venues[0]

        assert len(venue.venueProviders) == 1
        assert len(venue.cinemaProviderPivot) == 1
        venue_provider = venue.venueProviders[0]
        pivot = venue.cinemaProviderPivot[0]
        assert venue_provider.providerId == ems_provider.id
        assert venue_provider.isActive == True
        assert venue_provider.venueId == venue.id
        assert venue_provider.venueIdAtOfferProvider == "0661"
        assert pivot.idAtProvider == "0661"
        assert providers_models.EMSCinemaDetails.query.count() == 1

        job_mocked.assert_called_once_with(allocine_venue_provider.venueId, allocine_venue_provider.providerId, False)
        assert history_models.ActionHistory.query.count()

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_we_have_knowledge_of_available_venue_that_doesnt_exists_on_our_side(
        self, job_mocked, requests_mock, caplog
    ):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.SITES_DATA_VERSION_0)

        with caplog.at_level(logging.WARNING):
            collect_elligible_venues_and_activate_ems_sync()

        assert len(caplog.records) == 4

        for log in caplog.records:
            assert "Fail to find this venue" in log.msg
            assert log.extra["venue_siret"] in ["775670664", "42465026500012", "33069874700160", "21060105000011"]
            assert log.extra["venue_name"] in ["Océanic", "Le Pavillon Bleu", "Ems Cine", "Palace"]

        assert Venue.query.count() == 0
        job_mocked.assert_not_called()
        assert not history_models.ActionHistory.query.count()

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_we_dont_reactivate_ems_sync_that_was_deactivate_on_purpose(self, job_mocked, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.SITES_DATA_VERSION_0)
        ems_provider = get_provider_by_local_class("EMSStocks")

        # EMS sync deactivate on purpose by a pro
        oceanic = offerers_factories.VenueFactory(
            bookingEmail="oceanic-booking@example.com", withdrawalDetails="Modalité de retrait", siret="11111111111"
        )
        providers_factories.VenueProviderFactory(
            venue=oceanic, provider=ems_provider, venueIdAtOfferProvider="1111", isActive=False
        )
        providers_factories.CinemaProviderPivotFactory(venue=oceanic, provider=ems_provider, idAtProvider="1111")

        collect_elligible_venues_and_activate_ems_sync()

        venues = Venue.query.all()
        assert len(venues) == 1
        venue = venues[0]

        assert len(venue.venueProviders) == 1
        deactivated_venue_provider = venue.venueProviders[0]

        assert deactivated_venue_provider.providerId == ems_provider.id
        assert deactivated_venue_provider.isActive == False
        job_mocked.assert_not_called()
        assert not history_models.ActionHistory.query.count()

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_sync_is_not_activated_on_venue_without_existing_allocine_sync(self, job_mocked, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.SITES_DATA_VERSION_0)

        # Available venue for sync but without existing allocine sync and therefor without allocine_id (we can’t match the venue on our side)
        offerers_factories.VenueFactory(
            bookingEmail="oceanic-booking@example.com", withdrawalDetails="Modalité de retrait", siret="33069874700160"
        )

        collect_elligible_venues_and_activate_ems_sync()

        venues = Venue.query.all()
        assert len(venues) == 1
        venue = venues[0]

        assert len(venue.venueProviders) == 0
        assert len(venue.cinemaProviderPivot) == 0
        job_mocked.assert_not_called()
        assert not history_models.ActionHistory.query.count()

    @override_features(LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC=True)
    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.connectors.googledrive.TestingBackend.create_file")
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_that_we_successfully_log_available_cinemas_that_dont_have_sync_yet(
        self, job_mocked, mock_gdrive_create_file, requests_mock
    ):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.SITES_DATA_VERSION_0)

        collect_elligible_venues_and_activate_ems_sync()

        assert providers_models.EMSCinemaDetails.query.count() == 0
        job_mocked.assert_not_called()
        assert not history_models.ActionHistory.query.count()
        file_name = f"{datetime.datetime.today().date().isoformat()}.csv"
        with open(f"/tmp/{file_name}", "r", encoding="utf-8") as f:
            reader = DictReader(f)

            for line, cinema in zip(
                sorted(reader, key=lambda r: r["ems_id"]),
                sorted(fixtures.SITES_DATA_VERSION_0["sites"], key=lambda l: l["id"]),
            ):
                assert line == {
                    "siret": cinema["siret"],
                    "ems_id": cinema["id"],
                    "allocine_id": cinema["allocine_id"],
                    "cinema": cinema["name"],
                    "address": cinema["address"],
                    "zip_code": cinema["zip_code"],
                    "city": cinema["city"],
                }

        mock_gdrive_create_file.assert_called_once_with(
            settings.EMS_GOOGLE_DRIVE_FOLDER, file_name, Path(f"/tmp/{file_name}")
        )
