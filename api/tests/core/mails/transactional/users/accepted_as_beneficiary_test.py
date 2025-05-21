import pytest

from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.accepted_as_beneficiary import get_accepted_as_beneficiary_email_v3_data
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class GetAcceptedAsBeneficiaryEmailSendinblueTest:
    def test_return_correct_email_metadata(self):
        # Given
        user = users_factories.BeneficiaryFactory.create(email="fabien+test@example.net", deposit__amount=42)

        # When
        email = get_accepted_as_beneficiary_email_v3_data(user)

        # Then
        assert email.template == TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value
        assert email.params == {"CREDIT": 150}
