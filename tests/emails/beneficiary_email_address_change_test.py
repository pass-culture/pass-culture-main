import pytest

from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_address_change import get_confirmation_email_change_data
from pcapi.core.mails.transactional.users.email_address_change import get_information_email_change_data
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class AddressEmailChangeTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_should_return_dict_when_feature_toogle_false(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")

        # When
        data = get_information_email_change_data(user.firstName)
        data2 = get_confirmation_email_change_data(user.firstName, confirmation_link="ABCD123")

        # Then
        assert data == {"MJ-TemplateID": 2066067, "MJ-TemplateLanguage": True, "Vars": {"beneficiary_name": "Fabien"}}
        assert data2 == {
            "MJ-TemplateID": 2066065,
            "MJ-TemplateLanguage": True,
            "Vars": {"beneficiary_name": "Fabien", "confirmation_link": "ABCD123"},
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_should_return_sendinblue_data_when_feature_toggled(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        users_factories.ResetPasswordToken(user=user, value="ABCD123")

        # When
        data = get_information_email_change_data(user.firstName)
        data2 = get_confirmation_email_change_data(first_name=user.firstName, confirmation_link="ABCD123")

        # Then
        assert data.template == TransactionalEmail.EMAIL_ADDRESS_CHANGE_REQUEST
        assert data.params["FIRSTNAME"] == "Fabien"

        assert data2.template == TransactionalEmail.EMAIL_ADDRESS_CHANGE_CONFIRMATION
        assert data2.params["FIRSTNAME"] == "Fabien"
        assert data2.params["CONFIRMATION_LINK"] == "ABCD123"
