import pytest

import pcapi.core.users.factories as users_factories


VALID_UAI = "0470009E"


@pytest.mark.usefixtures("db_session")
class GetAutocompleteEducationalRedactorForUaiTest:
    def test_get_one_redactor(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            f"/collective/offers/redactors?uai={VALID_UAI}&candidate=sklodowska"
        )

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == [
            {
                "gender": "Mme.",
                "name": "SKLODOWSKA",
                "surname": "MARIA",
                "email": "maria.sklodowska@example.com",
            },
        ]

    def test_get_multiple_redactors(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            f"/collective/offers/redactors?uai={VALID_UAI}&candidate=HEN"
        )

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == [
            {
                "gender": "M.",
                "name": "POINTCARE",
                "surname": "HENRI",
                "email": "henri.pointcare@example.com",
            },
            {
                "gender": "M.",
                "name": "HENMAR",
                "surname": "CONFUSION",
                "email": "confusion.raymar@example.com",
            },
        ]

    def test_candidate_with_diacritics(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            f"/collective/offers/redactors?uai={VALID_UAI}&candidate=pointcaré"
        )

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == [
            {
                "gender": "M.",
                "name": "POINTCARE",
                "surname": "HENRI",
                "email": "henri.pointcare@example.com",
            },
        ]

    def test_candidate_with_space(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            f"/collective/offers/redactors?uai={VALID_UAI}&candidate=E%20H"
        )

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == [
            {
                "gender": "M.",
                "name": "POINTCARE",
                "surname": "HENRI",
                "email": "henri.pointcare@example.com",
            },
        ]

    def test_no_redactors_found(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            f"/collective/offers/redactors?uai={VALID_UAI}&candidate=Becquerel"
        )

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == []

    def test_uai_not_found(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            "/collective/offers/redactors?uai=NO_UAI&candidate=sklodowska"
        )

        # Then
        assert response.status_code == 404

    def test_uai_too_short(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            "/collective/offers/redactors?uai=X&candidate=sklodowska"
        )

        # Then
        assert response.status_code == 400

    def test_candidate_too_short(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_session_auth(email=user.email).get(
            f"/collective/offers/redactors?uai={VALID_UAI}&candidate=sk"
        )

        # Then
        assert response.status_code == 400

    def test_user_not_logged_in(self, client):
        # When
        response = client.get("/collective/offers/redactors?uai=X&candidate=sklodowska")

        # Then
        assert response.status_code == 401
