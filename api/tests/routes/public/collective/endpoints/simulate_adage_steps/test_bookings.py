import contextlib
import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.testing import override_features
from pcapi.models import db
from pcapi.routes.adage.v1.serialization import constants

from tests.routes.public.helpers import PublicAPIRestrictedEnvEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="current_year")
def current_year_fixture():
    return factories.EducationalYearFactory(
        beginningDate=datetime.datetime(factories._get_current_educational_year(), 9, 1),
        expirationDate=datetime.datetime(factories._get_current_educational_year() + 1, 8, 31, 23, 59),
    )


@pytest.fixture(name="institution")
def institution_fixture(current_year):
    return factories.EducationalDepositFactory(educationalYear=current_year).educationalInstitution


@pytest.fixture(name="pending_booking")
def pending_booking_fixture(current_year, institution):
    return factories.PendingCollectiveBookingFactory(educationalYear=current_year, educationalInstitution=institution)


@pytest.fixture(name="confirmed_booking")
def confirmed_booking_fixture(current_year, institution):
    return factories.ConfirmedCollectiveBookingFactory(educationalYear=current_year, educationalInstitution=institution)


@pytest.fixture(name="used_booking")
def used_booking_fixture(current_year, institution):
    return factories.UsedCollectiveBookingFactory(
        educationalYear=current_year,
        educationalInstitution=institution,
    )


@pytest.fixture(name="reimbursed_booking")
def reimbursed_booking_fixture(current_year, institution):
    return factories.ReimbursedCollectiveBookingFactory(
        educationalYear=current_year, educationalInstitution=institution
    )


@pytest.fixture(name="cancelled_booking")
def cancelled_booking_fixture(current_year, institution):
    return factories.CancelledCollectiveBookingFactory(educationalYear=current_year, educationalInstitution=institution)


@contextlib.contextmanager
def assert_status_changes_to(booking, expected_status):
    previous_status = booking.status

    yield

    db.session.refresh(booking)
    assert booking.status != previous_status
    assert booking.status == expected_status


@contextlib.contextmanager
def assert_status_does_not_change(booking):
    previous_status = booking.status

    yield

    db.session.refresh(booking)
    assert booking.status == previous_status


class ConfirmCollectiveBookingTest(PublicAPIRestrictedEnvEndpointHelper):
    endpoint_url = "/v2/collective/adage_mock/bookings/{booking_id}/confirm"
    endpoint_method = "post"
    default_path_params = {"booking_id": 1}

    def setup_method(self):
        self.plain_api_key, _ = self.setup_provider()

    def get_authenticated_client(self, client):
        if not hasattr(self, "_authenticated_client"):
            self._authenticated_client = client.with_explicit_token(self.plain_api_key)
        return self._authenticated_client

    def test_confirm_pending_booking(self, client, pending_booking):
        with assert_status_changes_to(pending_booking, models.CollectiveBookingStatus.CONFIRMED):
            self.confirm_booking(client, pending_booking.id, status_code=204)

    def test_confirm_confirmed_booking(self, client, confirmed_booking):
        with assert_status_does_not_change(confirmed_booking):
            self.confirm_booking(client, confirmed_booking.id, status_code=204)

    def test_confirm_used_booking(self, client, used_booking):
        error = {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}

        with assert_status_does_not_change(used_booking):
            self.confirm_booking(client, used_booking.id, status_code=403, json_error=error)

    def test_confirm_reimbursed_booking(self, client, reimbursed_booking):
        error = {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}

        with assert_status_does_not_change(reimbursed_booking):
            self.confirm_booking(client, reimbursed_booking.id, status_code=403, json_error=error)

    def test_confirm_cancelled_booking(self, client, cancelled_booking):
        error = {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}

        with assert_status_does_not_change(cancelled_booking):
            self.confirm_booking(client, cancelled_booking.id, status_code=403, json_error=error)

    def test_confirm_when_insufficient_fund(self, client, institution, pending_booking):
        for deposit in institution.deposits:
            deposit.amount = 0

        error = {"code": "INSUFFICIENT_FUND"}
        with assert_status_does_not_change(pending_booking):
            self.confirm_booking(client, pending_booking.id, status_code=403, json_error=error)

    @override_features(ENABLE_EAC_FINANCIAL_PROTECTION=True)
    def test_confirm_when_insufficient_ministry_fund(self, client, used_booking, pending_booking):
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
        with assert_status_does_not_change(pending_booking):
            self.confirm_booking(client, pending_booking.id, status_code=403, json_error=error)

    def test_confirm_when_insufficient_temporary_fund(self, client, institution, pending_booking):
        for deposit in institution.deposits:
            deposit.amount = 0
            deposit.isFinal = False

        error = {"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"}
        with assert_status_does_not_change(pending_booking):
            self.confirm_booking(client, pending_booking.id, status_code=403, json_error=error)

    def test_confirm_unknown_booking(self, client):
        error = {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}
        self.confirm_booking(client, 0, status_code=404, json_error=error)

    def test_confirm_unknown_deposit(self, client, institution, pending_booking):
        for deposit in institution.deposits:
            deposit.educationalYear = factories.EducationalYearFactory()

        error = {"code": "DEPOSIT_NOT_FOUND"}
        with assert_status_does_not_change(pending_booking):
            self.confirm_booking(client, pending_booking.id, status_code=404, json_error=error)

    def confirm_booking(self, client, booking_id, status_code, json_error=None):
        response = self.send_request(self.get_authenticated_client(client), url_params={"booking_id": booking_id})

        assert response.status_code == status_code
        if json_error:
            for key, msg in json_error.items():
                assert response.json.get(key) == msg
