from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class GetOffererUsersTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_users_returns_list(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        uo1 = offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(firstName=None, lastName=None)
        )
        uo2 = offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(firstName="Jean", lastName="Bon")
        )
        offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(), validationToken="not-validated"
        )

        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer2, user=users_factories.ProFactory())

        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == [
            {
                "id": uo1.user.id,
                "firstName": None,
                "lastName": None,
                "email": uo1.user.email,
            },
            {
                "id": uo2.user.id,
                "firstName": "Jean",
                "lastName": "Bon",
                "email": uo2.user.email,
            },
        ]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_users_returns_empty_if_offerer_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_users_without_permission(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        auth_token = generate_token(users_factories.UserFactory(), [])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_users_as_anonymous(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()

        # when
        response = client.get(url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id))

        # then
        assert response.status_code == 403
