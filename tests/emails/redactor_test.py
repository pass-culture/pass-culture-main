from freezegun import freeze_time

from pcapi.core.users import factories as users_factories
from pcapi.emails import redactor


class GetActivationEmailRedactorTest:
    @freeze_time("2021-06-15 09:00:00")
    def test_return_dict_for_native_eligible_project_redactor(self):
        # Given
        redactor_user = users_factories.InstitutionalProjectRedactorFactory(email="cecilia+test@ac-versailles.fr")
        token = users_factories.EmailValidationToken.build(user=redactor_user)

        # When
        activation_email_data = redactor.get_activation_email_data_for_redactor(redactor_user, token)

        # Then
        assert activation_email_data["Vars"]["lien_validation_mail"]
        assert "email%3Dcecilia%252Btest%2540ac-versailles.fr" in activation_email_data["Vars"]["lien_validation_mail"]
