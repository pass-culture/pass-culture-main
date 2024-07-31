import pytest

from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


VALID_UAI = "0470009E"


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_one_redactor(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  # user + session
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=sklodowska")
            assert response.status_code == 200

        # Then
        response_json = response.json
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
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  # user + session
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=HEN")
            assert response.status_code == 200

        # Then
        response_json = response.json
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
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  # session + user
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=pointcaré")
            assert response.status_code == 200

        # Then
        response_json = response.json
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
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  # session + user
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=E%20H")
            assert response.status_code == 200

        # Then
        response_json = response.json
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
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  #  session + user
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=Becquerel")
            assert response.status_code == 200

        # Then
        response_json = response.json
        assert response_json == []


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_uai_not_found(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  #  session + user
            response = client.get("/collective/offers/redactors?uai=NO_UAI&candidate=sklodowska")
            assert response.status_code == 404


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_uai_too_short(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  #  session + user
            response = client.get("/collective/offers/redactors?uai=X&candidate=sklodowska")
            assert response.status_code == 400

    def test_candidate_too_short(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        client = client.with_session_auth(email=user.email)
        with assert_num_queries(2):  #  session + user
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=sk")
            assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def test_user_not_logged_in(self, client):
        # When
        with assert_num_queries(0):
            response = client.get("/collective/offers/redactors?uai=X&candidate=sklodowska")
            assert response.status_code == 401
