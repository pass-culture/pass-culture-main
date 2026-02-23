import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.testing import assert_num_queries


VALID_UAI = "0470009E"

expected_num_queries = 1  # session + user
expected_num_queries_error = expected_num_queries + 1  # rollback

pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_get_one_redactor(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=sklodowska")
            assert response.status_code == 200

        response_json = response.json
        assert response_json == [
            {
                "name": "SKLODOWSKA",
                "surname": "MARIA",
                "email": "maria.sklodowska@example.com",
            },
        ]

    def test_get_multiple_redactors(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=HEN")
            assert response.status_code == 200

        response_json = response.json
        assert response_json == [
            {
                "name": "POINTCARE",
                "surname": "HENRI",
                "email": "henri.pointcare@example.com",
            },
            {
                "name": "HENMAR",
                "surname": "CONFUSION",
                "email": "confusion.raymar@example.com",
            },
        ]

    def test_candidate_with_diacritics(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=pointcaré")
            assert response.status_code == 200

        response_json = response.json
        assert response_json == [
            {
                "name": "POINTCARE",
                "surname": "HENRI",
                "email": "henri.pointcare@example.com",
            },
        ]

    def test_candidate_with_space(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=E%20H")
            assert response.status_code == 200

        response_json = response.json
        assert response_json == [
            {
                "name": "POINTCARE",
                "surname": "HENRI",
                "email": "henri.pointcare@example.com",
            },
        ]

    def test_no_redactors_found(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=Becquerel")
            assert response.status_code == 200

        response_json = response.json
        assert response_json == []


class Returns404Test:
    def test_uai_not_found(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries_error):
            response = client.get("/collective/offers/redactors?uai=NO_UAI&candidate=sklodowska")
            assert response.status_code == 404


class Returns400Test:
    def test_uai_too_short(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries_error):
            response = client.get("/collective/offers/redactors?uai=X&candidate=sklodowska")
            assert response.status_code == 400

    def test_candidate_too_short(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(email=user.email)
        with assert_num_queries(expected_num_queries_error):
            response = client.get(f"/collective/offers/redactors?uai={VALID_UAI}&candidate=sk")
            assert response.status_code == 400


class Returns401Test:
    def test_user_not_logged_in(self, client):
        with assert_num_queries(0):
            response = client.get("/collective/offers/redactors?uai=X&candidate=sklodowska")
            assert response.status_code == 401
