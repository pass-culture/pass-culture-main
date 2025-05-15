import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.rest import check_user_has_access_to_offerer


pytestmark = pytest.mark.usefixtures("db_session")


class CheckUserHasAccessToOffererTest:
    def test_check_user_has_access_to_offerer(self, app):
        pro = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        with assert_no_duplicated_queries():
            check_user_has_access_to_offerer(pro, offerer.id)

    def test_raises_if_user_cannot_access_offerer(self, app):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        with pytest.raises(ApiErrors) as error:
            check_user_has_access_to_offerer(user, offerer.id)

        assert error.value.errors["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
        assert error.value.status_code == 403
