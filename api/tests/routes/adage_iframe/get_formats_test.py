from flask import url_for
import pytest

from pcapi.core.categories.subcategories import EacFormat


pytestmark = pytest.mark.usefixtures("db_session")


class FormatsTest:
    def test_get_formats(self, client):
        test_client = client.with_adage_token(email="test@mail.com", uai="12890AI")
        response = test_client.get(url_for("adage_iframe.get_educational_offers_formats"))

        assert response.status_code == 200
        assert set(response.json["formats"]) == set(fmt.value for fmt in EacFormat)
