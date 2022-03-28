from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
from pcapi.scripts.change_some_pro_users_to_beneficiary import change_pro_users_to_beneficiary


@pytest.mark.usefixtures("db_session")
def test_should_change_pro_users_to_beneficiary():
    # given
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)
    pro_1 = users_factories.ProFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE, needsToFillCulturalSurvey=False)
    pro_2 = users_factories.ProFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE)
    offerers_factories.UserOffererFactory(user=pro_1)
    offerers_factories.UserOffererFactory(user=pro_1)
    offerers_factories.UserOffererFactory()  # placeholder, to be kept
    pro_users_list_to_change = [pro_1.id, pro_2.id]

    # when
    change_pro_users_to_beneficiary(pro_users_list_to_change)

    # then
    assert pro_1.has_beneficiary_role
    assert pro_1.has_beneficiary_role
    assert not pro_1.has_pro_role
    assert pro_1.needsToFillCulturalSurvey
    assert pro_1.wallet_balance == 300
    assert pro_2.has_beneficiary_role
    assert pro_2.has_beneficiary_role
    assert not pro_2.has_pro_role
    assert pro_2.needsToFillCulturalSurvey
    assert pro_2.wallet_balance == 300
    assert offerers_models.UserOfferer.query.count() == 1
