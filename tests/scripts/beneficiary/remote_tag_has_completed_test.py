from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock

import pytest

from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import User
from pcapi.scripts.beneficiary import remote_tag_has_completed

from tests.scripts.beneficiary.fixture import make_new_beneficiary_application_details


NOW = datetime.utcnow()
ONE_WEEK_AGO = NOW - timedelta(days=7)


@pytest.mark.usefixtures("db_session")
def test_tag_user_had_completed_id_check():
    # given
    recieved_beneficiary = UserFactory(hasCompletedIdCheck=False)
    already_beneficiary = BeneficiaryGrant18Factory(hasCompletedIdCheck=True)
    initiated_beneficiary = UserFactory(hasCompletedIdCheck=False)

    get_all_application_ids = Mock(return_value=[123, 456, 789])

    get_details = Mock()
    get_details.side_effect = [
        make_new_beneficiary_application_details(123, "received"),
        make_new_beneficiary_application_details(456, "received"),
        make_new_beneficiary_application_details(789, "initiated"),
    ]

    already_existing_user = Mock()
    already_existing_user.side_effect = [recieved_beneficiary, already_beneficiary, initiated_beneficiary]

    # when
    remote_tag_has_completed.run(
        ONE_WEEK_AGO,
        procedure_id=6712558,
        get_all_applications_ids=get_all_application_ids,
        get_details=get_details,
        already_existing_user=already_existing_user,
    )

    assert User.query.filter(User.hasCompletedIdCheck.is_(True)).count() == 3
