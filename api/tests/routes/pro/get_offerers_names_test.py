import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


class Returns200ForProUserTest:
    def _setup_offerers_for_pro_user(self, user):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        offerer_not_validated = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer_not_validated)

        offerer_validated_for_user = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer_validated_for_user)
        offerers_factories.UserOffererFactory(user=user, offerer=offerer_validated_for_user)

        offerer_not_validated_for_user = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer_not_validated_for_user)
        offerers_factories.NotValidatedUserOffererFactory(user=user, offerer=offerer_not_validated_for_user)

        other_offerer = offerers_factories.OffererFactory()
        other_user_offerer = offerers_factories.UserOffererFactory(offerer=other_offerer)

        other_offerer_not_validated = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=other_user_offerer.user, offerer=other_offerer_not_validated)

        return {
            "owned_offerer_validated": offerer,
            "owned_offerer_not_validated": offerer_not_validated,
            "owned_offerer_validated_for_user": offerer_validated_for_user,
            "owned_offerer_not_validated_for_user": offerer_not_validated_for_user,
            "other_offerer_user": other_offerer,
            "other_offerer_not_validated": other_offerer_not_validated,
        }

    @pytest.mark.usefixtures("db_session")
    def test_response_serializer(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        # when
        client = client.with_session_auth(pro_user.email)
        response = client.get("/offerers/names")

        # then
        assert response.status_code == 200
        assert response.json == {
            "offerersNames": [{"id": humanize(offerer.id), "name": offerer.name, "nonHumanizedId": offerer.id}]
        }

    @pytest.mark.usefixtures("db_session")
    def test_get_offerers_names_for_id(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        # when
        client = client.with_session_auth(pro_user.email)
        response = client.get(f'/offerers/names?offerer_id={offerers["owned_offerer_validated"].id}')

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 1
        assert response.json["offerersNames"][0]["id"] == humanize(offerers["owned_offerer_validated"].id)
        assert response.json["offerersNames"][0]["name"] == offerers["owned_offerer_validated"].name

    @pytest.mark.usefixtures("db_session")
    def test_get_all_offerers_names(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        # when
        client = client.with_session_auth(pro_user.email)
        response = client.get("/offerers/names")

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 4

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(offerers["owned_offerer_validated"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_not_validated"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_validated_for_user"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_not_validated_for_user"].id) in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_offerers_names(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        # when
        client = client.with_session_auth(pro_user.email)
        response = client.get("/offerers/names?validated=true")

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 3

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(offerers["owned_offerer_validated"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_validated_for_user"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_not_validated_for_user"].id) in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_for_user_offerers_names(self, client):
        # given
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        # when
        client = client.with_session_auth(pro_user.email)
        response = client.get("/offerers/names?validated_for_user=true")

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 3

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(offerers["owned_offerer_validated"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_not_validated"].id) in offerer_ids
        assert humanize(offerers["owned_offerer_validated_for_user"].id) in offerer_ids


class Returns200ForAdminTest:
    def _setup_offerers_for_users(self):
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        offerer_not_validated = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user_offerer.user, offerer=offerer_not_validated)

        other_offerer = offerers_factories.OffererFactory()
        other_user_offerer = offerers_factories.UserOffererFactory(offerer=other_offerer)

        other_offerer_not_validated = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=other_user_offerer.user, offerer=other_offerer_not_validated)
        return {
            "offerer": offerer,
            "offerer_not_validated": offerer_not_validated,
            "other_offerer": other_offerer,
            "other_offerer_not_validated": other_offerer_not_validated,
        }

    @pytest.mark.usefixtures("db_session")
    def test_get_all_offerers_names(self, client):
        # given
        admin = users_factories.AdminFactory()
        offerers = self._setup_offerers_for_users()

        # when
        client = client.with_session_auth(admin.email)
        response = client.get("/offerers/names")

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 4

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(offerers["offerer"].id) in offerer_ids
        assert humanize(offerers["offerer_not_validated"].id) in offerer_ids
        assert humanize(offerers["other_offerer"].id) in offerer_ids
        assert humanize(offerers["other_offerer_not_validated"].id) in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_offerers(self, client):
        # given
        admin = users_factories.AdminFactory()
        offerers = self._setup_offerers_for_users()

        # when
        client = client.with_session_auth(admin.email)
        response = client.get("/offerers/names?validated=true")

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 2

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(offerers["offerer"].id) in offerer_ids
        assert humanize(offerers["other_offerer"].id) in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_not_validated_offerers(self, client):
        # given
        admin = users_factories.AdminFactory()
        offerers = self._setup_offerers_for_users()

        # when
        client = client.with_session_auth(admin.email)
        response = client.get("/offerers/names?validated=false")

        # then
        assert response.status_code == 200
        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 2

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert humanize(offerers["offerer_not_validated"].id) in offerer_ids
        assert humanize(offerers["other_offerer_not_validated"].id) in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_queries(self, client):
        admin = users_factories.AdminFactory()
        self._setup_offerers_for_users()

        client = client.with_session_auth(admin.email)
        queries = AUTHENTICATION_QUERIES
        queries += 1  # select offerers
        with assert_num_queries(queries):
            response = client.get("/offerers/names")
        assert response.status_code == 200
