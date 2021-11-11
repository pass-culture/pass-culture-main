import pytest

from pcapi.core.categories import subcategories
import pcapi.core.users.factories as users_factories


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_categories(self, app, client):
        # Given
        user = users_factories.ProFactory()

        # when
        response = client.with_session_auth(user.email).get("/offers/categories")

        # then
        assert response.status_code == 200
        assert list(response.json.keys()) == ["categories", "subcategories"]
        assert len(response.json["categories"]) == 14
        assert all(
            list(category_dict.keys()) == ["id", "proLabel", "isSelectable"]
            for category_dict in response.json["categories"]
        )
        assert len(response.json["subcategories"]) == len(subcategories.ALL_SUBCATEGORIES)
        assert all(
            list(subcategory_dict.keys())
            == [
                "id",
                "categoryId",
                "matchingType",
                "proLabel",
                "appLabel",
                "searchGroupName",
                "isEvent",
                "conditionalFields",
                "canExpire",
                "canBeDuo",
                "canBeEducational",
                "onlineOfflinePlatform",
                "isDigitalDeposit",
                "isPhysicalDeposit",
                "reimbursementRule",
                "isSelectable",
            ]
            for subcategory_dict in response.json["subcategories"]
        )
