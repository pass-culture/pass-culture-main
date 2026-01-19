import datetime
import logging
from base64 import b64decode
from decimal import Decimal
from pathlib import Path
from typing import Type
from unittest import mock

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.etls.ems_etl import EMSExtractTransformLoadProcess
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.provider_manager import synchronize_ems_venue_providers
from pcapi.models import db
from pcapi.utils.requests import exceptions as requests_exception

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

    def execute_import(
        self,
        ProcessClass: Type[EMSExtractTransformLoadProcess] | Type[EMSStocks],
        venue_provider,
    ) -> None:
        if ProcessClass == EMSStocks:
            synchronize_ems_venue_providers()
        else:
            ProcessClass(venue_provider=venue_provider).execute()

    @time_machine.travel(datetime.datetime(2023, 2, 12), tick=False)
    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def should_fill_and_create_offer_and_stock_information_for_each_movie_if_product_doesnt_exist(
        self, ProcessClass, requests_mock
    ):
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

        assert db.session.query(offers_models.Product).count() == 0

        self.execute_import(ProcessClass, venue_provider)

        self._assert_seyne_sur_mer_initial_sync(venue, venue_provider, cinema_detail, 86400)

    # Not tested with `EMSExtractTransformLoadProcess` because it is logic that was implemented for a very specific Festival
    @mock.patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_RATE", Decimal("4.0"))
    @mock.patch("pcapi.local_providers.movie_festivals.constants.FESTIVAL_NAME", "My awesome festival")
    @mock.patch("pcapi.local_providers.movie_festivals.api.should_apply_movie_festival_rate")
    def should_update_stock_with_movie_festival_rate(self, should_apply_movie_festival_rate_mock, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0_MOVIE_FESTIVAL)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        venue = offerers_factories.VenueFactory(
            bookingEmail="seyne-sur-mer-booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        ems_provider = get_provider_by_local_class("EMSStocks")
        providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997", isDuoOffers=True
        )
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=ems_provider, idAtProvider="9997"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        assert db.session.query(offers_models.Product).count() == 0
        should_apply_movie_festival_rate_mock.return_value = True

        synchronize_ems_venue_providers()

        created_offer = db.session.query(offers_models.Offer).one()
        created_stock = db.session.query(offers_models.Stock).one()

        should_apply_movie_festival_rate_mock.assert_called_with(
            created_offer.id, created_stock.beginningDatetime.date()
        )

        assert created_stock.price == Decimal("4.0")
        assert created_stock.priceCategory.price == Decimal("4.0")
        assert created_stock.priceCategory.priceCategoryLabel.label == "My awesome festival"

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def should_fill_and_create_offer_and_stock_information_for_each_movie_based_on_product(
        self, ProcessClass, requests_mock
    ):
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

        self.execute_import(ProcessClass, venue_provider)

        self._assert_seyne_sur_mer_initial_sync_based_on_product(venue, venue_provider, cinema_detail, 86400)

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def should_create_offers_event_if_address_info_are_missing(self, ProcessClass, requests_mock):
        DATA_VERSION_0_WITHOUT_ADDRESS_INFO = {
            "sites": [
                {
                    "id": "9997",
                    "allocine_id": "Z9997",
                    "name": "Ems Cine",
                    "time_zone": "Europe/Paris",
                    "events": [
                        {
                            "id": "SHJRH",
                            "allocine_id": 269975,
                            "title": "Spider-Man : Across the Spider-Verse",
                            "director": "Joaquim Dos Santos, Justin K. Thompson, Kemp Powers",
                            "release_date": "20230531",
                            "synopsis": "Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus.",
                            "duration": 141,
                            "bill_url": "https://example.com/FR/poster/5F988F1C/120/SHJRH.jpg",
                            "sessions": [
                                {
                                    "id": "999700079243",
                                    "date": "202307111000",
                                    "features": ["video_3d", "vf", "disabled_access"],
                                    "hall_id": 5,
                                    "hall_name": "Salle 5",
                                    "pass_culture_price": 7.15,
                                },
                                {
                                    "id": "999700079244",
                                    "date": "202307111230",
                                    "features": ["video_3d", "vf", "disabled_access"],
                                    "hall_id": 5,
                                    "hall_name": "Salle 5",
                                    "pass_culture_price": 7.15,
                                },
                            ],
                        },
                        {
                            "id": "FGMSE",
                            "allocine_id": 241065,
                            "title": "Transformers : Rise of the Beasts",
                            "director": "Steven Caple Jr.",
                            "release_date": "20230607",
                            "synopsis": "Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons.",
                            "duration": 127,
                            "bill_url": "https://example.com/FR/poster/D7C57D16/120/FGMSE.jpg",
                            "sessions": [
                                {
                                    "id": "999700079212",
                                    "date": "202307111000",
                                    "features": ["video_4k", "audio_dtsx", "vf", "disabled_access"],
                                    "hall_id": 6,
                                    "hall_name": "Salle 6",
                                    "pass_culture_price": 5.15,
                                },
                            ],
                        },
                    ],
                },
                {
                    "id": "0063",
                    "allocine_id": "P1209",
                    "name": "Les Ormeaux",
                    "address": "17-26 Rue des Echolères (parking des Ormeaux - place du marché)",
                    "zip_code": "85520",
                    "city": "Jard-sur-Mer",
                    "time_zone": "Europe/Paris",
                    "events": [
                        {
                            "id": "CDFG5",
                            "allocine_id": 269976,
                            "title": "Mon voisin Totoro",
                            "director": "Hayao Miyazaki",
                            "release_date": "19991208",
                            "synopsis": "Mei, 4 ans, et Satsuki, 10 ans, s’installent à la campagne avec leur père pour se rapprocher de l’hôpital où séjourne leur mère. Elles découvrent la nature tout autour de la maison et, surtout, l’existence d’animaux étranges et merveilleux, les Totoros, avec qui elles deviennent très amies. Un jour, alors que Satsuki et Mei attendent le retour de leur mère, elles apprennent que sa sortie de l’hôpital a été repoussée. Mei décide alors d’aller lui rendre visite seule. Satsuki et les gens du village la recherchent en vain. Désespérée, Satsuki va finalement demander de l’aide à son voisin Totoro.",
                            "duration": 87,
                            "bill_url": "https://example.com/FR/poster/982D31BE/120/CDFG5.jpg",
                            "sessions": [
                                {
                                    "id": "006300006867",
                                    "date": "202307271000",
                                    "features": ["vf"],
                                    "hall_id": 1,
                                    "hall_name": "Salle 1",
                                    "pass_culture_price": 7,
                                }
                            ],
                        },
                    ],
                },
            ],
            "version": 86400,
        }
        requests_mock.get("https://fake_url.com?version=0", json=DATA_VERSION_0_WITHOUT_ADDRESS_INFO)
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

        self.execute_import(ProcessClass, venue_provider)

        self._assert_seyne_sur_mer_initial_sync_based_on_product(venue, venue_provider, cinema_detail, 86400)

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def should_update_finance_event_when_stock_beginning_datetime_is_updated(self, ProcessClass, requests_mock):
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
            self.execute_import(ProcessClass, venue_provider)
        mock_update_finance_event.assert_not_called()

        # synchronize with show with same date
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            self.execute_import(ProcessClass, venue_provider)
        mock_update_finance_event.assert_not_called()

        # synchronize with show with new date
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0_WITH_NEW_DATE)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        # targeting specific stock whith idAtprovider
        stock = (
            db.session.query(offers_models.Stock).where(offers_models.Stock.idAtProviders.like("%999700079243")).first()
        )
        assert stock is not None
        event_created = create_finance_event_to_update(stock=stock, venue_provider=venue_provider)
        last_pricingOrderingDate = event_created.pricingOrderingDate
        self.execute_import(ProcessClass, venue_provider)
        assert event_created.pricingOrderingDate != last_pricingOrderingDate

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def should_reuse_price_category(self, ProcessClass, requests_mock):
        connector = EMSScheduleConnector()
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)
        requests_mock.get("https://fake_url.com?version=86400", json=fixtures.DATA_VERSION_0)
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
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        if ProcessClass == EMSStocks:
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
        else:
            EMSExtractTransformLoadProcess(venue_provider).execute()
            EMSExtractTransformLoadProcess(venue_provider).execute()

        created_price_category = db.session.query(offers_models.PriceCategory).all()
        assert len(created_price_category) == 2

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def test_should_create_product_mediation(self, ProcessClass, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=ems_provider, idAtProvider="0063"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=poster)

        self.execute_import(ProcessClass, venue_provider)

        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.image.url == created_offer.product.productMediations[0].url

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def test_should_not_create_product_mediation(self, ProcessClass, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=ems_provider, idAtProvider="0063"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        product = offers_factories.EventProductFactory(
            name="Mon voisin Totoro",
            extraData=offers_models.OfferExtraData(allocineId=269976),
        )
        offers_factories.ProductMediationFactory(product=product, imageType=offers_models.ImageType.POSTER)

        get_image_adapter = requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg")

        self.execute_import(ProcessClass, venue_provider)

        assert get_image_adapter.last_request == None

    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def should_create_offer_even_if_thumb_is_incorrect(self, ProcessClass, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=ems_provider, idAtProvider="0063"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        # Image that should raise a `pcapi.core.offers.exceptions.UnidentifiedImage`
        file_path = Path(tests.__path__[0]) / "files" / "mouette_fake_jpg.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=poster)

        self.execute_import(ProcessClass, venue_provider)

        created_offer = db.session.query(offers_models.Offer).one()
        assert len(created_offer.mediations) == 0

    @pytest.mark.parametrize(
        "get_adapter_error_params",
        [
            # invalid responses
            {"status_code": 404},
            {"status_code": 502},
            # unexpected errors
            {"exc": requests_exception.ReadTimeout},
            {"exc": requests_exception.ConnectTimeout},
        ],
    )
    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def test_handle_error_on_movie_poster(self, ProcessClass, get_adapter_error_params, requests_mock, caplog):
        requests_mock.get("https://fake_url.com?version=0", json=fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=ems_provider, idAtProvider="0063"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", **get_adapter_error_params)

        with caplog.at_level(logging.WARNING):
            self.execute_import(ProcessClass, venue_provider)

        created_offer = db.session.query(offers_models.Offer).one()
        assert created_offer.image is None

        assert len(caplog.records) >= 1

        last_record = caplog.records.pop()
        assert last_record.message == "Could not fetch movie poster"
        assert last_record.extra == {
            "client": "EMSScheduleConnector",
            "url": "https://example.com/FR/poster/982D31BE/600/CDFG5.jpg",
        }

    @time_machine.travel(datetime.datetime(2023, 2, 12), tick=False)
    @pytest.mark.parametrize("ProcessClass", [EMSStocks, EMSExtractTransformLoadProcess])
    def test_successive_version_syncs(self, ProcessClass, requests_mock):
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
        if ProcessClass == EMSStocks:
            synchronize_ems_venue_providers()
        else:
            ProcessClass(ormeaux_venue_provider).execute()
            ProcessClass(ems_cine_venue_provider).execute()
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
        if ProcessClass == EMSStocks:
            synchronize_ems_venue_providers(from_last_version=True)
        else:
            ProcessClass(ormeaux_venue_provider, from_last_version=True).execute()
            ProcessClass(ems_cine_venue_provider, from_last_version=True).execute()

        # Nothing should change for this VenueProvider, except for the sync version, as there is no additional data to handle for it
        seyne_sur_mer_expected_version = 172800
        if (
            ProcessClass == EMSExtractTransformLoadProcess
        ):  # # We don't update the last version if there's no returned data by the API in the new process
            seyne_sur_mer_expected_version = 86400
        self._assert_seyne_sur_mer_initial_sync(
            ems_cine_venue,
            ems_cine_venue_provider,
            ems_cine_cinema_detail,
            seyne_sur_mer_expected_version,
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
        created_offers = (
            db.session.query(offers_models.Offer).filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        )
        created_stocks = (
            db.session.query(offers_models.Stock)
            .filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            db.session.query(offers_models.PriceCategory)
            .filter(offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 1
        assert len(created_stocks) == 1
        assert len(created_price_categories) == 1
        assert len(created_price_categories_labels) == 1

        assert created_offers[0].name == "Mon voisin Totoro"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddress == venue_provider.venue.offererAddress
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
        created_offers = (
            db.session.query(offers_models.Offer).filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        )
        created_stocks = (
            db.session.query(offers_models.Stock)
            .filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            db.session.query(offers_models.PriceCategory)
            .filter(offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 2

        assert created_offers[0].name == "Spider-Man : Across the Spider-Verse"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddress == venue_provider.venue.offererAddress
        assert (
            created_offers[0].description
            == "Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus."
        )

        assert created_offers[0].durationMinutes == 141
        assert created_offers[0].subcategoryId == subcategories.SEANCE_CINE.id
        assert created_offers[0].bookingEmail == "seyne-sur-mer-booking@example.com"
        assert created_offers[0].withdrawalDetails == "Modalité de retrait"
        assert created_offers[0].isDuo
        assert created_offers[0].publicationDatetime == datetime.datetime(2023, 2, 12, tzinfo=datetime.UTC)

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
        assert created_offers[1].publicationDatetime == datetime.datetime(2023, 2, 12, tzinfo=datetime.UTC)

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
        created_offers = (
            db.session.query(offers_models.Offer).filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        )
        created_stocks = (
            db.session.query(offers_models.Stock)
            .filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            db.session.query(offers_models.PriceCategory)
            .filter(offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 2
        assert len(created_stocks) == 3
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 2

        assert created_offers[0].name == "Produit allociné 1"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddress == venue_provider.venue.offererAddress
        assert created_offers[0].description == "Description du produit allociné 1"
        assert created_offers[0].durationMinutes == 111
        assert (
            created_offers[0].product
            == db.session.query(offers_models.Product)
            .filter(offers_models.Product.extraData.op("->")("allocineId") == "269975")
            .one()
        )

        assert created_offers[1].name == "Produit allociné 2"
        assert created_offers[1].venue == venue_provider.venue
        assert created_offers[1].description == "Description du produit allociné 2"
        assert created_offers[1].durationMinutes == 222
        assert (
            created_offers[1].product
            == db.session.query(offers_models.Product)
            .filter(offers_models.Product.extraData.op("->")("allocineId") == "241065")
            .one()
        )

    def _assert_ormeaux_version_sync(
        self,
        venue: Venue,
        venue_provider: providers_models.VenueProvider,
        cinema_detail: providers_models.EMSCinemaDetails,
        version: int,
    ):
        created_offers = (
            db.session.query(offers_models.Offer).filter_by(venueId=venue.id).order_by(offers_models.Offer.id).all()
        )
        created_stocks = (
            db.session.query(offers_models.Stock)
            .filter(offers_models.Stock.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.Stock.id)
            .all()
        )
        created_price_categories = (
            db.session.query(offers_models.PriceCategory)
            .filter(offers_models.PriceCategory.offerId.in_(offer.id for offer in created_offers))
            .order_by(offers_models.PriceCategory.id)
            .all()
        )
        created_price_categories_labels = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter_by(venueId=venue.id)
            .order_by(offers_models.PriceCategoryLabel.id)
            .all()
        )

        assert len(created_offers) == 2
        assert len(created_stocks) == 2
        assert len(created_price_categories) == 2
        assert len(created_price_categories_labels) == 1

        assert created_offers[0].name == "Mon voisin Totoro"
        assert created_offers[0].venue == venue_provider.venue
        assert created_offers[0].offererAddress == venue_provider.venue.offererAddress
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
