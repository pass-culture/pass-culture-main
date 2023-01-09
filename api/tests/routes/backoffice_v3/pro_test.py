from flask import url_for
import pytest

from pcapi.core.offerers import factories as offerers_factories
import pcapi.core.permissions.models as perm_models

from .helpers import search as search_helpers
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


def build_pro_user():
    return offerers_factories.UserOffererFactory().user


def build_offerer():
    return offerers_factories.UserOffererFactory().offerer


def build_venue():
    return offerers_factories.VenueFactory()


class SearchProUnauthorizedTest(unauthorized_helpers.UnauthorizedHelper):
    endpoint = "backoffice_v3_web.search_pro"
    needed_permission = perm_models.Permissions.SEARCH_PRO_ACCOUNT


class SearchProTest(search_helpers.SearchHelper):
    endpoint = "backoffice_v3_web.search_pro"

    @pytest.mark.parametrize(
        "pro_builder,pro_type",
        [
            (build_pro_user, "user"),
            (build_offerer, "offerer"),
            (build_venue, "venue"),
        ],
    )
    def test_search_result_page(self, authenticated_client, pro_builder, pro_type):
        pro_object = pro_builder()

        url = url_for(self.endpoint, terms=pro_object.id, pro_type=pro_type)
        response = authenticated_client.get(url)

        assert response.status_code == 200, f"[{response.status_code}] {response.location}"
