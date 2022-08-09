from flask import url_for
import pytest

import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetStudentsLevelsTest:
    def test_list_students_levels(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_students_levels")
        )

        # Then
        assert response.status_code == 200

        response_list = response.json
        assert {"id": "GENERAL0", "name": "Lycée - Terminale"} in response_list
        assert response_list == [
            {"id": student_level.name, "name": student_level.value}
            for student_level in educational_models.StudentLevels
        ]

    def test_list_students_levels_user_auth_returns_401(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        response = client.with_session_auth(user_offerer.user.email).get(
            url_for("pro_public_api_v2.list_students_levels")
        )

        # Then
        assert response.status_code == 401

    def test_list_students_levels_anonymous_returns_401(self, client):
        # Given

        # When
        response = client.get(url_for("pro_public_api_v2.list_students_levels"))

        # Then
        assert response.status_code == 401
