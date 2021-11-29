from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.models.user_offerer import UserOfferer
from pcapi.repository import repository
from pcapi.scripts.change_some_pro_users_to_beneficiary import change_pro_users_to_beneficiary


@pytest.mark.usefixtures("db_session")
def test_should_change_pro_users_to_beneficiary(app):
    # given
    offerer_1 = create_offerer(siren="987654321")
    offerer_2 = create_offerer(siren="567890342")
    offerer_3 = create_offerer(siren="345987987")
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.now() - relativedelta(years=18, months=4)
    pro_1 = users_factories.ProFactory(
        dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE, email="email@example.com", needsToFillCulturalSurvey=False
    )
    pro_2 = users_factories.ProFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE, email="email2@example.com")
    pro_3 = users_factories.ProFactory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE, email="email3@example.com")
    user_offerer_1 = create_user_offerer(pro_1, offerer_1)
    user_offerer_2 = create_user_offerer(pro_1, offerer_2)
    user_offerer_3 = create_user_offerer(pro_3, offerer_3)
    repository.save(user_offerer_1, user_offerer_2, user_offerer_3)
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
    assert UserOfferer.query.count() == 1
