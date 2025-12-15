import copy
import datetime
import decimal
import logging
import pathlib
from unittest import mock

import pytest
import time_machine

import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.providers.clients import cgr_serializers
from pcapi.core.providers.etls.cgr_etl import CGRExtractTransformLoadProcess
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.search import models as search_models
from pcapi.models import db
from pcapi.utils import requests

import tests
from tests.connectors.cgr import soap_definitions

from . import cgr_fixtures


pytestmark = pytest.mark.usefixtures("db_session")

TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
FUTURE_DATE_STR = (datetime.date.today() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")


class CGRExtractTransformLoadProcessTest:
    def setup_cinema_objects(self):
        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cgr_provider,
            isDuoOffers=True,
            venue__pricing_point="self",
            venueIdAtOfferProvider="venue_id_at_provider",
        )
        cinema_provider_pivot = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot,
            cinemaUrl="https://cgr-cinema-0.example.com/web_service",
        )

        return venue_provider

    def setup_requests_mock(self, requests_mock, film_payload: dict | list | None = None):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        film_payload = film_payload or [cgr_fixtures.FILM_138473]
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=cgr_fixtures.cgr_response_template(film_payload),
        )

    def test_execute_should_raise_inactive_provider(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)
        venue_provider.provider.isActive = False
        etl_process = CGRExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveProvider):
            etl_process.execute()

    def test_execute_should_raise_inactive_venue_provider_provider(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)
        venue_provider.isActive = False
        etl_process = CGRExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveVenueProvider):
            etl_process.execute()

    def test_should_log_and_raise_error_if_extract_fails(self, caplog, requests_mock):
        venue_provider = self.setup_cinema_objects()
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            exc=requests.exceptions.ConnectTimeout("houpsi"),
        )
        etl_process = CGRExtractTransformLoadProcess(venue_provider)

        with caplog.at_level(logging.WARNING):
            with pytest.raises(requests.exceptions.ConnectTimeout):
                etl_process.execute()

        assert len(caplog.records) >= 1
        last_record = caplog.records[-1]
        assert last_record.message == "[CGRExtractTransformLoadProcess] Step 1 - Extract failed"
        assert last_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {"exc": "ConnectTimeout", "msg": "houpsi"},
        }

    def test_extract_should_return_raw_results(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)

        etl_process = CGRExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        assert extract_result == {
            "films": [
                cgr_serializers.Film(
                    IDFilm=138473,
                    IDFilmAlloCine=138473,
                    Titre="Venom",
                    NumVisa=149341,
                    Duree=112,
                    Synopsis="Possédé par un symbiote qui agit de manière autonome, le journaliste Eddie Brock devient le protecteur létal Venom.",
                    Affiche="https://example.com/149341.jpg",
                    TypeFilm="CNC",
                    Seances=[
                        cgr_serializers.Seance(
                            IDSeance=177182,
                            Date=datetime.date(2023, 1, 29),
                            Heure=datetime.time(14, 0),
                            NbPlacesRestantes=99,
                            bAvecPlacement=True,
                            bAvecDuo=True,
                            bICE=True,
                            Relief="2D",
                            Version="VF",
                            bAVP=False,
                            PrixUnitaire=decimal.Decimal("6.9"),
                            libTarif="Tarif Standard ICE",
                        )
                    ],
                ),
            ],
        }

    def test_transform_should_return_loadable_result(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        etl_process = CGRExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        transform_result = etl_process._transform(extract_result=extract_result)
        assert transform_result == [
            {
                "movie_uuid": f"138473%{venue_id}%CGR",
                "movie_data": offers_models.Movie(
                    allocine_id="138473",
                    description="Possédé par un symbiote qui agit de manière autonome, le journaliste Eddie Brock devient le protecteur létal Venom.",
                    duration=112,
                    poster_url="https://example.com/149341.jpg",
                    visa="149341",
                    title="Venom",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "stock_uuid": f"138473%{venue_id}%CGR#177182",
                        "show_datetime": datetime.datetime(2023, 1, 29, 13, 0),  # date in naive UTC
                        "remaining_quantity": 99,
                        "features": ["VF", "ICE"],
                        "price": decimal.Decimal("6.9"),
                        "price_label": "Tarif Standard ICE",
                    }
                ],
            }
        ]

    def test_transform_should_drop_movie_without_show(self, requests_mock, caplog):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId

        film_without_show = copy.deepcopy(cgr_fixtures.FILM_138473)
        film_without_show["Seances"] = []
        self.setup_requests_mock(requests_mock, film_payload=[film_without_show])

        etl_process = CGRExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        with caplog.at_level(logging.WARNING):
            transform_result = etl_process._transform(extract_result=extract_result)
        assert transform_result == []

        assert len(caplog.records) >= 1
        movie_without_show_record = caplog.records[-1]
        assert (
            movie_without_show_record.message == "[CGRExtractTransformLoadProcess] Step 2 - Movie does not have shows"
        )
        assert movie_without_show_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {
                "movie_uuid": f"138473%{venue_id}%CGR",
                "movie_title": "Venom",
                "allocine_id": "138473",
                "visa": "149341",
            },
        }

    @time_machine.travel(datetime.datetime(2022, 12, 12, 12, 41, 30), tick=False)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_execute_should_create_and_index_offer(self, async_index_offer_ids_mock, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        file_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as thumb_file:
            poster_venom = thumb_file.read()
        requests_mock.get("https://example.com/149341.jpg", content=poster_venom)

        CGRExtractTransformLoadProcess(venue_provider).execute()

        offer_1 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"138473%{venue_id}%CGR").one_or_none()

        assert offer_1
        assert offer_1.idAtProvider == f"138473%{venue_id}%CGR"
        assert offer_1.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_1.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_1.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_1.dateModifiedAtLastProvider == datetime.datetime(2022, 12, 12, 12, 41, 30, tzinfo=datetime.UTC)
        assert offer_1.publicationDatetime == datetime.datetime(2022, 12, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_1.product
        assert offer_1.product.name == "Venom"
        assert offer_1.product.durationMinutes == 112
        assert offer_1.product.extraData["allocineId"] == 138473
        assert offer_1.product.extraData["visa"] == "149341"
        assert len(offer_1.product.productMediations) == 1
        assert offer_1.product.productMediations[0].lastProvider == venue_provider.provider
        assert offer_1.product.productMediations[0].imageType == offers_models.ImageType.POSTER

        offer_1_stocks = offer_1.activeStocks
        assert len(offer_1_stocks) == 1
        offer_1_stock_1 = offer_1_stocks[0]
        assert offer_1_stock_1.idAtProviders == f"138473%{venue_id}%CGR#177182"
        assert offer_1_stock_1.beginningDatetime == datetime.datetime(2023, 1, 29, 13, 0)
        assert offer_1_stock_1.bookingLimitDatetime == datetime.datetime(2023, 1, 29, 13, 0)
        assert offer_1_stock_1.dateModifiedAtLastProvider == datetime.datetime(2022, 12, 12, 12, 41, 30)
        assert offer_1_stock_1.features == ["VF", "ICE"]
        assert offer_1_stock_1.quantity == 99
        assert offer_1_stock_1.price == decimal.Decimal("6.9")
        assert offer_1_stock_1.priceCategory.price == decimal.Decimal("6.9")
        assert offer_1_stock_1.priceCategory.label == "Tarif Standard ICE"

        async_index_offer_ids_mock.assert_called_once_with(
            set([offer_1.id]),
            reason=search_models.IndexationReason.STOCK_UPDATE,
            log_extra={
                "source": "provider_api",
                "venue_id": venue_provider.venueId,
                "provider_id": venue_provider.providerId,
            },
        )

    def test_should_reuse_price_category(self, requests_mock):
        requests_mock.get("https://cgr-cinema-0.example.com/web_service", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.get("https://example.com/149341.jpg", content=bytes())

        venue_provider = self.setup_cinema_objects()

        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=cgr_fixtures.cgr_response_template([cgr_fixtures.FILM_138473]),
        )

        CGRExtractTransformLoadProcess(venue_provider).execute()
        CGRExtractTransformLoadProcess(venue_provider).execute()

        created_price_category = db.session.query(offers_models.PriceCategory).one()
        assert created_price_category.price == decimal.Decimal("6.9")
