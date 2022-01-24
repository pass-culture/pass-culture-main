from typing import ByteString
from typing import Optional
from unittest.mock import patch

import pytest

from pcapi.core.categories.categories import Category
from pcapi.core.categories.subcategories import Subcategory

from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


def _create_adage_valid_token_with_email(
    email: str,
    civility: Optional[str] = "Mme",
    lastname: Optional[str] = "LAPROF",
    firstname: Optional[str] = "Jeanne",
    uai: Optional[str] = "EAU123",
) -> ByteString:
    return create_adage_jwt_fake_valid_token(
        civility=civility, lastname=lastname, firstname=firstname, email=email, uai=uai
    )


pytestmark = pytest.mark.usefixtures("db_session")


@patch(
    "pcapi.core.categories.subcategories.ALL_SUBCATEGORIES",
    (
        Subcategory(
            id="ABO_BIBLIOTHEQUE",
            category_id="LIVRE",
            pro_label="Abonnement (bibliothèques, médiathèques...)",
            app_label="Abonnement (bibliothèques, médiathèques...)",
            search_group_name="LIVRE",
            homepage_label_name="LIVRE",
            is_event=False,
            conditional_fields=[],
            can_expire=True,
            can_be_duo=False,
            can_be_educational=False,
            online_offline_platform="OFFLINE",
            is_digital_deposit=False,
            is_physical_deposit=True,
            reimbursement_rule="STANDARD",
        ),
        Subcategory(
            id="CINE_PLEIN_AIR",
            category_id="CINEMA",
            pro_label="Cinéma plein air",
            app_label="Cinéma plein air",
            search_group_name="CINEMA",
            homepage_label_name="CINEMA",
            is_event=True,
            conditional_fields=["author", "visa", "stageDirector"],
            can_expire=False,
            can_be_duo=True,
            can_be_educational=True,
            online_offline_platform="OFFLINE",
            is_digital_deposit=False,
            is_physical_deposit=False,
            reimbursement_rule="STANDARD",
        ),
    ),
)
@patch(
    "pcapi.core.categories.categories.ALL_CATEGORIES",
    (
        Category(
            id="LIVRE",
            pro_label="Livre",
        ),
        Category(
            id="CINEMA",
            pro_label="Cinéma",
        ),
    ),
)
class Returns200Test:
    def test_get_categories(self, client):
        # Given
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email="toto@mail.com", uai="12890AI")
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.get("/adage-iframe/offers/categories")

        assert response.status_code == 200
        assert response.json == {
            "categories": [{"id": "CINEMA", "proLabel": "Cinéma"}],
            "subcategories": [{"id": "CINE_PLEIN_AIR", "categoryId": "CINEMA"}],
        }
