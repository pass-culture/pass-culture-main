from datetime import datetime

from pcapi.domain.booking_recap.booking_recap import BookingRecapStatus
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapCancelledHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapConfirmedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapReimbursedHistory
from pcapi.domain.booking_recap.booking_recap_history import BookingRecapValidatedHistory

from tests.domain_creators.generic_creators import create_domain_booking_recap


class BookingRecapTest:
    class StatusPropertyTest:
        class WhenBookingHasNoPaymentsTest:
            def test_should_return_booked_status_when_booking_is_not_cancelled_nor_used(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=False,
                    booking_is_cancelled=False,
                    booking_is_confirmed=False,
                    booking_is_reimbursed=False,
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.booked

            def test_should_return_validated_status_when_booking_is_used_and_not_cancelled(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=True, booking_is_cancelled=False, booking_is_reimbursed=False
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.validated

            def test_should_return_validated_status_when_booking_is_for_a_thing_and_not_cancellable(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=True, booking_is_cancelled=False, booking_is_reimbursed=False
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.validated

            def test_should_return_validated_status_when_booking_is_for_an_event_and_not_cancellable_but_validated(
                self,
            ):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=True,
                    booking_is_cancelled=False,
                    booking_is_confirmed=True,
                    booking_is_reimbursed=False,
                    event_beginning_datetime=datetime(2021, 3, 5),
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.validated

            def test_should_return_confirmed_status_when_booking_is_for_an_event_and_not_cancellable(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=False,
                    booking_is_cancelled=False,
                    booking_is_confirmed=True,
                    booking_is_reimbursed=False,
                    event_beginning_datetime=datetime(2021, 3, 5),
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.confirmed

            def test_should_return_cancelled_status_when_booking_is_cancelled_but_not_used(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=False, booking_is_cancelled=True, booking_is_reimbursed=False
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.cancelled

            def test_should_return_cancelled_status_when_booking_is_cancelled_and_used(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=True, booking_is_cancelled=True, booking_is_reimbursed=False
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.cancelled

        class WhenBookingIsReimbursedTest:
            def test_should_return_reimbursed_status_when_booking_is_not_cancelled_nor_used(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=False, booking_is_cancelled=False, booking_is_reimbursed=True
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.reimbursed

            def test_should_return_reimbursed_status_when_booking_is_used_and_not_cancelled(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=True, booking_is_cancelled=False, booking_is_reimbursed=True
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.reimbursed

            def test_should_return_reimbursed_status_when_booking_is_used_and_cancelled(self):
                # Given
                booking_recap = create_domain_booking_recap(
                    booking_is_used=True, booking_is_cancelled=True, booking_is_reimbursed=True
                )

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.reimbursed

    class TokenTest:
        def test_should_not_return_token_when_offer_is_thing_and_booking_is_not_used_nor_cancelled(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE", booking_is_used=False, booking_is_cancelled=False
            )

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token is None

        def test_should_return_token_when_offer_is_thing_and_booking_is_used_and_not_cancelled(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE", booking_is_used=True, booking_is_cancelled=False
            )

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == "ABCDE"

        def test_should_return_token_when_offer_is_thing_and_booking_is_not_used_and_is_cancelled(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE", booking_is_used=False, booking_is_cancelled=True
            )

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == "ABCDE"

        def test_should_return_token_when_offer_is_thing_and_booking_is_used_and_cancelled(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE", booking_is_used=True, booking_is_cancelled=True
            )

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == "ABCDE"

        def test_should_return_token_when_offer_is_event_and_booking_is_not_used_nor_cancelled(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=False,
                booking_is_cancelled=False,
                event_beginning_datetime=datetime(2021, 3, 5),
            )

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == "ABCDE"

    class BuildHistoryTest:
        def test_should_return_booking_recap_history(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=True,
                booking_is_cancelled=False,
                booking_amount=12,
                booking_date=datetime(2020, 1, 4),
            )

            # When
            booking_recap_history = booking_recap.booking_status_history

            # Then
            assert isinstance(booking_recap_history, BookingRecapHistory)
            assert booking_recap_history.booking_date == datetime(2020, 1, 4)

        def test_should_return_booking_recap_history_with_cancellation(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=True,
                booking_is_cancelled=True,
                booking_amount=12,
                booking_date=datetime(2020, 1, 4),
                cancellation_date=datetime(2020, 1, 5),
            )

            # When
            booking_recap_history = booking_recap.booking_status_history

            # Then
            assert isinstance(booking_recap_history, BookingRecapCancelledHistory)
            assert booking_recap_history.booking_date == datetime(2020, 1, 4)
            assert booking_recap_history.cancellation_date == datetime(2020, 1, 5)

        def test_should_return_booking_recap_history_with_validation(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=True,
                booking_is_cancelled=False,
                booking_amount=12,
                booking_date=datetime(2020, 1, 4),
                date_used=datetime(2020, 1, 5),
            )

            # When
            booking_recap_history = booking_recap.booking_status_history

            # Then
            assert isinstance(booking_recap_history, BookingRecapValidatedHistory)
            assert booking_recap_history.booking_date == datetime(2020, 1, 4)
            assert booking_recap_history.date_used == datetime(2020, 1, 5)

        def test_should_return_booking_recap_history_with_confirmation(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=True,
                booking_is_cancelled=False,
                booking_amount=12,
                booking_is_confirmed=True,
                booking_date=datetime(2020, 1, 4),
                date_used=datetime(2020, 1, 5),
            )

            # When
            booking_recap_history = booking_recap.booking_status_history

            # Then
            assert isinstance(booking_recap_history, BookingRecapConfirmedHistory)

        def test_should_return_booking_recap_history_with_payment(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=True,
                booking_is_cancelled=False,
                booking_amount=12,
                booking_date=datetime(2020, 1, 4),
                payment_date=datetime(2020, 1, 6),
                date_used=datetime(2020, 1, 5),
                booking_is_reimbursed=True,
            )

            # When
            booking_recap_history = booking_recap.booking_status_history

            # Then
            assert isinstance(booking_recap_history, BookingRecapReimbursedHistory)
            assert booking_recap_history.booking_date == datetime(2020, 1, 4)
            assert booking_recap_history.payment_date == datetime(2020, 1, 6)
            assert booking_recap_history.date_used == datetime(2020, 1, 5)

        def test_should_return_booking_recap_history_with_payment_even_if_cancelled(self):
            # Given
            booking_recap = create_domain_booking_recap(
                booking_token="ABCDE",
                booking_is_used=True,
                booking_is_cancelled=True,
                booking_amount=12,
                booking_is_reimbursed=True,
                cancellation_date=datetime(2020, 1, 4),
                booking_date=datetime(2020, 1, 4),
                date_used=datetime(2020, 1, 7),
                payment_date=datetime(2020, 1, 6),
            )

            # When
            booking_recap_history = booking_recap.booking_status_history

            # Then
            assert isinstance(booking_recap_history, BookingRecapReimbursedHistory)
            assert booking_recap_history.booking_date == datetime(2020, 1, 4)
            assert booking_recap_history.payment_date == datetime(2020, 1, 6)
            assert booking_recap_history.date_used == datetime(2020, 1, 7)
