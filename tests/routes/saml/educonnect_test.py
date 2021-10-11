import datetime
import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_educonnect_login(client):
    response = client.get("/saml/educonnect/login")
    assert response.status_code == 302
    assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")


@patch("pcapi.core.users.external.educonnect.api.get_saml_client")
def test_on_educonnect_authentication_response(mock_get_educonnect_saml_client, client, caplog):
    mock_saml_client = MagicMock()
    mock_saml_response = MagicMock()
    mock_get_educonnect_saml_client.return_value = mock_saml_client
    mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
    mock_saml_response.get_identity.return_value = {
        "givenName": ["Max"],
        "sn": ["SENS"],
        "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
            "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
        ],
        "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
        "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
        "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
        "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
    }
    mock_saml_response.in_response_to = "id-XXMmsDBrJGm1N0761"

    with caplog.at_level(logging.INFO):
        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

    assert response.status_code == 302
    assert caplog.records[0].extra == {
        "date_of_birth": datetime.date(2006, 8, 18),
        "educonnect_connection_date": datetime.datetime(2021, 10, 8, 11, 51, 33, 437000),
        "educonnect_id": "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875",
        "first_name": "Max",
        "last_name": "SENS",
        "logout_url": "https://educonnect.education.gouv.fr/Logout",
        "saml_request_id": "id-XXMmsDBrJGm1N0761",
        "student_level": "2212",
    }
