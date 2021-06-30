import pytest

import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_categories(self, app):
        # Given
        user = users_factories.UserFactory()

        # when
        client = TestClient(app.test_client()).with_auth(email=user.email)
        response = client.get("/offers/categories")

        # then
        assert response.status_code == 200
        assert list(response.json.keys()) == ["categories", "subcategories"]
        assert len(response.json["categories"]) == 13
        assert all(list(category_dict.keys()) == ["id", "proLabel"] for category_dict in response.json["categories"])
        assert len(response.json["subcategories"]) == 60
        assert all(
            list(subcategory_dict.keys())
            == [
                "id",
                "categoryId",
                "matchingType",
                "proLabel",
                "appLabel",
                "searchGroup",
                "isEvent",
                "conditionalFields",
                "canExpire",
                "canBeDuo",
                "onlineOfflinePlatform",
                "isDigitalDeposit",
                "isPhysicalDeposit",
                "reimbursementRule",
                "isSelectable",
            ]
            for subcategory_dict in response.json["subcategories"]
        )
