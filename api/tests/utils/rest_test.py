import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import humanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_raise_error


pytestmark = pytest.mark.usefixtures("db_session")


class CheckUserHasAccessToOffererTest:
    def test_check_user_has_access_to_offerer(self, app):
        pro = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        # fmt: off
        n_queries = (
            1  # select Offerer
            + 1  # select User
            + 1  # select UserOfferer
        )
        # fmt: on
        with assert_num_queries(n_queries):
            check_user_has_access_to_offerer(pro, offerer.id)

    def test_raises_if_user_cannot_access_offerer(self, app):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        with pytest.raises(ApiErrors) as error:
            check_user_has_access_to_offerer(user, offerer.id)

        assert error.value.errors["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert error.value.status_code == 403


class TestLoadOrRaiseErrorTest:
    def test_returns_object_if_found(self, app):
        with pytest.raises(ApiErrors) as error:
            load_or_raise_error(Venue, humanize(1))

        assert error.value.errors["global"] == [
            "Aucun objet ne correspond à cet identifiant dans notre base de données"
        ]
        assert error.value.status_code == 404

    def test_raises_api_error_if_no_object(self, app):
        venue = offerers_factories.VenueFactory()

        load_or_raise_error(Venue, humanize(venue.id))  # should not raise
