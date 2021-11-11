from pcapi.emails.new_offerer_validation import retrieve_data_for_new_offerer_validation_email
from pcapi.model_creators.generic_creators import create_offerer


class MakeNewOffererValidationEmailTest:
    def test_email(self):
        # Given
        offerer = create_offerer(name="Le Théâtre SAS")

        # When
        new_offerer_validation_email = retrieve_data_for_new_offerer_validation_email(offerer)

        # Then
        assert new_offerer_validation_email == {
            "MJ-TemplateID": 778723,
            "MJ-TemplateLanguage": True,
            "Vars": {"offerer_name": "Le Théâtre SAS"},
        }
