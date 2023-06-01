from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.educational.api.institution as api
import pcapi.core.educational.factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="freeze")
def freeze_fixture():
    with freeze_time("2023-12-15 16:00:00"):
        yield


@pytest.fixture(name="current_year_deposit")
def current_year_deposit_fixture(freeze):
    now = datetime.utcnow()

    return educational_factories.EducationalDepositFactory(
        educationalYear__beginningDate=datetime(now.year, 9, 1),
        educationalYear__expirationDate=datetime(now.year + 1, 8, 31),
    )


class GetEducationalInstitutionRemainingCreditTest:
    def test_used_offer(self, current_year_deposit):
        institution = current_year_deposit.educationalInstitution
        booking = educational_factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=current_year_deposit.educationalYear
        )

        res = api.get_current_year_remaining_credit(institution)
        assert res == current_year_deposit.get_amount() - booking.collectiveStock.price

    def test_used_and_cancelled_and_pending_offers(self, current_year_deposit):
        """
        Cancelled and pending offers should be ignored
        """
        institution = current_year_deposit.educationalInstitution

        educational_factories.CancelledCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=current_year_deposit.educationalYear
        )
        used_booking = educational_factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=current_year_deposit.educationalYear
        )

        res = api.get_current_year_remaining_credit(institution)
        assert res == current_year_deposit.get_amount() - used_booking.collectiveStock.price

    def test_no_bookings(self, current_year_deposit):
        institution = current_year_deposit.educationalInstitution
        res = api.get_current_year_remaining_credit(institution)
        assert res == current_year_deposit.get_amount()
