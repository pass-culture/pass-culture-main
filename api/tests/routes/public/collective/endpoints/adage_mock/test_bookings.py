from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import patch

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus

from tests.routes.public.helpers import PublicAPIRestrictedEnvEndpointHelper
from tests.routes.public.helpers import assert_attribute_does_not_change
from tests.routes.public.helpers import assert_attribute_value_changes_to

from .base import AdageMockEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class ConfirmCollectiveBookingTest(AdageMockEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/confirm"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}
    default_factory = factories.PendingCollectiveBookingFactory

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_confirm_pending_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        pending_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(pending_booking, "status", models.CollectiveBookingStatus.CONFIRMED):
            self.assert_request_has_expected_result(
                auth_client, url_params={"booking_id": pending_booking.id}, expected_status_code=204
            )

    def test_confirm_confirmed_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        confirmed_booking = self.setup_base_resource(
            factory=factories.ConfirmedCollectiveBookingFactory,
            venue=venue_provider.venue,
            provider=venue_provider.provider,
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(confirmed_booking, "status"):
            self.assert_request_has_expected_result(
                auth_client, url_params={"booking_id": confirmed_booking.id}, expected_status_code=204
            )

    @pytest.mark.parametrize(
        "booking_factory,expected_status_code,expected_json",
        [
            (factories.UsedCollectiveBookingFactory, 403, {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}),
            (factories.ReimbursedCollectiveBookingFactory, 403, {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}),
            (factories.CancelledCollectiveBookingFactory, 403, {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}),
        ],
    )
    def test_should_raise_403_because_status_does_not_allow_confirmation(
        self, client, booking_factory, expected_status_code, expected_json
    ):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(
            factory=booking_factory, venue=venue_provider.venue, provider=venue_provider.provider
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": booking.id},
                expected_status_code=expected_status_code,
                expected_error_json=expected_json,
            )

    def test_confirm_when_insufficient_fund(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        pending_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        for deposit in pending_booking.educationalInstitution.deposits:
            deposit.amount = 0
        db.session.flush()

        with assert_attribute_does_not_change(pending_booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": pending_booking.id},
                expected_status_code=403,
                expected_error_json={"code": "INSUFFICIENT_FUND"},
            )

    @pytest.mark.features(ENABLE_EAC_FINANCIAL_PROTECTION=True)
    def test_confirm_when_insufficient_ministry_fund(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)
        pending_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        used_booking = self.setup_base_resource(
            factory=factories.UsedCollectiveBookingFactory,
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            deposit=pending_booking.educationalInstitution.deposits[0],
        )

        # ensure offer's stock start between september and december
        # because this validation is not ran after and before that.
        start = pending_booking.collectiveStock.startDatetime.replace(month=10)
        pending_booking.collectiveStock.startDatetime = start

        # pending booking price is within the the institution's budget
        # but some special rules apply at the end of the year: the
        # overall used budget must be at most 1/3 of the total.
        institution = used_booking.educationalInstitution
        deposit_amount = sum(deposit.amount for deposit in institution.deposits)
        used_booking.collectiveStock.price = deposit_amount / 3

        db.session.flush()

        with assert_attribute_does_not_change(pending_booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": pending_booking.id},
                expected_status_code=403,
                expected_error_json={"code": "INSUFFICIENT_MINISTRY_FUND"},
            )

    def test_confirm_when_insufficient_temporary_fund(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        pending_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        for deposit in pending_booking.educationalInstitution.deposits:
            deposit.amount = 0
            deposit.isFinal = False

        db.session.flush()

        with assert_attribute_does_not_change(pending_booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": pending_booking.id},
                expected_status_code=403,
                expected_error_json={"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"},
            )

    def test_confirm_unknown_booking(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"booking_id": 9},
            expected_status_code=404,
            expected_error_json={"code": "BOOKING_NOT_FOUND"},
        )

    def test_confirm_unknown_deposit(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        pending_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        for deposit in pending_booking.educationalInstitution.deposits:
            deposit.educationalYear = factories.EducationalYearFactory()

        with assert_attribute_does_not_change(pending_booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": pending_booking.id},
                expected_status_code=404,
                expected_error_json={"code": "DEPOSIT_NOT_FOUND"},
            )


class CancelCollectiveBookingTest(AdageMockEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/cancel"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}
    default_factory = factories.ConfirmedCollectiveBookingFactory

    on_success_num_queries = 1  # 1. get api key
    on_success_num_queries += 1  # 2. get collective booking
    on_success_num_queries += 1  # 3. get collective stock (lock for update)
    on_success_num_queries += 1  # 4. get collective booking (refresh)
    on_success_num_queries += 1  # 5. does pricing exists for collective booking?
    on_success_num_queries += 1  # 6. get finance events for booking
    on_success_num_queries += 1  # 7. update booking

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    @pytest.mark.parametrize(
        "booking_factory",
        [
            factories.ConfirmedCollectiveBookingFactory,
            factories.PendingCollectiveBookingFactory,
            factories.UsedCollectiveBookingFactory,
        ],
    )
    def test_should_cancel_booking(self, client, booking_factory):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(
            factory=booking_factory, venue=venue_provider.venue, provider=venue_provider.provider
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(booking, "status", models.CollectiveBookingStatus.CANCELLED):
            booking_id = booking.id
            with assert_num_queries(self.on_success_num_queries):
                self.assert_request_has_expected_result(
                    auth_client, url_params={"booking_id": booking_id}, expected_status_code=204
                )

    def test_cannot_cancel_cancelled_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        cancelled_booking = self.setup_base_resource(
            factory=factories.CancelledCollectiveBookingFactory,
            venue=venue_provider.venue,
            provider=venue_provider.provider,
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(cancelled_booking, "status"):
            booking_id = cancelled_booking.id

            expected_queries_count = 1  # 1. get api key
            expected_queries_count += 1  # 3. get collective booking
            expected_queries_count += 1  # 4. get collective stock (lock for update)
            expected_queries_count += 1  # 5. get collective booking (refresh)
            expected_queries_count += 1  # 6. does pricing exists for collective booking?
            expected_queries_count += 1  # 7. get finance events for booking
            expected_queries_count += 1  # 8. rollback
            expected_queries_count += 1  # 9. rollback (second one because of with atomic in cancel_collective_booking)

            with assert_num_queries(expected_queries_count):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=403,
                    expected_error_json={"code": "ALREADY_CANCELLED_BOOKING"},
                )

    def test_cannot_cancel_reimbursed_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        reimbursed_booking = self.setup_base_resource(
            factory=factories.ReimbursedCollectiveBookingFactory,
            venue=venue_provider.venue,
            provider=venue_provider.provider,
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(reimbursed_booking, "status"):
            booking_id = reimbursed_booking.id

            expected_queries_count = 1  # 1. get api key
            expected_queries_count += 1  # 3. get collective booking
            expected_queries_count += 1  # 4. get collective stock (lock for update)
            expected_queries_count += 1  # 5. get collective booking (refresh)
            expected_queries_count += 1  # 6. rollback
            expected_queries_count += 1  # 7. rollback (second one because of with atomic in cancel_collective_booking)

            with assert_num_queries(expected_queries_count):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=403,
                    expected_error_json={"code": "BOOKING_IS_REIMBURSED"},
                )

    def test_cannot_cancel_unknown_booking(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        expected_queries_count = 1  # 1. get api key
        expected_queries_count += 1  # 3. get collective booking
        expected_queries_count += 1  # 4. rollback

        with assert_num_queries(expected_queries_count):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": 0},
                expected_status_code=404,
                expected_error_json={"code": "BOOKING_NOT_FOUND"},
            )

    @patch("pcapi.core.educational.api.booking.finance_api")
    def test_unexpected_error_is_handled(self, mock_finance_api, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        mock_finance_api.cancel_latest_event.side_effect = [RuntimeError("test")]

        with assert_attribute_does_not_change(booking, "status"):
            booking_id = booking.id

            expected_queries_count = 1  # 1. get api key
            expected_queries_count += 1  # 3. get collective booking
            expected_queries_count += 1  # 4. get collective stock (lock for update)
            expected_queries_count += 1  # 5. get collective booking (refresh)
            expected_queries_count += 1  # 6. does pricing exists for collective booking?
            expected_queries_count += 1  # 7. rollback
            expected_queries_count += 1  # 8. rollback (second one because of with atomic in cancel_collective_booking)

            with assert_num_queries(expected_queries_count):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=500,
                    expected_error_json={"code": "FAILED_TO_CANCEL_BOOKING_TRY_AGAIN"},
                )


class UseCollectiveBookingTest(AdageMockEndpointHelper):
    endpoint_url = "/v2/collective/bookings/{booking_id}/use"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}
    default_factory = factories.ConfirmedCollectiveBookingFactory

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_use_confirmed_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        confirmed_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(confirmed_booking, "status", models.CollectiveBookingStatus.USED):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": confirmed_booking.id},
                expected_status_code=204,
            )

    @pytest.mark.parametrize(
        "booking_factory",
        [
            factories.PendingCollectiveBookingFactory,
            factories.UsedCollectiveBookingFactory,
            factories.CancelledCollectiveBookingFactory,
            factories.ReimbursedCollectiveBookingFactory,
        ],
    )
    def test_should_raise_403_when_status_is_not_confirmed(self, client, booking_factory):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(
            factory=booking_factory, venue=venue_provider.venue, provider=venue_provider.provider
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": booking.id},
                expected_status_code=403,
                expected_error_json={"code": "ONLY_CONFIRMED_BOOKING_CAN_BE_USED"},
            )

    def test_should_raise_404_when_booking_does_not_exist(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"booking_id": 0},
            expected_status_code=404,
            expected_error_json={"code": "BOOKING_NOT_FOUND"},
        )

    @patch("pcapi.routes.public.collective.endpoints.adage_mock.bookings.finance_api")
    def test_booking_not_used_in_case_of_internal_error(self, api_mock, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)

        api_mock.add_event.side_effect = [RuntimeError("test")]

        with assert_attribute_does_not_change(booking, "status"):
            self.assert_request_has_expected_result(
                auth_client,
                url_params={"booking_id": booking.id},
                expected_status_code=500,
                expected_error_json={"code": "FAILED_TO_USE_BOOKING_TRY_AGAIN_LATER"},
            )


class ResetCollectiveBookingTest(AdageMockEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/pending"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}
    default_factory = factories.PendingCollectiveBookingFactory

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_can_reset_pending_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)
        with assert_attribute_does_not_change(booking, "status"):
            expected_num_queries = 1  # 1. get api key
            expected_num_queries += 1  # 2. get collective booking (no update triggered since status does not change)

            booking_id = booking.id
            with assert_num_queries(expected_num_queries):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=204,
                )

    @pytest.mark.parametrize(
        "booking_factory", [factories.ConfirmedCollectiveBookingFactory, factories.CancelledCollectiveBookingFactory]
    )
    def test_can_reset_confirmed_booking(self, client, booking_factory):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(
            factory=booking_factory, venue=venue_provider.venue, provider=venue_provider.provider
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(booking, "status", models.CollectiveBookingStatus.PENDING):
            expected_num_queries = 1  # 1. get api key
            expected_num_queries += 1  # 2. get collective booking
            if booking_factory is factories.CancelledCollectiveBookingFactory:
                expected_num_queries += 1  # update booking (uncancel_booking)
            expected_num_queries += 1  # update booking (to PENDING)

            booking_id = booking.id
            with assert_num_queries(expected_num_queries):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=204,
                )

    @pytest.mark.parametrize(
        "booking_factory,expected_json",
        [
            (factories.UsedCollectiveBookingFactory, {"code": "CANNOT_SET_BACK_USED_BOOKING_TO_PENDING"}),
            (factories.ReimbursedCollectiveBookingFactory, {"code": "CANNOT_SET_BACK_REIMBURSED_BOOKING_TO_PENDING"}),
        ],
    )
    def test_cannot_reset_used_booking(self, client, booking_factory, expected_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(
            factory=booking_factory, venue=venue_provider.venue, provider=venue_provider.provider
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(booking, "status"):
            expected_num_queries = 1  # 1. get api key
            expected_num_queries += 1  # 3. get collective booking
            expected_num_queries += 1  # 4. rollback

            booking_id = booking.id
            with assert_num_queries(expected_num_queries):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=403,
                    expected_error_json=expected_json,
                )


class RepayCollectiveBookingTest(AdageMockEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/reimburse"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}
    default_factory = factories.UsedCollectiveBookingFactory

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_can_repay_used_booking(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        used_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        auth_client = client.with_explicit_token(plain_api_key)
        with assert_attribute_value_changes_to(used_booking, "status", models.CollectiveBookingStatus.REIMBURSED):
            booking_id = used_booking.id

            expected_num_queries = 1  # 1. get api key
            expected_num_queries += 1  # 2. get collective booking
            expected_num_queries += 1  # 3. update booking

            with assert_num_queries(expected_num_queries):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=204,
                )

    @pytest.mark.parametrize(
        "booking_factory,expected_json",
        [
            (factories.PendingCollectiveBookingFactory, {"code": "CANNOT_REIMBURSE_PENDING_BOOKING"}),
            (factories.CancelledCollectiveBookingFactory, {"code": "CANNOT_REIMBURSE_CANCELLED_BOOKING"}),
            (factories.ConfirmedCollectiveBookingFactory, {"code": "CANNOT_REIMBURSE_CONFIRMED_BOOKING"}),
            (factories.ReimbursedCollectiveBookingFactory, {"code": "CANNOT_REIMBURSE_REIMBURSED_BOOKING"}),
        ],
    )
    def test_should_raise_403_when_status_is_not_used(self, client, booking_factory, expected_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        booking = self.setup_base_resource(
            factory=booking_factory, venue=venue_provider.venue, provider=venue_provider.provider
        )
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(booking, "status"):
            booking_id = booking.id

            expected_num_queries = 1  # 1. get api key
            expected_num_queries += 1  # 2. get collective booking
            expected_num_queries += 1  # 3. rollback

            with assert_num_queries(expected_num_queries):
                self.assert_request_has_expected_result(
                    auth_client,
                    url_params={"booking_id": booking_id},
                    expected_status_code=403,
                    expected_error_json=expected_json,
                )


class BookCollectiveOfferTest(PublicAPIRestrictedEnvEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/offer/{offer_id}/book"
    endpoint_method = "post"
    default_path_params = {"offer_id": 1}
    default_factory = factories.CollectiveOfferFactory

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_can_book_collective_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=deposit.educationalInstitution,
        ).collectiveOffer

        offer_id = offer.id

        expected_num_queries = 1  # get api key
        expected_num_queries += 1  # get collective offer
        expected_num_queries += 1  # get stock (booking limit datetime)
        expected_num_queries += 1  # get venue
        expected_num_queries += 1  # search redactor
        expected_num_queries += 1  # save (new) redactor
        expected_num_queries += 1  # get institution (with program) based on UAI
        expected_num_queries += 1  # select (same) stock for update
        expected_num_queries += 1  # search for offer's bookings
        expected_num_queries += 1  # get educational year (filtered)
        expected_num_queries += 1  # create new booking
        expected_num_queries += 1  # get educational domain and collective domain
        expected_num_queries += 1  # get FF (during booking serialize for adage notify_prebooking)

        with assert_num_queries(expected_num_queries):
            response = self.assert_request_has_expected_result(
                auth_client,
                url_params={"offer_id": offer_id},
                expected_status_code=200,
            )

        assert response.json["bookingId"]
        assert response.json["bookingStatus"] == models.CollectiveBookingStatus.PENDING.value

        db.session.refresh(offer)
        bookings = offer.collectiveStock.collectiveBookings
        assert bookings
        assert len(bookings) == 1

        booking = bookings[0]
        assert booking.status == models.CollectiveBookingStatus.PENDING

    def test_cannot_book_inactive_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=deposit.educationalInstitution,
            collectiveOffer__isActive=False,
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=403,
            expected_error_json={"code": "OFFER_IS_NOT_BOOKABLE"},
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    @pytest.mark.parametrize(
        "validation_status",
        [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED],
    )
    def test_cannot_book_not_approved_offer(self, client, validation_status):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=deposit.educationalInstitution,
            collectiveOffer__validation=validation_status,
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=403,
            expected_error_json={"code": "OFFER_IS_NOT_BOOKABLE"},
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    def test_cannot_book_soldout_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        institution = deposit.educationalInstitution
        offer = factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__provider=venue_provider.provider,
            collectiveStock__collectiveOffer__venue=venue_provider.venue,
            collectiveStock__collectiveOffer__institution=institution,
        ).collectiveStock.collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=403,
            expected_error_json={"code": "OFFER_IS_NOT_BOOKABLE_BECAUSE_BOOKING_EXISTS"},
        )

        # offer is sold out because of used booking.
        # no new booking should have been created.
        db.session.refresh(offer)
        assert len(offer.collectiveStock.collectiveBookings) == 1

    def test_cannot_book_offer_without_institution(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=None,
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=403,
            expected_error_json={"code": "OFFER_IS_NOT_LINKED_TO_AN_INSTITUTION"},
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    def test_cannot_book_offer_if_educational_year_is_missing(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=factories.EducationalInstitutionFactory(),
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=403,
            expected_error_json={"code": "OFFERS_YEAR_NOT_FOUND"},
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    def test_cannot_book_offer_if_no_educational_year_matches_start(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            # deposit creates an educational year
            collectiveOffer__institution=deposit.educationalInstitution,
            # start will not match the educational year
            startDatetime=datetime.now(timezone.utc) + timedelta(weeks=512),
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=403,
            expected_error_json={"code": "OFFERS_YEAR_NOT_FOUND"},
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    def test_cannot_book_offer_if_unexpected_error(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=deposit.educationalInstitution,
        ).collectiveOffer

        with patch("pcapi.core.educational.api.booking.book_collective_offer") as mock:
            mock.side_effect = [RuntimeError("test")]

            self.assert_request_has_expected_result(
                auth_client,
                url_params={"offer_id": offer.id},
                expected_status_code=500,
                expected_error_json={"code": "OFFER_BOOKING_FAILED_TRY_AGAIN_LATER"},
            )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__institution=deposit.educationalInstitution
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client, url_params={"offer_id": offer.id}, expected_status_code=404
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        deposit = factories.EducationalDepositFactory(educationalYear=factories.EducationalCurrentYearFactory())
        offer = factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__institution=deposit.educationalInstitution,
        ).collectiveOffer

        self.assert_request_has_expected_result(
            auth_client,
            url_params={"offer_id": offer.id},
            expected_status_code=404,
        )

        db.session.refresh(offer)
        assert not offer.collectiveStock.collectiveBookings
