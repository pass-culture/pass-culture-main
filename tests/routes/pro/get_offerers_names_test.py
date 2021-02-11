import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200:
    @pytest.mark.usefixtures("db_session")
    def should_returns_only_validated_offerers_managed_by_user_when_user_is_not_admin(self, app):
        # given
        pro = users_factories.UserFactory(isBeneficiary=False)
        owned_offerer_validated = offers_factories.OffererFactory()
        owned_offerer_not_validated = offers_factories.OffererFactory(validationToken="token")
        other_offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=owned_offerer_validated)
        offers_factories.UserOffererFactory(user=pro, offerer=owned_offerer_not_validated)

        # when
        response = TestClient(app.test_client()).with_auth(pro.email).get("/offerers/names")

        # then
        assert response.status_code == 200
        assert len(response.json) == 1

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(owned_offerer_validated.id) in offerer_ids
        assert [humanize(owned_offerer_not_validated.id), humanize(other_offerer.id)] not in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def should_returns_all_validated_offerers_managed_by_user_when_user_is_admin(self, app):
        # given
        admin = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        offerer_not_validated = offers_factories.OffererFactory(validationToken="token")
        other_offerer = offers_factories.OffererFactory()

        # when
        response = TestClient(app.test_client()).with_auth(admin.email).get("/offerers/names")

        # then
        assert response.status_code == 200
        assert len(response.json) == 1

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(other_offerer.id) in offerer_ids
        assert humanize(offerer_not_validated.id) not in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def should_returns_offerers_names_by_id(self, app):
        # given
        pro = users_factories.UserFactory(isBeneficiary=False)
        owned_offerer_validated = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=owned_offerer_validated)

        # when
        response = TestClient(app.test_client()).with_auth(pro.email).get("/offerers/names")

        # then
        assert response.status_code == 200
        assert response.json == {
            "offerersNames": [{"id": humanize(owned_offerer_validated.id), "name": owned_offerer_validated.name}]
        }
