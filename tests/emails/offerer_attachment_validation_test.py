import pytest

from pcapi.emails.offerer_attachment_validation import retrieve_data_for_offerer_attachment_validation_email
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class ProOffererAttachmentValidationEmailTest:
    def test_email(self):
        # Given
        offerer = create_offerer(name="Le Théâtre SAS")
        pro_user = create_user(email="pro@example.com")
        user_offerer = create_user_offerer(pro_user, offerer)

        repository.save(pro_user, user_offerer)

        # When
        offerer_attachment_validation_email = retrieve_data_for_offerer_attachment_validation_email(user_offerer)

        # Then
        assert offerer_attachment_validation_email == {
            "MJ-TemplateID": 778756,
            "MJ-TemplateLanguage": True,
            "Vars": {"nom_structure": "Le Théâtre SAS"},
        }
