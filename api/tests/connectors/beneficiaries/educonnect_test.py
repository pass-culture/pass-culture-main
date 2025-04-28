import shutil

import pytest

from pcapi import settings
from pcapi.connectors.beneficiaries.educonnect import educonnect_connector
from pcapi.utils import requests


CERTIFICATE_CONTENT = ""
KEY_CONTENT = ""


@pytest.fixture
def path(tmp_path):
    try:
        yield tmp_path
    finally:
        shutil.rmtree(tmp_path)


@pytest.mark.skip(reason="Should only be run locally for testing pysaml2 updates")
@pytest.mark.settings(
    API_URL_FOR_EDUCONNECT="https://backend.staging.passculture.team",
    EDUCONNECT_METADATA_FILE="educonnect.pr4.metadata.xml",
)
def test_educonnect(path, monkeypatch, socket_enabled):
    """
    CERTIFICATE_CONTENT and KEY_CONTENT should be populated from values set on stating (not testing) env.

    CERTIFICATE_CONTENT → settings.EDUCONNECT_SP_CERTIFICATE
    KEY_CONTENT → settings.EDUCONNECT_SP_PRIVATE_KEY
    """

    cert_file = path / "public.cert"
    key_file = path / "private.key"
    PASS_CULTURE_IDENTITY_ID = f"{settings.API_URL_FOR_EDUCONNECT}/saml/metadata.xml"
    PASS_CULTURE_ACS_URL = f"{settings.API_URL_FOR_EDUCONNECT}/saml/acs/"

    cert_file.write_text(CERTIFICATE_CONTENT)
    key_file.write_text(KEY_CONTENT)

    monkeypatch.setattr(educonnect_connector, "PUBLIC_CERTIFICATE_FILE_PATH", cert_file.as_posix())
    monkeypatch.setattr(educonnect_connector, "PRIVATE_KEY_FILE_PATH", key_file.as_posix())
    monkeypatch.setattr(educonnect_connector, "PASS_CULTURE_IDENTITY_ID", PASS_CULTURE_IDENTITY_ID)
    monkeypatch.setattr(educonnect_connector, "PASS_CULTURE_ACS_URL", PASS_CULTURE_ACS_URL)

    saml_client = educonnect_connector.get_saml_client()
    _, info = saml_client.prepare_for_authenticate()
    redirect_url = next(header[1] for header in info["headers"] if header[0] == "Location")

    response = requests.get(redirect_url, timeout=None)  # timeout is None here to bypass linter's warning
    assert response.status_code == 200
