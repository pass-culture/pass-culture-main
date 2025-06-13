import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing


class Returns200ForProUserTest:
    def _setup_offerers_for_pro_user(self, user):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        offerer_not_validated = offerers_factories.NewOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer_not_validated)

        offerer_validated_for_user = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer_validated_for_user)
        offerers_factories.UserOffererFactory(user=user, offerer=offerer_validated_for_user)

        offerer_not_validated_for_user = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer_not_validated_for_user)
        offerers_factories.NewUserOffererFactory(user=user, offerer=offerer_not_validated_for_user)

        other_offerer = offerers_factories.OffererFactory()
        other_user_offerer = offerers_factories.UserOffererFactory(offerer=other_offerer)

        other_offerer_not_validated = offerers_factories.NewOffererFactory()
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
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        client = client.with_session_auth(pro_user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = client.get("/offerers/names")
            assert response.status_code == 200

        assert response.json == {
            "offerersNames": [{"name": offerer.name, "id": offerer.id, "allowedOnAdage": offerer.allowedOnAdage}]
        }

    @pytest.mark.usefixtures("db_session")
    def test_get_offerers_names_for_id(self, client):
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        client = client.with_session_auth(pro_user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = client.get(f"/offerers/names?offerer_id={offerers['owned_offerer_validated'].id}")
            assert response.status_code == 200

        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 1
        assert response.json["offerersNames"][0]["id"] == offerers["owned_offerer_validated"].id
        assert response.json["offerersNames"][0]["name"] == offerers["owned_offerer_validated"].name

    @pytest.mark.usefixtures("db_session")
    def test_get_all_offerers_names(self, client):
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        client = client.with_session_auth(pro_user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = client.get("/offerers/names")
            assert response.status_code == 200

        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 4

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert offerers["owned_offerer_validated"].id in offerer_ids
        assert offerers["owned_offerer_not_validated"].id in offerer_ids
        assert offerers["owned_offerer_validated_for_user"].id in offerer_ids
        assert offerers["owned_offerer_not_validated_for_user"].id in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_offerers_names(self, client):
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        client = client.with_session_auth(pro_user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = client.get("/offerers/names?validated=true")
            assert response.status_code == 200

        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 3

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert offerers["owned_offerer_validated"].id in offerer_ids
        assert offerers["owned_offerer_validated_for_user"].id in offerer_ids
        assert offerers["owned_offerer_not_validated_for_user"].id in offerer_ids

    @pytest.mark.usefixtures("db_session")
    def test_get_all_validated_for_user_offerers_names(self, client):
        pro_user = users_factories.ProFactory()
        offerers = self._setup_offerers_for_pro_user(pro_user)

        client = client.with_session_auth(pro_user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerers
        with testing.assert_num_queries(num_queries):
            response = client.get("/offerers/names?validated_for_user=true")
            assert response.status_code == 200

        assert "offerersNames" in response.json
        assert len(response.json["offerersNames"]) == 3

        offerer_ids = [offererName["id"] for offererName in response.json["offerersNames"]]
        assert offerers["owned_offerer_validated"].id in offerer_ids
        assert offerers["owned_offerer_not_validated"].id in offerer_ids
        assert offerers["owned_offerer_validated_for_user"].id in offerer_ids
