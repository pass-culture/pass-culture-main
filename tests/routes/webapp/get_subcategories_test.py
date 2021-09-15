import pytest

from pcapi.core.categories import subcategories
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_get_subcategories(self, app, client):
        user = users_factories.BeneficiaryGrant18Factory()

        response = TestClient(app.test_client()).with_session_auth(user.email).get("/subcategories")

        assert response.status_code == 200
        assert list(response.json.keys()) == ["subcategories", "searchGroups"]
        assert len(response.json["searchGroups"]) == len(subcategories.SearchGroupChoicesEnum)
        assert len(response.json["subcategories"]) == len(subcategories.ALL_SUBCATEGORIES)
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
        assert all(
            list(search_group_dict.keys())
            == [
                "name",
                "value",
            ]
            for search_group_dict in response.json["searchGroups"]
        )
