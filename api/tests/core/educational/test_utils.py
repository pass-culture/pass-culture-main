from datetime import datetime

from pcapi.core.educational import utils


class ComputeEducationalBookingCancellationLimitDateTest:
    def test_should_be_15_days_before_event_when_booking_occured_more_than_15_days_before_event(
        self,
    ) -> None:
        # Given
        booking_datetime = datetime.fromisoformat("2021-11-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")
        fifteen_days_before_event = datetime.fromisoformat("2021-11-30T20:00:00")

        # When
        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == fifteen_days_before_event

    def test_should_be_booking_date_when_booking_occured_less_than_15_days_before_event(
        self,
    ) -> None:
        # Given
        booking_datetime = datetime.fromisoformat("2021-12-04T15:00:00")
        event_beginning_datetime = datetime.fromisoformat("2021-12-15T20:00:00")

        # When
        cancellation_limit_date = utils.compute_educational_booking_cancellation_limit_date(
            event_beginning_datetime, booking_datetime
        )

        # Then
        assert cancellation_limit_date == booking_datetime


class GetInstitutionTypeAndNameTest:
    def test_simple_cases(self) -> None:
        # Given
        test_cases = {
            "LP pouet": ("LYCEE PROFESSIONNEL", "pouet"),
            "E.R.P.D.PR taça": ("ECOLE REGIONALE DU PREMIER DEGRE PRIVEE", "taça"),
        }
        for given, expected in test_cases.items():
            result = utils.get_institution_type_and_name(given)
            assert result == expected

    def test_institution_without_type(self) -> None:
        result = utils.get_institution_type_and_name(" rien")
        assert result == ("", "rien")

    def test_conflitcual_cases(self) -> None:
        # Given
        test_cases = {
            "LG PR pouet": ("LYCEE GENERAL PRIVE", "pouet"),
            "LGTA taça": ("LYCEE GENERAL TECHNOLOGIQUE AGRICOLE", "taça"),
        }
        for given, expected in test_cases.items():
            result = utils.get_institution_type_and_name(given)
            assert result == expected


class HashUserEmailTest:
    def test_should_hash_user_email(self) -> None:
        # Given
        email = "test@mail.com"

        # When
        result = utils.get_hashed_user_id(email)

        # Then
        assert result == "f0e2a21bcf499cbc713c47d8f034d66e90a99f9ffcfe96466c9971dfdc5c9816"
