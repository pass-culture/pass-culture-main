from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories
from pcapi.scripts.beneficiary.send_mail_after_idcheck_outage import _get_eligible_users_created_between


pytestmark = pytest.mark.usefixtures("db_session")


class SendMailAfterIdcheckOutageTest:
    @freeze_time("2018-01-01 01:00:00")
    def test_get_eligible_users_created_between(self, app):
        ELIGIBLE_CONDTIONS = {"dateCreated": datetime.now(), "roles": []}
        # 19 yo
        factories.UserFactory(dateOfBirth=datetime(1999, 1, 1), **ELIGIBLE_CONDTIONS)
        user_just_18_in_eligible_area = factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), **ELIGIBLE_CONDTIONS)
        # Beneficiary
        factories.BeneficiaryGrant18Factory(
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime.now(),
        )
        # Admin
        factories.AdminFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime.now())
        # Pro
        pro_user = factories.ProFactory(dateOfBirth=datetime(2000, 1, 1), **ELIGIBLE_CONDTIONS)
        offers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        factories.UserFactory(dateOfBirth=datetime(2000, 1, 2), **ELIGIBLE_CONDTIONS)

        result = _get_eligible_users_created_between(
            datetime.now() - timedelta(days=1), datetime.now() + timedelta(minutes=1)
        )

        assert {u.id for u in result} == {user_just_18_in_eligible_area.id}
