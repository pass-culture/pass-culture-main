import pytest

from pcapi.core.offers.factories import OffererFactory
from pcapi.emails.offerer_attachment_validation import retrieve_data_for_offerer_attachment_validation_email


@pytest.mark.usefixtures("db_session")
class ProOffererAttachmentValidationEmailTest:
    def test_email(self):
        offerer = OffererFactory(name="Le Théâtre SAS")

        mail_data = retrieve_data_for_offerer_attachment_validation_email(offerer)

        assert mail_data == {
            "MJ-TemplateID": 778756,
            "MJ-TemplateLanguage": True,
            "Vars": {"nom_structure": "Le Théâtre SAS"},
        }
