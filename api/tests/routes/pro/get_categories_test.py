from unittest.mock import patch

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.categories import pro_categories
from pcapi.core.categories.subcategories import ABO_BIBLIOTHEQUE
from pcapi.core.categories.subcategories import CINE_PLEIN_AIR
from pcapi.core.categories.subcategories import VISITE_LIBRE
from pcapi.core.testing import assert_num_queries


@patch(
    "pcapi.core.categories.subcategories.ALL_SUBCATEGORIES",
    (ABO_BIBLIOTHEQUE, CINE_PLEIN_AIR, VISITE_LIBRE),
)
@patch(
    "pcapi.core.categories.pro_categories.ALL_CATEGORIES",
    (
        pro_categories.Category(
            id="LIVRE",
            pro_label="Livre",
        ),
        pro_categories.Category(
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
        with assert_num_queries(1):  #  session + user
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
                    "isEvent": False,
                    "conditionalFields": [],
                    "canExpire": True,
                    "canBeDuo": False,
                    "canBeWithdrawable": False,
                    "onlineOfflinePlatform": "OFFLINE",
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": True,
                    "reimbursementRule": "STANDARD",
                    "isSelectable": True,
                    "canHaveOpeningHours": False,
                },
                {
                    "id": "CINE_PLEIN_AIR",
                    "categoryId": "CINEMA",
                    "proLabel": "Cinéma plein air",
                    "appLabel": "Cinéma plein air",
                    "isEvent": True,
                    "conditionalFields": ["author", "visa", "stageDirector"],
                    "canExpire": False,
                    "canBeDuo": True,
                    "canBeWithdrawable": False,
                    "onlineOfflinePlatform": "OFFLINE",
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": False,
                    "reimbursementRule": "STANDARD",
                    "isSelectable": True,
                    "canHaveOpeningHours": False,
                },
                {
                    "id": "VISITE",
                    "categoryId": "MUSEE",
                    "proLabel": "Visite libre",
                    "appLabel": "Visite libre",
                    "isEvent": True,
                    "conditionalFields": [],
                    "canExpire": False,
                    "canBeDuo": True,
                    "canBeWithdrawable": False,
                    "onlineOfflinePlatform": "OFFLINE",
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": False,
                    "reimbursementRule": "STANDARD",
                    "isSelectable": True,
                    "canHaveOpeningHours": True,
                },
            ],
        }
