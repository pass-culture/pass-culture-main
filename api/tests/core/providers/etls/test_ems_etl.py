import datetime
import decimal
import logging
import pathlib
from unittest import mock

import pytest
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.connectors.ems import ems_serializers
from pcapi.core.categories import subcategories
from pcapi.core.providers.etls.ems_etl import EMSExtractTransformLoadProcess
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.search import models as search_models
from pcapi.models import db
from pcapi.utils import requests

import tests
from tests.local_providers.provider_test_utils import create_finance_event_to_update

from . import ems_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class EMSExtractTransformLoadProcessTest:
    def setup_cinema_objects(self):
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue = offerers_factories.VenueFactory(
            bookingEmail="seyne-sur-mer-booking@example.com", withdrawalDetails="Modalité de retrait"
        )
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue, provider=ems_provider, venueIdAtOfferProvider="9997", isDuoOffers=True
        )
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=ems_provider, idAtProvider="9997"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        return venue_provider

    def setup_requests_mock(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

    def test_execute_should_raise_inactive_provider(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)
        venue_provider.provider.isActive = False
        etl_process = EMSExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveProvider):
            etl_process.execute()

    def test_execute_should_raise_inactive_venue_provider_provider(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)
        venue_provider.isActive = False
        etl_process = EMSExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveVenueProvider):
            etl_process.execute()

    def test_should_log_and_raise_error_if_extract_fails(self, caplog, requests_mock):
        venue_provider = self.setup_cinema_objects()
        requests_mock.get("https://fake_url.com?version=0", exc=requests.exceptions.ConnectTimeout("so slow"))

        etl_process = EMSExtractTransformLoadProcess(venue_provider)

        with caplog.at_level(logging.WARNING):
            with pytest.raises(requests.exceptions.ConnectTimeout):
                etl_process.execute()

        assert len(caplog.records) >= 1
        last_record = caplog.records[-1]
        assert last_record.message == "[EMSExtractTransformLoadProcess] Step 1 - Extract failed"
        assert last_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {"exc": "ConnectTimeout", "msg": "so slow"},
        }

    def test_extract_should_return_raw_results(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)

        etl_process = EMSExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        assert extract_result == {
            "site_with_events": ems_serializers.SiteWithEvents(
                id="9997",
                name="Ems Cine",
                address="Monnaie-Services, 334 rue du Luxembourg",
                zip_code="83500",
                city="La seyne sur mer",
                events=[
                    ems_serializers.Event(
                        id="SHJRH",
                        allocine_id=269975,
                        title="Spider-Man : Across the Spider-Verse",
                        director="Joaquim Dos Santos, Justin K. Thompson, Kemp Powers",
                        synopsis="Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus.",
                        bill_url="https://example.com/FR/poster/5F988F1C/120/SHJRH.jpg",
                        duration=141,
                        sessions=[
                            ems_serializers.Session(
                                id="999700079243",
                                date="202307111000",
                                features=["video_3d", "vf", "disabled_access"],
                                pass_culture_price=decimal.Decimal("7.15"),
                            ),
                            ems_serializers.Session(
                                id="999700079244",
                                date="202307111230",
                                features=["video_3d", "vf", "disabled_access"],
                                pass_culture_price=decimal.Decimal("7.15"),
                            ),
                        ],
                    ),
                    ems_serializers.Event(
                        id="FGMSE",
                        allocine_id=241065,
                        title="Transformers : Rise of the Beasts",
                        director="Steven Caple Jr.",
                        synopsis="Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons.",
                        bill_url="https://example.com/FR/poster/D7C57D16/120/FGMSE.jpg",
                        duration=127,
                        sessions=[
                            ems_serializers.Session(
                                id="999700079212",
                                date="202307111000",
                                features=["video_4k", "audio_dtsx", "vf", "disabled_access"],
                                pass_culture_price=decimal.Decimal("5.15"),
                            )
                        ],
                    ),
                ],
            ),
            "version": 86400,
        }

    def test_transform_should_return_loadable_result(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        etl_process = EMSExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        transform_result = etl_process._transform(extract_result=extract_result)
        assert transform_result == [
            {
                "movie_uuid": f"SHJRH%{venue_id}%EMS",
                "movie_data": offers_models.Movie(
                    allocine_id="269975",
                    description="Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus.",
                    duration=141,
                    poster_url="https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg",  # /120/ -> /600/
                    visa=None,
                    title="Spider-Man : Across the Spider-Verse",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "stock_uuid": f"SHJRH%{venue_id}%EMS#999700079243",
                        "show_datetime": datetime.datetime(2023, 7, 11, 8, 0),  # date in naive UTC
                        "remaining_quantity": None,
                        "features": ["VF", "3D"],
                        "price": decimal.Decimal("7.15"),
                        "price_label": "Tarif pass Culture 7.15€",
                    },
                    {
                        "stock_uuid": f"SHJRH%{venue_id}%EMS#999700079244",
                        "show_datetime": datetime.datetime(2023, 7, 11, 10, 30),  # date in naive UTC
                        "remaining_quantity": None,
                        "features": ["VF", "3D"],
                        "price": decimal.Decimal("7.15"),
                        "price_label": "Tarif pass Culture 7.15€",
                    },
                ],
            },
            {
                "movie_uuid": f"FGMSE%{venue_id}%EMS",
                "movie_data": offers_models.Movie(
                    allocine_id="241065",
                    description="Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons.",
                    duration=127,
                    poster_url="https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg",  # /120/ -> /600/
                    visa=None,
                    title="Transformers : Rise of the Beasts",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "stock_uuid": f"FGMSE%{venue_id}%EMS#999700079212",
                        "show_datetime": datetime.datetime(2023, 7, 11, 8, 00),  # date in naive UTC
                        "remaining_quantity": None,
                        "features": ["VF"],
                        "price": decimal.Decimal("5.15"),
                        "price_label": "Tarif pass Culture 5.15€",
                    },
                ],
            },
        ]

    def test_transform_should_drop_movie_without_show(self, requests_mock, caplog):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0_WITHOUT_SESSIONS)

        etl_process = EMSExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        with caplog.at_level(logging.WARNING):
            transform_result = etl_process._transform(extract_result=extract_result)
        assert transform_result == []

        assert len(caplog.records) >= 1
        movie_without_show_record = caplog.records[-1]
        assert (
            movie_without_show_record.message == "[EMSExtractTransformLoadProcess] Step 2 - Movie does not have shows"
        )
        assert movie_without_show_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {
                "movie_uuid": f"FGMSE%{venue_id}%EMS",
                "movie_title": "Transformers : Rise of the Beasts",
                "allocine_id": "241065",
                "visa": None,
            },
        }

    @time_machine.travel(datetime.datetime(2023, 6, 12, 12, 41, 30), tick=False)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_execute_should_create_and_index_offer(self, async_index_offer_ids_mock, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        file_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster_venom = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=poster_venom)

        EMSExtractTransformLoadProcess(venue_provider).execute()

        offer_1 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"SHJRH%{venue_id}%EMS").one_or_none()
        offer_2 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"FGMSE%{venue_id}%EMS").one_or_none()

        assert offer_1
        assert offer_1.idAtProvider == f"SHJRH%{venue_id}%EMS"
        assert offer_1.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_1.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_1.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_1.publicationDatetime == datetime.datetime(2023, 6, 12, 12, 41, 30)
        assert offer_1.dateModifiedAtLastProvider == datetime.datetime(2023, 6, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_1.product
        assert offer_1.product.name == "Spider-Man : Across the Spider-Verse"
        assert offer_1.product.durationMinutes == 141
        assert (
            offer_1.product.description
            == "Après avoir retrouvé Gwen Stacy, Spider-Man, le sympathique héros originaire de Brooklyn, est catapulté à travers le Multivers, où il rencontre une équipe de Spider-Héros chargée d'en protéger l'existence. Mais lorsque les héros s'opposent sur la façon de gérer une nouvelle menace, Miles se retrouve confronté à eux et doit redéfinir ce que signifie être un héros afin de sauver les personnes qu'il aime le plus."
        )
        assert offer_1.product.extraData["allocineId"] == 269975
        assert offer_1.product.extraData.get("visa") == None
        assert len(offer_1.product.productMediations) == 1
        assert offer_1.product.productMediations[0].lastProvider == venue_provider.provider
        assert offer_1.product.productMediations[0].imageType == offers_models.ImageType.POSTER

        offer_1_stocks = offer_1.activeStocks
        assert len(offer_1_stocks) == 2
        offer_1_stock_1 = offer_1_stocks[0]
        assert offer_1_stock_1.idAtProviders == f"SHJRH%{venue_id}%EMS#999700079243"
        assert offer_1_stock_1.beginningDatetime == datetime.datetime(2023, 7, 11, 8, 0)
        assert offer_1_stock_1.bookingLimitDatetime == datetime.datetime(2023, 7, 11, 8, 0)
        assert offer_1_stock_1.dateModifiedAtLastProvider == datetime.datetime(2023, 6, 12, 12, 41, 30)
        assert offer_1_stock_1.features == ["VF", "3D"]
        assert offer_1_stock_1.quantity == None
        assert offer_1_stock_1.price == decimal.Decimal("7.15")
        assert offer_1_stock_1.priceCategory.price == decimal.Decimal("7.15")
        assert offer_1_stock_1.priceCategory.label == "Tarif pass Culture 7.15€"

        offer_1_stock_2 = offer_1_stocks[1]
        assert offer_1_stock_2.idAtProviders == f"SHJRH%{venue_id}%EMS#999700079244"
        assert offer_1_stock_2.beginningDatetime == datetime.datetime(2023, 7, 11, 10, 30)
        assert offer_1_stock_2.bookingLimitDatetime == datetime.datetime(2023, 7, 11, 10, 30)
        assert offer_1_stock_2.dateModifiedAtLastProvider == datetime.datetime(2023, 6, 12, 12, 41, 30)
        assert offer_1_stock_2.features == ["VF", "3D"]
        assert offer_1_stock_2.quantity == None
        assert offer_1_stock_2.price == decimal.Decimal("7.15")
        assert offer_1_stock_2.priceCategory.price == decimal.Decimal("7.15")
        assert offer_1_stock_2.priceCategory.label == "Tarif pass Culture 7.15€"

        assert offer_2
        assert offer_2.idAtProvider == f"FGMSE%{venue_id}%EMS"
        assert offer_2.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_2.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_2.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_2.publicationDatetime == datetime.datetime(2023, 6, 12, 12, 41, 30)
        assert offer_2.dateModifiedAtLastProvider == datetime.datetime(2023, 6, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_2.product
        assert offer_2.product.name == "Transformers : Rise of the Beasts"
        assert offer_2.product.durationMinutes == 127
        assert (
            offer_2.product.description
            == "Renouant avec l'action et le grand spectacle qui ont fait des premiers Transformers un phénomène mondial il y a 14 ans, Transformers : Rise of The Beasts transportera le public dans une aventure aux quatre coins du monde au coeur des années 1990. On y découvrira pour la première fois les Maximals, Predacons et Terrorcons rejoignant l'éternel combat entre les Autobots et les Decepticons."
        )
        assert offer_2.product.extraData["allocineId"] == 241065
        assert offer_2.product.extraData.get("visa") == None
        assert len(offer_2.product.productMediations) == 0

        offer_2_stocks = offer_2.activeStocks
        assert len(offer_2_stocks) == 1
        offer_2_stock_1 = offer_2_stocks[0]
        assert offer_2_stock_1.idAtProviders == f"FGMSE%{venue_id}%EMS#999700079212"
        assert offer_2_stock_1.beginningDatetime == datetime.datetime(2023, 7, 11, 8, 0)
        assert offer_2_stock_1.bookingLimitDatetime == datetime.datetime(2023, 7, 11, 8, 0)
        assert offer_2_stock_1.dateModifiedAtLastProvider == datetime.datetime(2023, 6, 12, 12, 41, 30)
        assert offer_2_stock_1.features == ["VF"]
        assert offer_2_stock_1.quantity == None
        assert offer_2_stock_1.price == decimal.Decimal("5.15")
        assert offer_2_stock_1.priceCategory.price == decimal.Decimal("5.15")
        assert offer_2_stock_1.priceCategory.label == "Tarif pass Culture 5.15€"

        async_index_offer_ids_mock.assert_called_once_with(
            set([offer_1.id, offer_2.id]),
            reason=search_models.IndexationReason.STOCK_UPDATE,
            log_extra={
                "source": "provider_api",
                "venue_id": venue_provider.venueId,
                "provider_id": venue_provider.providerId,
            },
        )

    def test_should_reuse_price_category(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())
        venue_provider = self.setup_cinema_objects()

        EMSExtractTransformLoadProcess(venue_provider).execute()
        EMSExtractTransformLoadProcess(venue_provider).execute()

        created_price_category = db.session.query(offers_models.PriceCategory).all()
        assert len(created_price_category) == 2

    def test_should_create_product_mediation(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)

        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venueIdAtOfferProvider="0063")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=ems_provider, idAtProvider="0063"
        )
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        file_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/982D31BE/600/CDFG5.jpg", content=poster)

        EMSExtractTransformLoadProcess(venue_provider).execute()

        created_offer = db.session.query(offers_models.Offer).one()

        assert created_offer.image.url == created_offer.product.productMediations[0].url

    def test_should_not_create_product_mediation(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)

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

        EMSExtractTransformLoadProcess(venue_provider).execute()

        assert get_image_adapter.last_request == None

    def should_create_offer_even_if_thumb_is_incorrect(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)

        venue_provider = self.setup_cinema_objects()
        # Image that should raise a `pcapi.core.offers.exceptions.UnidentifiedImage`
        file_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_fake_jpg.jpg"
        with open(file_path, "rb") as thumb_file:
            poster = thumb_file.read()
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=poster)
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        EMSExtractTransformLoadProcess(venue_provider).execute()

        assert db.session.query(offers_models.Offer).count() == 2
        created_offer = (
            db.session.query(offers_models.Offer).filter_by(idAtProvider=f"SHJRH%{venue_provider.venueId}%EMS").one()
        )
        assert len(created_offer.mediations) == 0

    @pytest.mark.parametrize(
        "get_adapter_error_params",
        [
            # invalid responses
            {"status_code": 404},
            {"status_code": 502},
            # unexpected errors
            {"exc": requests.exceptions.ReadTimeout},
            {"exc": requests.exceptions.ConnectTimeout},
        ],
    )
    def test_handle_error_on_movie_poster(self, get_adapter_error_params, requests_mock, caplog):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)

        venue_provider = self.setup_cinema_objects()
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", **get_adapter_error_params)
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        with caplog.at_level(logging.WARNING):
            EMSExtractTransformLoadProcess(venue_provider).execute()

        assert db.session.query(offers_models.Offer).count() == 2
        created_offer = (
            db.session.query(offers_models.Offer).filter_by(idAtProvider=f"SHJRH%{venue_provider.venueId}%EMS").one()
        )
        assert created_offer.image is None

        assert len(caplog.records) >= 1

        last_record = caplog.records.pop()
        assert last_record.message == "Could not fetch movie poster"
        assert last_record.extra == {
            "client": "EMSScheduleConnector",
            "url": "https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg",
        }

    def should_update_finance_event_when_stock_beginning_datetime_is_updated(self, requests_mock):
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)
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
            EMSExtractTransformLoadProcess(venue_provider).execute()
        mock_update_finance_event.assert_not_called()

        # synchronize with show with same date
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        requests_mock.get("https://example.com/FR/poster/D7C57D16/600/FGMSE.jpg", content=bytes())

        with mock.patch("pcapi.core.finance.api.update_finance_event_pricing_date") as mock_update_finance_event:
            EMSExtractTransformLoadProcess(venue_provider).execute()
        mock_update_finance_event.assert_not_called()

        # synchronize with show with new date
        requests_mock.get("https://fake_url.com?version=0", json=ems_fixtures.DATA_VERSION_0_WITH_NEW_DATE)
        requests_mock.get("https://example.com/FR/poster/5F988F1C/600/SHJRH.jpg", content=bytes())
        # targeting specific stock whith idAtprovider
        stock = (
            db.session.query(offers_models.Stock).where(offers_models.Stock.idAtProviders.like("%999700079243")).first()
        )
        assert stock is not None
        event_created = create_finance_event_to_update(stock=stock, venue_provider=venue_provider)
        last_pricingOrderingDate = event_created.pricingOrderingDate
        EMSExtractTransformLoadProcess(venue_provider).execute()
        assert event_created.pricingOrderingDate != last_pricingOrderingDate
