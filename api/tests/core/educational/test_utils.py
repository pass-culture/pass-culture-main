from datetime import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import utils


class ComputeEducationalBookingCancellationLimitDateTest:
    def test_should_be_30_days_before_event_when_booking_occured_more_than_15_days_before_event(
        self,
    ) -> None:
        booking_datetime = datetime.fromisoformat("2021-11-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")
        fifteen_days_before_event = datetime.fromisoformat("2021-11-15T20:00:00")

        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        assert cancellation_limit_date == fifteen_days_before_event

    def test_should_be_30_days_before_event_when_booking_occured_more_than_30_days_before_event(
        self,
    ) -> None:
        booking_datetime = datetime.fromisoformat("2021-11-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")
        thirty_days_before_event = datetime.fromisoformat("2021-11-15T20:00:00")

        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        assert cancellation_limit_date == thirty_days_before_event

    def test_should_be_booking_date_when_booking_occured_less_than_15_days_before_event(
        self,
    ) -> None:
        booking_datetime = datetime.fromisoformat("2021-12-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")

        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        assert cancellation_limit_date == booking_datetime


class HashUserEmailTest:
    def test_should_hash_user_email(self) -> None:
        email = "test@mail.com"

        result = utils.get_hashed_user_id(email)

        assert result == "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816"


class GetNonEmptyDateTimeRangeTest:
    def test_get_non_empty_datetime_range(self) -> None:
        start = datetime(2024, 12, 24, 23, 59, 59)
        end = datetime(2024, 12, 25, 23, 59, 59)

        result = utils.get_non_empty_date_time_range(start, end)

        assert result.lower == start
        assert result.upper == end

    def test_get_non_empty_datetime_range_ends_when_starts(self) -> None:
        start = datetime(2024, 12, 24, 23, 59, 59)

        result = utils.get_non_empty_date_time_range(start, start)

        assert result.lower == start
        assert result.upper == datetime(2024, 12, 25, 0, 0, 0)


@pytest.mark.usefixtures("db_session")
class GetCollectiveOfferFullAddressTest:
    def test_school(self):
        offer = factories.CollectiveOfferOnSchoolLocationFactory()
        result = utils.get_collective_offer_full_address(offer)

        assert result == "En établissement scolaire"

    def test_to_be_defined(self):
        offer = factories.CollectiveOfferOnToBeDefinedLocationFactory()
        result = utils.get_collective_offer_full_address(offer)

        assert result == "À déterminer avec l'enseignant"

    def test_address_venue(self):
        offer = factories.CollectiveOfferOnAddressVenueLocationFactory(venue__publicName="Nice venue")
        result = utils.get_collective_offer_full_address(offer)

        assert result == f"Nice venue - {offer.offererAddress.address.fullAddress}"

    def test_address_other(self):
        offer = factories.CollectiveOfferOnOtherAddressLocationFactory(offererAddress__label="Nice location")
        result = utils.get_collective_offer_full_address(offer)

        assert result == f"Nice location - {offer.offererAddress.address.fullAddress}"

    def test_address_other_label_none(self):
        offer = factories.CollectiveOfferOnOtherAddressLocationFactory(offererAddress__label=None)
        result = utils.get_collective_offer_full_address(offer)

        assert result == offer.offererAddress.address.fullAddress
