from unittest.mock import patch

import pytest

from pcapi.core.categories import categories
from pcapi.core.categories.subcategories_v2 import ABO_BIBLIOTHEQUE
from pcapi.core.categories.subcategories_v2 import CINE_PLEIN_AIR
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


@patch(
    "pcapi.core.categories.subcategories_v2.ALL_SUBCATEGORIES",
    (ABO_BIBLIOTHEQUE, CINE_PLEIN_AIR),
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
class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_categories(self, app, client):
        # Given
        user = users_factories.ProFactory()

        # when
        client = client.with_session_auth(user.email)
        with assert_num_queries(2):  #  session + user
            response = client.get("/offers/categories")
            assert response.status_code == 200

        assert response.json == {
            "categories": [
                {"id": "LIVRE", "proLabel": "Livre", "isSelectable": True},
                {"id": "CINEMA", "proLabel": "Cinéma", "isSelectable": True},
            ],
            "subcategories": [
                {
                    "id": "ABO_BIBLIOTHEQUE",
                    "categoryId": "LIVRE",
                    "proLabel": "Abonnement (bibliothèques, médiathèques...)",
                    "appLabel": "Abonnement (bibliothèques, médiathèques...)",
                    "searchGroupName": "LIVRES",
                    "isEvent": False,
                    "conditionalFields": [],
                    "canExpire": True,
                    "canBeDuo": False,
                    "canBeEducational": False,
                    "canBeWithdrawable": False,
                    "onlineOfflinePlatform": "OFFLINE",
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": True,
                    "reimbursementRule": "STANDARD",
                    "isSelectable": True,
                },
                {
                    "id": "CINE_PLEIN_AIR",
                    "categoryId": "CINEMA",
                    "proLabel": "Cinéma plein air",
                    "appLabel": "Cinéma plein air",
                    "searchGroupName": "FILMS_SERIES_CINEMA",
                    "isEvent": True,
                    "conditionalFields": ["author", "visa", "stageDirector"],
                    "canExpire": False,
                    "canBeDuo": True,
                    "canBeEducational": True,
                    "canBeWithdrawable": False,
                    "onlineOfflinePlatform": "OFFLINE",
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": False,
                    "reimbursementRule": "STANDARD",
                    "isSelectable": True,
                },
            ],
        }
