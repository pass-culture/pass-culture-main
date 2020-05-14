from domain.booking_recap.booking_recap import BookingRecapStatus
from tests.domain_creators.generic_creators import create_domain_thing_booking_recap, create_domain_event_booking_recap


class BookingRecapTest:
    class StatusPropertyTest:
        class WhenBookingHasNoPaymentsTest:
            def test_should_return_booked_status_when_booking_is_not_cancelled_nor_used(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=False,
                    booking_is_cancelled=False,
                    booking_is_reimbursed=False)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.booked

            def test_should_return_validated_status_when_booking_is_used_and_not_cancelled(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=True,
                    booking_is_cancelled=False,
                    booking_is_reimbursed=False)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.validated

            def test_should_return_cancelled_status_when_booking_is_cancelled_but_not_used(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=False,
                    booking_is_cancelled=True,
                    booking_is_reimbursed=False)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.cancelled

            def test_should_return_cancelled_status_when_booking_is_cancelled_and_used(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=True,
                    booking_is_cancelled=True,
                    booking_is_reimbursed=False)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.cancelled

        class WhenBookingIsReimbursedTest:
            def test_should_return_reimbursed_status_when_booking_is_not_cancelled_nor_used(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=False,
                    booking_is_cancelled=False,
                    booking_is_reimbursed=True)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.reimbursed

            def test_should_return_reimbursed_status_when_booking_is_used_and_not_cancelled(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=True,
                    booking_is_cancelled=False,
                    booking_is_reimbursed=True)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.reimbursed

            def test_should_return_reimbursed_status_when_booking_is_used_and_cancelled(self):
                # Given
                booking_recap = create_domain_thing_booking_recap(
                    booking_is_used=True,
                    booking_is_cancelled=True,
                    booking_is_reimbursed=True)

                # When
                booking_recap_status = booking_recap.booking_status

                # Then
                assert booking_recap_status == BookingRecapStatus.reimbursed

    class TokenTest:
        def test_should_not_return_token_when_offer_is_thing_and_booking_is_not_used_nor_cancelled(self):
            # Given
            booking_recap = create_domain_thing_booking_recap(booking_token='ABCDE', booking_is_used=False,
                                                              booking_is_cancelled=False)

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token is None

        def test_should_return_token_when_offer_is_thing_and_booking_is_used_and_not_cancelled(self):
            # Given
            booking_recap = create_domain_thing_booking_recap(booking_token='ABCDE', booking_is_used=True,
                                                              booking_is_cancelled=False)

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == 'ABCDE'

        def test_should_return_token_when_offer_is_thing_and_booking_is_not_used_and_is_cancelled(self):
            # Given
            booking_recap = create_domain_thing_booking_recap(booking_token='ABCDE', booking_is_used=False,
                                                              booking_is_cancelled=True)

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == 'ABCDE'

        def test_should_return_token_when_offer_is_thing_and_booking_is_used_and_cancelled(self):
            # Given
            booking_recap = create_domain_thing_booking_recap(booking_token='ABCDE', booking_is_used=True,
                                                              booking_is_cancelled=True)

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == 'ABCDE'

        def test_should_return_token_when_offer_is_event_and_booking_is_not_used_nor_cancelled(self):
            # Given
            booking_recap = create_domain_event_booking_recap(booking_token='ABCDE', booking_is_used=False,
                                                              booking_is_cancelled=False)

            # When
            booking_recap_token = booking_recap.booking_token

            # Then
            assert booking_recap_token == 'ABCDE'
