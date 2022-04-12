import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.serialization.cine_digital_service_serializers import PaymentTypeCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import TariffCDS
from pcapi.core.booking_providers.cds.CineDigitalService import CineDigitalServiceAPI
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions


class CineDigitalServiceGetShowTest:
    @patch("pcapi.core.booking_providers.cds.CineDigitalService.get_shows")
    def test_should_return_show_corresponding_to_show_id(self, mocked_get_shows):
        shows = [
            ShowCDS(
                id=1,
                internet_remaining_place=10,
                showtime=datetime.datetime(2022, 3, 28),
                is_cancelled=False,
                is_deleted=False,
            ),
            ShowCDS(
                id=2,
                internet_remaining_place=30,
                showtime=datetime.datetime(2022, 3, 29),
                is_cancelled=False,
                is_deleted=False,
            ),
            ShowCDS(
                id=3,
                internet_remaining_place=100,
                showtime=datetime.datetime(2022, 3, 30),
                is_cancelled=False,
                is_deleted=False,
            ),
        ]
        mocked_get_shows.return_value = shows
        cine_digital_service = CineDigitalServiceAPI(cinemaid="cinemaid_test", token="token_test", apiUrl="apiUrl_test")
        show = cine_digital_service.get_show(2)

        assert show.id == 2

    @patch("pcapi.core.booking_providers.cds.CineDigitalService.get_shows")
    def test_should_raise_exception_if_show_not_found(self, mocked_get_shows):
        shows = [
            ShowCDS(
                id=1,
                internet_remaining_place=10,
                showtime=datetime.datetime(2022, 3, 28),
                is_cancelled=False,
                is_deleted=False,
            ),
            ShowCDS(
                id=2,
                internet_remaining_place=30,
                showtime=datetime.datetime(2022, 3, 29),
                is_cancelled=False,
                is_deleted=False,
            ),
            ShowCDS(
                id=3,
                internet_remaining_place=100,
                showtime=datetime.datetime(2022, 3, 30),
                is_cancelled=False,
                is_deleted=False,
            ),
        ]
        mocked_get_shows.return_value = shows
        cine_digital_service = CineDigitalServiceAPI(cinemaid="test_id", token="token_test", apiUrl="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_show(4)
        assert (
            str(cds_exception.value)
            == "Show #4 not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetPaymentTypeTest:
    @patch("pcapi.core.booking_providers.cds.CineDigitalService.get_payment_types")
    def test_should_return_pass_culture_payment_type(self, mocked_get_payment_types):
        payment_types = [
            PaymentTypeCDS(
                id=21,
                active=True,
                shortlabel="PASSCULTURE",
            ),
            PaymentTypeCDS(
                id=22,
                active=True,
                shortlabel="OTHERPAYMENTYPE",
            ),
        ]

        mocked_get_payment_types.return_value = payment_types
        cine_digital_service = CineDigitalServiceAPI(cinemaid="cinemaid_test", token="token_test", apiUrl="apiUrl_test")

        payment_type = cine_digital_service.get_payment_type()
        assert payment_type.short_label == "PASSCULTURE"

    @patch("pcapi.core.booking_providers.cds.CineDigitalService.get_payment_types")
    def test_should_raise_exception_if_payment_type_not_found(self, mocked_get_payment_types):
        payment_types = [
            PaymentTypeCDS(
                id=23,
                active=True,
                shortlabel="OTHERPAYMENTYPE2",
            ),
            PaymentTypeCDS(
                id=22,
                active=True,
                shortlabel="OTHERPAYMENTYPE",
            ),
        ]
        mocked_get_payment_types.return_value = payment_types
        cine_digital_service = CineDigitalServiceAPI(cinemaid="test_id", token="token_test", apiUrl="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_payment_type()
        assert (
            str(cds_exception.value)
            == "Pass Culture payment type not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetTariffTest:
    @patch("pcapi.core.booking_providers.cds.CineDigitalService.get_tariffs")
    def test_should_return_tariffs_with_pass_culture_tariff(self, mocked_get_tariffs):
        tariffs = [
            TariffCDS(
                id=1,
                price=10,
                label="Pass Culture 5€",
                is_active=True,
            ),
            TariffCDS(
                id=2,
                price=3.5,
                label="Other tariff",
                is_active=True,
            ),
        ]
        mocked_get_tariffs.return_value = tariffs
        cine_digital_service = CineDigitalServiceAPI(cinemaid="cinemaid_test", token="token_test", apiUrl="apiUrl_test")
        tariff = cine_digital_service.get_tariff()

        assert tariff.label == "Pass Culture 5€"

    @patch("pcapi.core.booking_providers.cds.CineDigitalService.get_tariffs")
    def test_should_raise_exception_if_tariff_not_found(self, mocked_get_tariffs):
        tariffs = [
            TariffCDS(
                id=1,
                price=10,
                label="Another Tariff",
                is_active=True,
            ),
            TariffCDS(
                id=2,
                price=3.5,
                label="Other tariff",
                is_active=True,
            ),
        ]
        mocked_get_tariffs.return_value = tariffs
        cine_digital_service = CineDigitalServiceAPI(cinemaid="test_id", token="token_test", apiUrl="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_tariff()
        assert (
            str(cds_exception.value)
            == "Tariff Pass Culture not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )
