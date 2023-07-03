from unittest.mock import patch

import pytest

from pcapi.core.categories import categories
from pcapi.core.categories.subcategories import Subcategory
from pcapi.core.categories.subcategories_v2 import ConditionalField
from pcapi.core.categories.subcategories_v2 import ExtraDataFieldEnum
from pcapi.core.categories.subcategories_v2 import NativeCategory
import pcapi.core.users.factories as users_factories


@patch(
    "pcapi.core.categories.subcategories.ALL_SUBCATEGORIES",
    (
        Subcategory(
            id="ABO_BIBLIOTHEQUE",
            category=categories.LIVRE,
            native_category=NativeCategory.BIBLIOTHEQUE,
            pro_label="Abonnement (bibliothèques, médiathèques...)",
            app_label="Abonnement (bibliothèques, médiathèques...)",
            search_group_name="LIVRE",
            homepage_label_name="LIVRE",
            is_event=False,
            conditional_fields={},
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
            category=categories.CINEMA,
            native_category=NativeCategory.SEANCES_DE_CINEMA,
            pro_label="Cinéma plein air",
            app_label="Cinéma plein air",
            search_group_name="CINEMA",
            homepage_label_name="CINEMA",
            is_event=True,
            conditional_fields={
                ExtraDataFieldEnum.AUTHOR.value: ConditionalField(),
                ExtraDataFieldEnum.VISA.value: ConditionalField(),
                ExtraDataFieldEnum.STAGE_DIRECTOR.value: ConditionalField(),
            },
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
class GetCategoriesTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_categories(self, app, client):
        # Given
        user = users_factories.ProFactory()

        # when
        response = client.with_session_auth(user.email).get("/offers/categories")

        # then
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
                    "searchGroupName": "LIVRE",
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
                    "searchGroupName": "CINEMA",
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
