from unittest.mock import patch

import pytest

from pcapi.core.categories import categories
from pcapi.core.categories.subcategories_v2 import ABO_BIBLIOTHEQUE
from pcapi.core.categories.subcategories_v2 import CINE_PLEIN_AIR

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


pytestmark = pytest.mark.usefixtures("db_session")


@patch(
    "pcapi.core.categories.subcategories_v2.ALL_SUBCATEGORIES",
    (
        ABO_BIBLIOTHEQUE,
        CINE_PLEIN_AIR,
    ),
)
@patch(
    "pcapi.core.categories.categories.ALL_CATEGORIES",
    (
        categories.Category(
            id="LIVRE",
            pro_label="Livre",
        ),
        categories.Category(
            id="CINEMA",
            pro_label="Cinéma",
        ),
    ),
)
class CategoriesTest:
    def test_get_categories(self, client):
        # Given
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get("/adage-iframe/offers/categories")

        assert response.status_code == 200
        assert response.json == {
            "categories": [{"id": "CINEMA", "proLabel": "Cinéma"}],
            "subcategories": [{"id": "CINE_PLEIN_AIR", "categoryId": "CINEMA"}],
        }
