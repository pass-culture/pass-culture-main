import pytest

from pcapi.core.educational import factories
from pcapi.core.educational.api import institution as api


pytestmark = pytest.mark.usefixtures("db_session")


class GetEducationalInstitutionRemainingCreditTest:
    def test_used_offer(self):
        year = factories.EducationalCurrentYearFactory()
        deposit = factories.EducationalDepositFactory(educationalYear=year)
        institution = deposit.educationalInstitution

        booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit
        )

        res = api.get_current_year_remaining_credit(institution)
        assert res == deposit.amount - booking.collectiveStock.price

    def test_used_and_cancelled_and_pending_offers(self):
        """
        Cancelled and pending offers should be ignored
        """
        year = factories.EducationalCurrentYearFactory()
        deposit = factories.EducationalDepositFactory(educationalYear=year)
        institution = deposit.educationalInstitution

        factories.PendingCollectiveBookingFactory(educationalInstitution=institution, educationalYear=year)
        factories.CancelledCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit
        )
        used_booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit
        )

        res = api.get_current_year_remaining_credit(institution)
        assert res == deposit.amount - used_booking.collectiveStock.price

    def test_no_bookings(self):
        year = factories.EducationalCurrentYearFactory()
        deposit = factories.EducationalDepositFactory(educationalYear=year)
        institution = deposit.educationalInstitution

        res = api.get_current_year_remaining_credit(institution)
        assert res == deposit.amount
