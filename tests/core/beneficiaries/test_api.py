import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.beneficiaries import api
from pcapi.core.beneficiaries import exceptions
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class CreateBeneficiaryTest:
    def test_with_ineligible_user_raises_exception(self):
        user = users_factories.UserFactory.build(isBeneficiary=False)
        with pytest.raises(exceptions.NotEligible):
            api.activate_beneficiary(user, "test")

    def test_with_eligible_user(self):
        eligible_date = datetime.date.today() - relativedelta(years=18, days=30)
        user = users_factories.UserFactory(isBeneficiary=False, dateOfBirth=eligible_date)
        user = api.activate_beneficiary(user, "test")
        assert user.isBeneficiary
        assert len(user.deposits) == 1
