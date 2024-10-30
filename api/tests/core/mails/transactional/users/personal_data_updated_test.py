import dataclasses

import pytest

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.personal_data_updated import send_beneficiary_personal_data_updated
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class PersonalDataUpdatedTest:
    def test_nothing_updated(self) -> None:
        user = users_factories.UserFactory()
        assert not send_beneficiary_personal_data_updated(user)
        assert len(mails_testing.outbox) == 0

    @pytest.mark.parametrize(
        "parameter,expected_updated_field",
        [
            ("is_first_name_updated", "FIRST_NAME"),
            ("is_last_name_updated", "LAST_NAME"),
            ("is_email_updated", "EMAIL"),
            ("is_phone_number_updated", "PHONE_NUMBER"),
        ],
    )
    def test_single_field_updated(self, parameter, expected_updated_field) -> None:
        user = users_factories.UserFactory()
        assert send_beneficiary_personal_data_updated(user, **{parameter: True})
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": user.firstName,
            "LASTNAME": user.lastName,
            "UPDATED_FIELD": expected_updated_field,
        }

    def test_two_fields_updated(self) -> None:
        user = users_factories.UserFactory()
        assert send_beneficiary_personal_data_updated(user, is_last_name_updated=True, is_email_updated=True)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": user.firstName,
            "LASTNAME": user.lastName,
            "UPDATED_FIELD": "EMAIL,LAST_NAME",
        }

    def test_all_fields_updated(self) -> None:
        user = users_factories.UserFactory()
        assert send_beneficiary_personal_data_updated(
            user,
            is_first_name_updated=True,
            is_last_name_updated=True,
            is_email_updated=True,
            is_phone_number_updated=True,
        )
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.PERSONAL_DATA_UPDATED_FROM_BACKOFFICE.value
        )
        assert mails_testing.outbox[0]["params"] == {
            "FIRSTNAME": user.firstName,
            "LASTNAME": user.lastName,
            "UPDATED_FIELD": "EMAIL,FIRST_NAME,LAST_NAME,PHONE_NUMBER",
        }
