import datetime
from unittest.mock import patch

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.routes.adage.v1.serialization import constants

from tests.routes.public.helpers import PublicAPIRestrictedEnvEndpointHelper
from tests.routes.public.helpers import assert_attribute_does_not_change
from tests.routes.public.helpers import assert_attribute_value_changes_to


pytestmark = pytest.mark.usefixtures("db_session")


def _get_offerer(provider):
    offerer = offerers_models.OffererProvider.query.filter_by(provider=provider).first().offerer

    if not offerer:
        offerer = providers_factories.OffererProviderFactory(
            provider=provider,
        ).offerer

    return offerer


def _build_current_year():
    return factories.EducationalYearFactory(
        beginningDate=datetime.datetime(factories._get_current_educational_year(), 9, 1),
        expirationDate=datetime.datetime(factories._get_current_educational_year() + 1, 8, 31, 23, 59),
    )


def _build_booking(factory, provider, venue=None, year=None, institution=None):
    if not year:
        year = _build_current_year()

    if not institution:
        institution = factories.EducationalDepositFactory(educationalYear=year).educationalInstitution

    if not venue:
        offerer = _get_offerer(provider)
        venue = providers_factories.VenueProviderFactory(venue__managingOfferer=offerer, provider=provider).venue

    return factory(
        educationalYear=year,
        educationalInstitution=institution,
        collectiveStock__collectiveOffer__provider=provider,
        collectiveStock__collectiveOffer__venue=venue,
    )


def build_pending_booking(provider, venue=None, institution=None, year=None):
    return _build_booking(
        factory=factories.PendingCollectiveBookingFactory,
        provider=provider,
        venue=venue,
        institution=institution,
        year=year,
    )


def build_confirmed_booking(provider, venue=None, institution=None, year=None):
    return _build_booking(
        factory=factories.ConfirmedCollectiveBookingFactory,
        provider=provider,
        venue=venue,
        institution=institution,
        year=year,
    )


def build_used_booking(provider, venue=None, institution=None, year=None):
    return _build_booking(
        factory=factories.UsedCollectiveBookingFactory,
        provider=provider,
        venue=venue,
        institution=institution,
        year=year,
    )


def build_reimbursed_booking(provider, venue=None, institution=None, year=None):
    return _build_booking(
        factory=factories.ReimbursedCollectiveBookingFactory,
        provider=provider,
        venue=venue,
        institution=institution,
        year=year,
    )


def build_cancelled_booking(provider, venue=None, institution=None, year=None):
    return _build_booking(
        factory=factories.CancelledCollectiveBookingFactory,
        provider=provider,
        venue=venue,
        institution=institution,
        year=year,
    )


class ConfirmCollectiveBookingTest(PublicAPIRestrictedEnvEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/confirm"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}

    def test_confirm_pending_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(pending_booking, "status", models.CollectiveBookingStatus.CONFIRMED):
            self.confirm_booking(auth_client, pending_booking.id, status_code=204)

    def test_confirm_confirmed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        confirmed_booking = build_confirmed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(confirmed_booking, "status"):
            self.confirm_booking(auth_client, confirmed_booking.id, status_code=204)

    def test_confirm_used_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        used_booking = build_used_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}

        with assert_attribute_does_not_change(used_booking, "status"):
            self.confirm_booking(auth_client, used_booking.id, status_code=403, json_error=error)

    def test_confirm_reimbursed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        reimbursed_booking = build_reimbursed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}

        with assert_attribute_does_not_change(reimbursed_booking, "status"):
            self.confirm_booking(auth_client, reimbursed_booking.id, status_code=403, json_error=error)

    def test_confirm_cancelled_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        cancelled_booking = build_cancelled_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}

        with assert_attribute_does_not_change(cancelled_booking, "status"):
            self.confirm_booking(auth_client, cancelled_booking.id, status_code=403, json_error=error)

    def test_confirm_when_insufficient_fund(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        for deposit in pending_booking.educationalInstitution.deposits:
            deposit.amount = 0

        error = {"code": "INSUFFICIENT_FUND"}
        with assert_attribute_does_not_change(pending_booking, "status"):
            self.confirm_booking(auth_client, pending_booking.id, status_code=403, json_error=error)

    @override_features(ENABLE_EAC_FINANCIAL_PROTECTION=True)
    def test_confirm_when_insufficient_ministry_fund(self, client):
        plain_api_key, provider = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        current_year = _build_current_year()

        pending_booking = build_pending_booking(provider, year=current_year)

        venue = pending_booking.collectiveStock.collectiveOffer.venue
        institution = pending_booking.educationalInstitution

        used_booking = build_used_booking(provider, venue=venue, institution=institution, year=current_year)

        # ensure offer's stock start between september and december
        # because this validation is not ran after and before that.
        start = pending_booking.collectiveStock.startDatetime.replace(month=10)
        pending_booking.collectiveStock.startDatetime = start
        pending_booking.collectiveStock.beginningDatetime = start

        # pending booking price is within the the institution's budget
        # but some special rules apply at the end of the year: the
        # overall used budget must be at most 1/3 of the total.
        institution = used_booking.educationalInstitution
        deposit_amount = sum(deposit.amount for deposit in institution.deposits)
        used_booking.collectiveStock.price = deposit_amount / 3

        error = {"code": "INSUFFICIENT_MINISTRY_FUND"}
        with assert_attribute_does_not_change(pending_booking, "status"):
            self.confirm_booking(auth_client, pending_booking.id, status_code=403, json_error=error)

    def test_confirm_when_insufficient_temporary_fund(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        for deposit in pending_booking.educationalInstitution.deposits:
            deposit.amount = 0
            deposit.isFinal = False

        error = {"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"}
        with assert_attribute_does_not_change(pending_booking, "status"):
            self.confirm_booking(auth_client, pending_booking.id, status_code=403, json_error=error)

    def test_confirm_unknown_booking(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}
        self.confirm_booking(auth_client, 0, status_code=404, json_error=error)

    def test_confirm_unknown_deposit(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        for deposit in pending_booking.educationalInstitution.deposits:
            deposit.educationalYear = factories.EducationalYearFactory()

        error = {"code": "DEPOSIT_NOT_FOUND"}
        with assert_attribute_does_not_change(pending_booking, "status"):
            self.confirm_booking(auth_client, pending_booking.id, status_code=404, json_error=error)

    def confirm_booking(self, client, booking_id, status_code, json_error=None):
        self.assert_request_has_expected_result(
            client,
            url_params={"booking_id": booking_id},
            expected_status_code=status_code,
            expected_error_json=json_error,
        )


class CancelCollectiveBookingTest(PublicAPIRestrictedEnvEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/cancel"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}

    # 1. get api key
    # 2. get FF
    # 3. get collective booking
    # 4. get collective stock (lock for update)
    # 5. get collective booking (refresh)
    # 6. does pricing exists for collective booking?
    # 7. get finance events for booking
    # 8. update booking
    on_success_num_queries = 8

    def test_can_cancel_confirmed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        confirmed_booking = build_confirmed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(confirmed_booking, "status", models.CollectiveBookingStatus.CANCELLED):
            booking_id = confirmed_booking.id
            with assert_num_queries(self.on_success_num_queries):
                self.cancel_booking(auth_client, booking_id, status_code=204)

    def test_can_cancel_pending_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(pending_booking, "status", models.CollectiveBookingStatus.CANCELLED):
            booking_id = pending_booking.id
            with assert_num_queries(self.on_success_num_queries):
                self.cancel_booking(auth_client, booking_id, status_code=204)

    def test_can_cancel_used_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        used_booking = build_used_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(used_booking, "status", models.CollectiveBookingStatus.CANCELLED):
            booking_id = used_booking.id
            with assert_num_queries(self.on_success_num_queries):
                self.cancel_booking(auth_client, booking_id, status_code=204)

    def test_cannot_cancel_cancelled_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        cancelled_booking = build_cancelled_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "ALREADY_CANCELLED_BOOKING"}
        with assert_attribute_does_not_change(cancelled_booking, "status"):
            booking_id = cancelled_booking.id
            # 1. get api key
            # 2. get FF
            # 3. get collective booking
            # 4. get collective stock (lock for update)
            # 5. get collective booking (refresh)
            # 6. does pricing exists for collective booking?
            # 7. get finance events for booking
            # 8. rollback
            with assert_num_queries(8):
                self.cancel_booking(auth_client, booking_id, status_code=403, json_error=error)

    def test_cannot_cancel_reimbursed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        reimbursed_booking = build_reimbursed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "BOOKING_IS_REIMBURSED"}
        with assert_attribute_does_not_change(reimbursed_booking, "status"):
            booking_id = reimbursed_booking.id
            # 1. get api key
            # 2. get FF
            # 3. get collective booking
            # 4. get collective stock (lock for update)
            # 5. get collective booking (refresh)
            # 6. rollback
            with assert_num_queries(6):
                self.cancel_booking(auth_client, booking_id, status_code=403, json_error=error)

    def test_cannot_cancel_unknown_booking(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "BOOKING_NOT_FOUND"}

        # 1. get api key
        # 2. get FF
        # 3. get collective booking
        with assert_num_queries(3):
            self.cancel_booking(auth_client, 0, status_code=404, json_error=error)

    def test_cannot_cancel_booking_not_linked_to_key(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        booking = factories.CollectiveBookingFactory()
        error = {"code": "BOOKING_NOT_FOUND"}

        with assert_attribute_does_not_change(booking, "status"):
            booking_id = booking.id
            # 1. get api key
            # 2. get FF
            # 3. get collective booking
            with assert_num_queries(3):
                self.cancel_booking(auth_client, booking_id, status_code=404, json_error=error)

    @patch("pcapi.core.educational.api.booking.finance_api")
    def test_unexpected_error_is_handled(self, mock_finance_api, client):
        plain_api_key, provider = self.setup_provider()
        confirmed_booking = build_confirmed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        mock_finance_api.cancel_latest_event.side_effect = [RuntimeError("test")]

        error = {"code": "FAILED_TO_CANCEL_BOOKING_TRY_AGAIN"}

        with assert_attribute_does_not_change(confirmed_booking, "status"):
            booking_id = confirmed_booking.id
            # 1. get api key
            # 2. get FF
            # 3. get collective booking
            # 4. get collective stock (lock for update)
            # 5. get collective booking (refresh)
            # 6. does pricing exists for collective booking?
            # 7. get finance events for booking
            # 8. rollback
            with assert_num_queries(8):
                self.cancel_booking(auth_client, booking_id, status_code=500, json_error=error)

    def cancel_booking(self, client, booking_id, status_code, json_error=None):
        self.assert_request_has_expected_result(
            client,
            url_params={"booking_id": booking_id},
            expected_status_code=status_code,
            expected_error_json=json_error,
        )


class UseCollectiveBookingTest(PublicAPIRestrictedEnvEndpointHelper):
    endpoint_url = "/v2/collective/bookings/{booking_id}/use"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}

    def test_use_confirmed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        confirmed_booking = build_confirmed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_value_changes_to(confirmed_booking, "status", models.CollectiveBookingStatus.USED):
            self.use_booking(auth_client, confirmed_booking.id, status_code=204)

    def test_use_pending_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "ONLY_CONFIRMED_BOOKING_CAN_BE_USED"}
        with assert_attribute_does_not_change(pending_booking, "status"):
            self.use_booking(auth_client, pending_booking.id, status_code=403, json_error=error)

    def test_use_used_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        used_booking = build_used_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)
        error = {"code": "ONLY_CONFIRMED_BOOKING_CAN_BE_USED"}
        with assert_attribute_does_not_change(used_booking, "status"):
            self.use_booking(auth_client, used_booking.id, status_code=403, json_error=error)

    def test_use_cancelled_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        cancelled_booking = build_cancelled_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "ONLY_CONFIRMED_BOOKING_CAN_BE_USED"}
        with assert_attribute_does_not_change(cancelled_booking, "status"):
            self.use_booking(auth_client, cancelled_booking.id, status_code=403, json_error=error)

    def test_use_reimbursed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        reimbursed_booking = build_reimbursed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "ONLY_CONFIRMED_BOOKING_CAN_BE_USED"}
        with assert_attribute_does_not_change(reimbursed_booking, "status"):
            self.use_booking(auth_client, reimbursed_booking.id, status_code=403, json_error=error)

    def test_use_unknown_booking(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        error = {"code": "BOOKING_NOT_FOUND"}
        self.use_booking(auth_client, 0, status_code=404, json_error=error)

    @patch("pcapi.routes.public.collective.endpoints.simulate_adage_steps.bookings.finance_api")
    def test_booking_not_used_in_case_of_internal_error(self, api_mock, client):
        plain_api_key, provider = self.setup_provider()
        confirmed_booking = build_confirmed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)
        api_mock.add_event.side_effect = [RuntimeError("test")]

        with assert_attribute_does_not_change(confirmed_booking, "status"):
            error = {"code": "FAILED_TO_USE_BOOKING_TRY_AGAIN_LATER"}
            self.use_booking(auth_client, confirmed_booking.id, status_code=500, json_error=error)

    def use_booking(self, client, booking_id, status_code, json_error=None):
        self.assert_request_has_expected_result(
            client,
            url_params={"booking_id": booking_id},
            expected_status_code=status_code,
            expected_error_json=json_error,
        )


class RepayCollectiveBookingTest(PublicAPIRestrictedEnvEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/repay"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}

    def test_cannot_repay_booking_not_linked_to_key(self, client):
        plain_api_key, _ = self.setup_provider()
        auth_client = client.with_explicit_token(plain_api_key)

        booking = factories.CollectiveBookingFactory()
        with assert_attribute_does_not_change(booking, "status"):
            self.repay_booking(auth_client, booking.id, status_code=404)

    def test_can_repay_used_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        used_booking = build_used_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)
        with assert_attribute_value_changes_to(used_booking, "status", models.CollectiveBookingStatus.REIMBURSED):
            booking_id = used_booking.id

            expected_num_queries = 1  # 1. get api key
            expected_num_queries += 1  # 2. get FF
            expected_num_queries += 1  # 3. get collective booking
            expected_num_queries += 1  # 4. update booking
            with assert_num_queries(expected_num_queries):
                self.repay_booking(auth_client, booking_id, status_code=204)

    def test_cannot_repay_pending_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        pending_booking = build_pending_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(pending_booking, "status"):
            self.repay_booking(auth_client, pending_booking.id, status_code=403)

    def test_cannot_repay_cancelled_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        cancelled_booking = build_cancelled_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(cancelled_booking, "status"):
            self.repay_booking(auth_client, cancelled_booking.id, status_code=403)

    def test_cannot_repay_confirmed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        confirmed_booking = build_confirmed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(confirmed_booking, "status"):
            self.repay_booking(auth_client, confirmed_booking.id, status_code=403)

    def test_cannot_repay_reimbursed_booking(self, client):
        plain_api_key, provider = self.setup_provider()
        reimbursed_booking = build_reimbursed_booking(provider)
        auth_client = client.with_explicit_token(plain_api_key)

        with assert_attribute_does_not_change(reimbursed_booking, "status"):
            self.repay_booking(auth_client, reimbursed_booking.id, status_code=403)

    def repay_booking(self, client, booking_id, status_code, json_error=None):
        response = self.send_request(client, url_params={"booking_id": booking_id})

        assert response.status_code == status_code
        if json_error:
            for key, msg in json_error.items():
                assert response.json.get(key) == msg
