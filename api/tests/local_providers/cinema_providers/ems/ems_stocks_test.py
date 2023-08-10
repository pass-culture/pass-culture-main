from base64 import b64decode
import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from pcapi import settings
from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
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
            bookingEmail="seyne-sur-mer-booking@example.com", withdrawalDetails="Modalité de retrait"
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

        self._assert_seyne_sur_mer_initial_sync(venue, venue_provider, cinema_detail, 86400)

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

    def should_create_product_with_correct_thumb(self, requests_mock):
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

        created_product = offers_models.Product.query.one()
        assert created_product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(created_product.id)}"
        assert created_product.thumbCount == 1

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
            venue=ormeaux_venue, provider=ems_provider, venueIdAtOfferProvider="0063"
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
            venue=ems_cine_venue, provider=ems_provider, venueIdAtOfferProvider="9997"
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
        created_products = (
            offers_models.Product.query.filter_by(idAtProviders="CDFG5%EMS").order_by(offers_models.Product.id).all()
        )
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
        assert len(created_products) == 1
        assert len(created_stocks) == 1
        assert len(created_price_categories) == 1
        assert len(created_price_categories_labels) == 1

        assert created_offers[0].name == "Mon voisin Totoro"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert (
            created_offers[0].description
            == "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro."
        )

        assert created_offers[0].durationMinutes == 87
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "ormeaux-booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"

        assert created_products[0].name == "Mon voisin Totoro"
        assert (
            created_products[0].description
            == "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro."
        )
        assert created_products[0].durationMinutes == 87
        assert created_products[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert not created_stocks[0].quantity
        assert created_stocks[0].price == Decimal("7.00")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 7, 27, 10)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 7, 27, 10)
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
        created_products = (
            offers_models.Product.query.filter(offers_models.Product.idAtProviders.in_(["FGMSE%EMS", "SHJRH%EMS"]))
            .order_by(offers_models.Product.id)
            .all()
        )
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
        assert created_offers[0].bookingEmail == "seyne-sur-mer-booking@example.com"
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
        assert created_offers[1].bookingEmail == "seyne-sur-mer-booking@example.com"
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
        assert cinema_detail.lastVersion == version

    def _assert_ormeaux_version_sync(
        self,
        venue: Venue,
        venue_provider: providers_models.VenueProvider,
        cinema_detail: providers_models.EMSCinemaDetails,
        version: int,
    ):
        created_offers = offers_models.Offer.query.filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        created_products = (
            offers_models.Product.query.filter(offers_models.Product.idAtProviders.in_(["CDFG5%EMS", "HIJIC%EMS"]))
            .order_by(offers_models.Product.id)
            .all()
        )
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
        assert len(created_products) == 2
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 1

        assert created_offers[0].name == "Mon voisin Totoro"
        assert created_offers[0].product == created_products[0]
        assert created_offers[0].venue == venue_provider.venue
        assert (
            created_offers[0].description
            == "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro."
        )

        assert created_offers[0].durationMinutes == 87
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "ormeaux-booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"

        assert created_products[0].name == "Mon voisin Totoro"
        assert (
            created_products[0].description
            == "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro."
        )
        assert created_products[0].durationMinutes == 87
        assert created_products[0].subcategoryId == subcategories.SEANCE_CINE.id

        assert not created_stocks[0].quantity
        assert created_stocks[0].price == Decimal("7.00")
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].bookingLimitDatetime == datetime.datetime(2023, 7, 27, 10)
        assert created_stocks[0].beginningDatetime == datetime.datetime(2023, 7, 27, 10)
        assert created_stocks[0].priceCategory.price == Decimal("7.00")
        assert created_stocks[0].priceCategory.label == "Tarif pass Culture 7€"
        assert created_stocks[0].features == ["VF"]

        assert not created_stocks[1].quantity
        assert created_stocks[1].price == Decimal("7.00")
        assert created_stocks[1].dateCreated
        assert created_stocks[1].bookingLimitDatetime == datetime.datetime(2023, 8, 14, 21)
        assert created_stocks[1].beginningDatetime == datetime.datetime(2023, 8, 14, 21)
        assert created_stocks[1].priceCategory.price == Decimal("7.00")
        assert created_stocks[1].priceCategory.label == "Tarif pass Culture 7€"
        assert created_stocks[1].features == ["VO"]

        assert created_offers[1].name == "Joker"
        assert created_offers[1].product == created_products[1]
        assert created_offers[1].venue == venue_provider.venue
        assert (
            created_offers[1].description
            == "Dans les années 1980, à Gotham City, Arthur Fleck, un humoriste de stand‐up raté, bascule dans la folie et devient le Joker."
        )

        assert created_offers[1].durationMinutes == 122
        assert created_offers[1].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[1].bookingEmail == "ormeaux-booking@example.com"
        assert created_offers[1].withdrawalDetails == "Modalité de retrait"

        assert created_products[1].name == "Joker"
        assert (
            created_products[1].description
            == "Dans les années 1980, à Gotham City, Arthur Fleck, un humoriste de stand‐up raté, bascule dans la folie et devient le Joker."
        )
        assert created_products[1].durationMinutes == 122
        assert created_products[1].subcategoryId == subcategories.SEANCE_CINE.id

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
