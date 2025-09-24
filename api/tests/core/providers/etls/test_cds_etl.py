import datetime
import decimal
import logging
from unittest import mock

import pytest
import time_machine

import pcapi.core.offers.models as offers_models
import pcapi.core.providers.exceptions as providers_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.providers.clients import cds_serializers
from pcapi.core.providers.etls.cds_etl import CDSExtractTransformLoadProcess
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.search import models as search_models
from pcapi.models import db
from pcapi.utils import requests

from . import cds_fixtures


pytestmark = pytest.mark.usefixtures("db_session")

TODAY_STR = datetime.date.today().strftime("%Y-%m-%d")
FUTURE_DATE_STR = (datetime.date.today() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")


@mock.patch("pcapi.settings.CDS_API_URL", "cds_api.fake/")
class CDSExtractTransformLoadProcessTest:
    def setup_cinema_objects(self):
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(
            provider=cds_provider,
            isDuoOffers=True,
            venue__pricing_point="self",
            venueIdAtOfferProvider="venue_id_at_provider",
        )
        cinema_provider_pivot = providers_factories.CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot,
            accountId="account_id",
            cinemaApiToken="fake_token",
        )

        return venue_provider

    def setup_requests_mock(self, requests_mock):
        requests_mock.get(
            "https://account_id.cds_api.fake/shows?api_token=fake_token",
            json=cds_fixtures.MANY_SHOWS_RESPONSE_JSON,
        )
        requests_mock.get(
            "https://account_id.cds_api.fake/media?api_token=fake_token",
            json=cds_fixtures.MEDIA_RESPONSE_JSON,
        )
        requests_mock.get(
            "https://account_id.cds_api.fake/mediaoptions?api_token=fake_token",
            json=cds_fixtures.MEDIA_OPTIONS_RESPONSE_JSON,
        )
        requests_mock.get(
            "https://account_id.cds_api.fake/cinemas?api_token=fake_token",
            json=cds_fixtures.CINEMAS_RESPONSE_JSON,
        )
        requests_mock.get(
            "https://account_id.cds_api.fake/vouchertype?api_token=fake_token",
            json=cds_fixtures.VOUCHER_TYPES_RESPONSE_JSON,
        )

    def test_execute_should_raise_inactive_provider(self):
        venue_provider = self.setup_cinema_objects()
        venue_provider.provider.isActive = False
        etl_process = CDSExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveProvider):
            etl_process.execute()

    def test_execute_should_raise_inactive_venue_provider_provider(self):
        venue_provider = self.setup_cinema_objects()
        venue_provider.isActive = False
        etl_process = CDSExtractTransformLoadProcess(venue_provider)

        with pytest.raises(providers_exceptions.InactiveVenueProvider):
            etl_process.execute()

    def test_should_log_and_raise_error_if_extract_fails(self, caplog, requests_mock):
        venue_provider = self.setup_cinema_objects()
        etl_process = CDSExtractTransformLoadProcess(venue_provider)
        requests_mock.get(
            "https://account_id.cds_api.fake/media?api_token=fake_token",
            exc=requests.exceptions.ConnectTimeout("pas le time"),
        )

        with caplog.at_level(logging.WARNING):
            with pytest.raises(requests.exceptions.ConnectTimeout):
                etl_process.execute()

        assert len(caplog.records) >= 1
        last_record = caplog.records[-1]
        assert last_record.message == "[CDSExtractTransformLoadProcess] Step 1 - Extract failed"
        assert last_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {"exc": "ConnectTimeout", "msg": "pas le time"},
        }

    def test_extract_should_return_raw_results(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)

        etl_process = CDSExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()

        assert extract_result == {
            "movies": [
                cds_serializers.MediaCDS(
                    id=1,
                    title="Test movie #1",
                    duration=7200,
                    posterpath=None,
                    storyline="Test description #1",
                    visanumber="123",
                    allocineid=None,
                ),
                cds_serializers.MediaCDS(
                    id=2,
                    title="Test movie #2",
                    duration=5400,
                    posterpath=None,
                    storyline="Test description #2",
                    visanumber="456",
                    allocineid=None,
                ),
                cds_serializers.MediaCDS(
                    id=3,
                    title="Test movie #3",
                    duration=6600,
                    posterpath=None,
                    storyline="Test description #3",
                    visanumber=None,
                    allocineid=None,
                ),
            ],
            "media_options": {
                12: "VF",
                13: "VO",
                14: "3D",
            },
            "voucher_types": [
                cds_serializers.VoucherTypeCDS(
                    id=2,
                    code="PSCULTURE",
                    tariff=cds_serializers.TariffCDS(id=96, price=5, active=True, labeltariff="Tarif pass Culture"),
                ),
                cds_serializers.VoucherTypeCDS(
                    id=3,
                    code="PSCULTURE",
                    tariff=cds_serializers.TariffCDS(id=97, price=6, active=True, labeltariff="Tarif PC"),
                ),
            ],
            "is_internet_sale_gauge_active": False,
            "shows": [
                cds_serializers.ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=98,
                    internet_remaining_place=10,
                    showtime=datetime.datetime(
                        2022, 3, 28, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                    ),
                    shows_tariff_pos_type_collection=[
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=96)),
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=3)),
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=2)),
                    ],
                    screen=cds_serializers.IdObjectCDS(id=10),
                    media=cds_serializers.IdObjectCDS(id=1),
                    shows_mediaoptions_collection=[
                        cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=12))
                    ],
                ),
                cds_serializers.ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=120,
                    internet_remaining_place=30,
                    showtime=datetime.datetime(
                        2022, 3, 29, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                    ),
                    shows_tariff_pos_type_collection=[
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=96))
                    ],
                    screen=cds_serializers.IdObjectCDS(id=10),
                    media=cds_serializers.IdObjectCDS(id=1),
                    shows_mediaoptions_collection=[
                        cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=12)),
                        cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=14)),
                    ],
                ),
                cds_serializers.ShowCDS(
                    id=3,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=88,
                    internet_remaining_place=100,
                    showtime=datetime.datetime(
                        2022, 3, 30, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                    ),
                    shows_tariff_pos_type_collection=[
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=96))
                    ],
                    screen=cds_serializers.IdObjectCDS(id=20),
                    media=cds_serializers.IdObjectCDS(id=2),
                    shows_mediaoptions_collection=[
                        cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=13))
                    ],
                ),
            ],
        }

    def test_transform_should_return_loadable_result(self, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        etl_process = CDSExtractTransformLoadProcess(venue_provider)

        extract_result = etl_process._extract()
        transform_result = etl_process._transform(extract_result)
        assert transform_result == [
            {
                "movie_uuid": f"1%{venue_id}%CDS",
                "movie_data": offers_models.Movie(
                    allocine_id=None,
                    description="Test description #1",
                    duration=120,
                    poster_url=None,
                    visa="123",
                    title="Test movie #1",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "stock_uuid": f"1%{venue_id}%CDS#1",
                        "show_datetime": datetime.datetime(2022, 3, 28, 10, 0),
                        "remaining_quantity": 98,
                        "features": ["VF"],
                        "price": decimal.Decimal("5.0"),
                        "price_label": "Tarif pass Culture",
                    },
                    {
                        "stock_uuid": f"1%{venue_id}%CDS#2",
                        "show_datetime": datetime.datetime(2022, 3, 29, 10, 0),
                        "remaining_quantity": 120,
                        "features": ["VF", "3D"],
                        "price": decimal.Decimal("5.0"),
                        "price_label": "Tarif pass Culture",
                    },
                ],
            },
            {
                "movie_uuid": f"2%{venue_id}%CDS",
                "movie_data": offers_models.Movie(
                    allocine_id=None,
                    description="Test description #2",
                    duration=90,
                    poster_url=None,
                    visa="456",
                    title="Test movie #2",
                    extra_data=None,
                ),
                "stocks_data": [
                    {
                        "features": ["VO"],
                        "price": decimal.Decimal("5.0"),
                        "price_label": "Tarif pass Culture",
                        "remaining_quantity": 88,
                        "show_datetime": datetime.datetime(2022, 3, 30, 10, 0),
                        "stock_uuid": f"2%{venue_id}%CDS#3",
                    },
                ],
            },
        ]

    def test_transform_should_drop_show_without_pc_voucher_type(self, caplog):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        etl_process = CDSExtractTransformLoadProcess(venue_provider)
        extract_result = {
            "movies": [
                cds_serializers.MediaCDS(
                    id=1,
                    title="Test movie #1",
                    duration=7200,
                    posterpath=None,
                    storyline="Test description #1",
                    visanumber="123",
                    allocineid=None,
                ),
            ],
            "media_options": {},
            "voucher_types": [
                cds_serializers.VoucherTypeCDS(
                    id=2,
                    code="FULL_PRICE",
                    tariff=cds_serializers.TariffCDS(id=96, price=5, active=True, labeltariff="Plein tarif"),
                ),
            ],
            "is_internet_sale_gauge_active": False,
            "shows": [
                cds_serializers.ShowCDS(
                    id=53,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=True,
                    remaining_place=98,
                    internet_remaining_place=10,
                    showtime=datetime.datetime(
                        2022, 3, 28, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                    ),
                    shows_tariff_pos_type_collection=[
                        # only full price tariff
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=2)),
                    ],
                    screen=cds_serializers.IdObjectCDS(id=10),
                    media=cds_serializers.IdObjectCDS(id=1),
                    shows_mediaoptions_collection=[
                        cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=12))
                    ],
                ),
            ],
        }

        with caplog.at_level(logging.WARNING):
            transform_result = etl_process._transform(extract_result)
        assert transform_result == []

        assert len(caplog.records) >= 2
        missing_tariff_record = caplog.records[-2]
        assert missing_tariff_record.message == "[CDSExtractTransformLoadProcess] Step 2 - Missing pass Culture tariff"
        assert missing_tariff_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {
                "show_id": 53,
                "show_datetime": datetime.datetime(
                    2022, 3, 28, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                ),
            },
        }

        movie_without_show_record = caplog.records[-1]
        assert (
            movie_without_show_record.message == "[CDSExtractTransformLoadProcess] Step 2 - Movie does not have shows"
        )
        assert movie_without_show_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {
                "movie_uuid": f"1%{venue_id}%CDS",
                "movie_title": "Test movie #1",
                "allocine_id": None,
                "visa": "123",
            },
        }

    def test_transform_should_drop_show_without_movie(self, caplog):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        etl_process = CDSExtractTransformLoadProcess(venue_provider)
        extract_result = {
            "movies": [
                cds_serializers.MediaCDS(
                    id=1,
                    title="Test movie #1",
                    duration=7200,
                    posterpath=None,
                    storyline="Test description #1",
                    visanumber="123",
                    allocineid=None,
                ),
            ],
            "media_options": {},
            "voucher_types": [
                cds_serializers.VoucherTypeCDS(
                    id=2,
                    code="PSCULTURE",
                    tariff=cds_serializers.TariffCDS(id=96, price=5, active=True, labeltariff="Tarif pass Culture"),
                ),
            ],
            "is_internet_sale_gauge_active": False,
            "shows": [
                cds_serializers.ShowCDS(
                    id=56,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=True,
                    remaining_place=98,
                    internet_remaining_place=10,
                    showtime=datetime.datetime(
                        2022, 3, 28, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                    ),
                    shows_tariff_pos_type_collection=[
                        cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=2)),
                    ],
                    screen=cds_serializers.IdObjectCDS(id=10),
                    media=cds_serializers.IdObjectCDS(id=2),  # not present in movie
                    shows_mediaoptions_collection=[
                        cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=12))
                    ],
                ),
            ],
        }
        with caplog.at_level(logging.WARNING):
            transform_result = etl_process._transform(extract_result)

        assert transform_result == []

        assert len(caplog.records) >= 2
        missing_movie_record = caplog.records[-2]
        assert missing_movie_record.message == "[CDSExtractTransformLoadProcess] Step 2 - Missing movie"
        assert missing_movie_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {
                "show_id": 56,
                "show_datetime": datetime.datetime(
                    2022, 3, 28, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))
                ),
            },
        }

        movie_without_show_record = caplog.records[-1]
        assert (
            movie_without_show_record.message == "[CDSExtractTransformLoadProcess] Step 2 - Movie does not have shows"
        )
        assert movie_without_show_record.extra == {
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
            "venue_provider_id": venue_provider.id,
            "venue_id_at_offer_provider": venue_provider.venueIdAtOfferProvider,
            "data": {
                "movie_uuid": f"1%{venue_id}%CDS",
                "movie_title": "Test movie #1",
                "allocine_id": None,
                "visa": "123",
            },
        }

    @time_machine.travel(datetime.datetime(2022, 2, 12, 12, 41, 30), tick=False)
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_execute_should_create_and_index_offer(self, async_index_offer_ids_mock, requests_mock):
        venue_provider = self.setup_cinema_objects()
        venue_id = venue_provider.venueId
        self.setup_requests_mock(requests_mock)

        CDSExtractTransformLoadProcess(venue_provider).execute()

        offer_1 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"1%{venue_id}%CDS").one_or_none()
        offer_2 = db.session.query(offers_models.Offer).filter_by(idAtProvider=f"2%{venue_id}%CDS").one_or_none()

        assert offer_1
        assert offer_1.idAtProvider == f"1%{venue_id}%CDS"
        assert offer_1.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_1.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_1.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_1.publicationDatetime == datetime.datetime(2022, 2, 12, 12, 41, 30)
        assert offer_1.dateModifiedAtLastProvider == datetime.datetime(2022, 2, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_1.product
        assert offer_1.product.name == "Test movie #1"
        assert offer_1.product.description == "Test description #1"
        assert offer_1.product.durationMinutes == 120
        assert offer_1.product.extraData.get("allocineId") == None
        assert offer_1.product.extraData["visa"] == "123"

        assert offer_2
        assert offer_2.idAtProvider == f"2%{venue_id}%CDS"
        assert offer_2.bookingEmail == venue_provider.venue.bookingEmail
        assert offer_2.subcategoryId == subcategories.SEANCE_CINE.id
        assert offer_2.withdrawalDetails == venue_provider.venue.withdrawalDetails
        assert offer_2.publicationDatetime == datetime.datetime(2022, 2, 12, 12, 41, 30)
        assert offer_2.dateModifiedAtLastProvider == datetime.datetime(2022, 2, 12, 12, 41, 30, tzinfo=datetime.UTC)

        assert offer_2.product
        assert offer_2.product.name == "Test movie #2"
        assert offer_2.product.description == "Test description #2"
        assert offer_2.product.durationMinutes == 90
        assert offer_2.product.extraData.get("allocineId") == None
        assert offer_2.product.extraData["visa"] == "456"
        assert not offer_2.product.productMediations

        offer_1_stocks = offer_1.activeStocks
        assert len(offer_1_stocks) == 2
        offer_1_stocks.sort(key=lambda offer: offer.idAtProviders)
        offer_1_stock_1 = offer_1_stocks[0]
        assert offer_1_stock_1.idAtProviders == f"1%{venue_id}%CDS#1"
        assert offer_1_stock_1.beginningDatetime == datetime.datetime(2022, 3, 28, 10, 0)
        assert offer_1_stock_1.bookingLimitDatetime == datetime.datetime(2022, 3, 28, 10, 0)
        assert offer_1_stock_1.dateModifiedAtLastProvider == datetime.datetime(2022, 2, 12, 12, 41, 30)
        assert offer_1_stock_1.features == ["VF"]
        assert offer_1_stock_1.quantity == 98
        assert offer_1_stock_1.price == decimal.Decimal("5.0")
        assert offer_1_stock_1.priceCategory.price == decimal.Decimal("5.0")
        assert offer_1_stock_1.priceCategory.label == "Tarif pass Culture"

        offer_1_stock_2 = offer_1_stocks[1]
        assert offer_1_stock_2.idAtProviders == f"1%{venue_id}%CDS#2"
        assert offer_1_stock_2.beginningDatetime == datetime.datetime(2022, 3, 29, 10, 0)
        assert offer_1_stock_2.bookingLimitDatetime == datetime.datetime(2022, 3, 29, 10, 0)
        assert offer_1_stock_2.dateModifiedAtLastProvider == datetime.datetime(2022, 2, 12, 12, 41, 30)
        assert offer_1_stock_2.features == ["VF", "3D"]
        assert offer_1_stock_2.quantity == 120
        assert offer_1_stock_2.price == decimal.Decimal("5.0")
        assert offer_1_stock_2.priceCategory.price == decimal.Decimal("5.0")
        assert offer_1_stock_2.priceCategory.label == "Tarif pass Culture"

        assert len(offer_2.activeStocks) == 1
        offer_2_stock_1 = offer_2.activeStocks[0]
        assert offer_2_stock_1.idAtProviders == f"2%{venue_id}%CDS#3"
        assert offer_2_stock_1.beginningDatetime == datetime.datetime(2022, 3, 30, 10, 0)
        assert offer_2_stock_1.bookingLimitDatetime == datetime.datetime(2022, 3, 30, 10, 0)
        assert offer_2_stock_1.dateModifiedAtLastProvider == datetime.datetime(2022, 2, 12, 12, 41, 30)
        assert offer_2_stock_1.features == ["VO"]
        assert offer_2_stock_1.quantity == 88
        assert offer_2_stock_1.price == decimal.Decimal("5.0")
        assert offer_2_stock_1.priceCategory.price == decimal.Decimal("5.0")
        assert offer_2_stock_1.priceCategory.label == "Tarif pass Culture"

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
        venue_provider = self.setup_cinema_objects()
        self.setup_requests_mock(requests_mock)

        CDSExtractTransformLoadProcess(venue_provider).execute()
        db.session.query(offers_models.PriceCategory).count() == 2
        CDSExtractTransformLoadProcess(venue_provider).execute()
        db.session.query(offers_models.PriceCategory).count() == 2
