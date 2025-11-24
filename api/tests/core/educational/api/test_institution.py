import pytest
import time_machine

from pcapi.core.educational import factories
from pcapi.core.educational.api import institution as api


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="freeze")
def freeze_fixture():
    with time_machine.travel("2023-12-15 16:00:00"):
        yield


@pytest.fixture(name="current_year_deposit")
def current_year_deposit_fixture(freeze):
    educational_year = factories.EducationalCurrentYearFactory()

    return factories.EducationalDepositFactory(educationalYear=educational_year)


class GetEducationalInstitutionRemainingCreditTest:
    def test_used_offer(self, current_year_deposit):
        institution = current_year_deposit.educationalInstitution
        booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=current_year_deposit.educationalYear
        )

        res = api.get_current_year_remaining_credit(institution)
        assert res == current_year_deposit.amount - booking.collectiveStock.price

    def test_used_and_cancelled_and_pending_offers(self, current_year_deposit):
        """
        Cancelled and pending offers should be ignored
        """
        institution = current_year_deposit.educationalInstitution

        factories.CancelledCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=current_year_deposit.educationalYear
        )
        used_booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=current_year_deposit.educationalYear
        )

        res = api.get_current_year_remaining_credit(institution)
        assert res == current_year_deposit.amount - used_booking.collectiveStock.price

    def test_no_bookings(self, current_year_deposit):
        institution = current_year_deposit.educationalInstitution
        res = api.get_current_year_remaining_credit(institution)
        assert res == current_year_deposit.amount
