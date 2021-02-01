from pcapi.emails.pro_waiting_validation import retrieve_data_for_pro_user_waiting_offerer_validation_email
from pcapi.model_creators.generic_creators import create_offerer


class MakeProUserWaitingForValidationByAdminEmailTest:
    def test_should_return_mailjet_data(self):
        # Given
        offerer = create_offerer(name="Bar des amis")

        # When
        mailjet_data = retrieve_data_for_pro_user_waiting_offerer_validation_email(offerer)

        # Then
        assert mailjet_data == {
            "MJ-TemplateID": 778329,
            "MJ-TemplateLanguage": True,
            "Vars": {"nom_structure": "Bar des amis"},
        }
