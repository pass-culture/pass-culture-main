import datetime
import logging

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors import boost
import pcapi.core.external_bookings.boost.exceptions as boost_exceptions
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import override_settings
from pcapi.routes.serialization import BaseModel


pytestmark = pytest.mark.usefixtures("db_session")


class BoostBuildUrlTest:
    def test_build_url(self):
        cinema_url = "https://cinema.example.com/"
        resource = boost.ResourceBoost.EXAMPLE_WITH_PATTERNS

        url = boost.build_url(cinema_url, resource, {"start": 1, "end": 5})

        assert url == "https://cinema.example.com/example/1/5"


class BoostLoginTest:
    @time_machine.travel("2022-10-12 17:09:25", tick=False)
    def test_login(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema.example.com/")
        response_json = {"message": "Login successful", "token": "new-token"}
        requests_mock.post("https://cinema.example.com/api/vendors/login", json=response_json)

        token = boost.login(cinema_details)

        assert requests_mock.last_request.json() == {
            "password": "fake_password",
            "username": "fake_user",
            "stationName": f"pcapi - {settings.ENV}",
        }
        assert requests_mock.last_request.url == "https://cinema.example.com/api/vendors/login?ignore_device=True"
        assert token == cinema_details.token == "new-token"
        assert cinema_details.tokenExpirationDate == datetime.datetime(2022, 10, 13, 17, 9, 25)

    @override_settings(BOOST_API_PASSWORD="wrong_password")
    def test_wrong_credentials(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="old-token",
            tokenExpirationDate=datetime.datetime(2022, 10, 1),
        )
        response_json = {"code": 400, "message": "Vendor login failed. Wrong password!"}
        requests_mock.post("https://cinema.example.com/api/vendors/login", status_code=400, json=response_json)

        with pytest.raises(boost_exceptions.BoostAPIException) as exc:
            boost.login(cinema_details)

        assert requests_mock.last_request.json() == {
            "password": "wrong_password",
            "username": "fake_user",
            "stationName": f"pcapi - {settings.ENV}",
        }
        assert requests_mock.last_request.url == "https://cinema.example.com/api/vendors/login?ignore_device=True"
        assert cinema_details.token == "old-token"
        assert cinema_details.tokenExpirationDate == datetime.datetime(2022, 10, 1)
        assert (
            str(exc.value) == "Unexpected 400 response from Boost login API on "
            "https://cinema.example.com/api/vendors/login?ignore_device=True: Vendor login failed. Wrong password!"
        )


class BoostLogoutTest:
    def test_logout(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="old-token",
        )
        response_json = {"code": 200, "message": "OK"}
        requests_mock.post("https://cinema.example.com/api/vendors/logout", json=response_json)

        boost.logout(cinema_details)

        assert requests_mock.last_request.headers["Authorization"] == "Bearer old-token"


class BoostGetResourceTest:
    def test_with_valid_non_expired_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="dG90bw==",
        )
        resource = boost.ResourceBoost.EXAMPLE
        params = {"page": 1}
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        get_adapter = requests_mock.get("https://cinema.example.com/example?page=1", json={"key": "value"})
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login")

        json_data = boost.get_resource(cinema_str_id, resource, params)

        assert login_adapter.call_count == 0
        assert get_adapter.last_request.headers["Authorization"] == "Bearer dG90bw=="
        assert json_data == {"key": "value"}

    def test_with_expired_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="old-token",
            tokenExpirationDate=datetime.datetime(2022, 10, 1),
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        response_data = {"key": "value"}
        get_adapter = requests_mock.get("https://cinema.example.com/example", json=response_data)
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        json_data = boost.get_resource(cinema_str_id, resource)

        assert login_adapter.call_count == 1
        assert get_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert json_data == response_data

    def test_with_non_expired_invalid_token(self, requests_mock, caplog):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="invalid-token",
            tokenExpirationDate=datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        invalid_token_response_json = {
            "code": 401,
            "message": "Invalid JWT Token",
        }
        response_data = {"key": "value"}
        get_adapter = requests_mock.get(
            "https://cinema.example.com/example",
            [
                {"json": invalid_token_response_json, "status_code": 401},
                {"json": response_data, "status_code": 200},
            ],
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        with caplog.at_level(logging.INFO):
            json_data = boost.get_resource(cinema_str_id, resource)
            assert caplog.records[1].message == "Caught exception, retrying"
            assert caplog.records[1].extra["exception"] == "BoostInvalidTokenException"

        assert login_adapter.call_count == 1
        assert get_adapter.call_count == 2
        assert get_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert json_data == response_data

    def test_without_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token=None,
            tokenExpirationDate=None,
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        response_data = {"key": "value"}
        get_adapter = requests_mock.get("https://cinema.example.com/example", json=response_data)
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        json_data = boost.get_resource(cinema_str_id, resource)

        assert login_adapter.call_count == 1
        assert get_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert json_data == response_data

    def test_should_raise_if_error(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="token",
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.get(
            "https://cinema.example.com/example",
            status_code=417,
            reason="Expectation failed",
            json={"message": "Why must you fail me so often ?"},
        )

        with pytest.raises(boost_exceptions.BoostAPIException) as exc:
            boost.get_resource(cinema_str_id, resource)

        assert requests_mock.last_request.url == "https://cinema.example.com/example"
        assert requests_mock.last_request.headers["Authorization"] == "Bearer token"
        assert isinstance(exc.value, boost_exceptions.BoostAPIException)
        assert "token" not in str(exc.value)
        assert (
            "Error on Boost API on GET ResourceBoost.EXAMPLE : Expectation failed - Why must you fail me so often ?"
            == str(exc.value)
        )


class BoostPostResourceTest:
    def test_with_valid_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="dG90bw==",
        )
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        resource = boost.ResourceBoost.EXAMPLE
        adapter_response_data = {"message": "OK"}
        requests_mock.post(
            "https://cinema.example.com/example",
            status_code=204,
            json=adapter_response_data,
            headers={"Content-Type": "application/json"},
        )

        body = BaseModel(key=1)
        response = boost.post_resource(cinema_str_id, resource, body)

        assert requests_mock.last_request.url == "https://cinema.example.com/example"
        assert response == adapter_response_data

    def test_without_valid_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="old-token",
            tokenExpirationDate=datetime.datetime(2022, 10, 1),
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        adapter_response_data = {"key": "value"}
        post_adapter = requests_mock.post(
            "https://cinema.example.com/example",
            status_code=204,
            json=adapter_response_data,
            headers={"Content-Type": "application/json"},
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        body = BaseModel(key=1)
        response = boost.post_resource(cinema_str_id, resource, body)

        assert login_adapter.call_count == 1
        assert post_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert response == adapter_response_data

    def test_without_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token=None,
            tokenExpirationDate=None,
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        adapter_response_data = {"key": "value"}
        post_adapter = requests_mock.post(
            "https://cinema.example.com/example",
            status_code=204,
            json=adapter_response_data,
            headers={"Content-Type": "application/json"},
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        body = BaseModel(key=1)
        response = boost.post_resource(cinema_str_id, resource, body)

        assert login_adapter.call_count == 1
        assert post_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert response == adapter_response_data

    def test_should_raise_if_error(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="token",
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.post(
            "https://cinema.example.com/example",
            status_code=417,
            reason="Expectation failed",
            json={"message": "Why must you fail me so often ?"},
        )

        with pytest.raises(boost_exceptions.BoostAPIException) as exc:
            body = BaseModel(key=1)
            boost.post_resource(cinema_str_id, resource, body)

        assert requests_mock.last_request.url == "https://cinema.example.com/example"
        assert requests_mock.last_request.headers["Authorization"] == "Bearer token"
        assert isinstance(exc.value, boost_exceptions.BoostAPIException)
        assert "token" not in str(exc.value)
        assert (
            "Error on Boost API on POST ResourceBoost.EXAMPLE : Expectation failed - Why must you fail me so often ?"
            == str(exc.value)
        )

    def test_with_non_expired_invalid_token(self, requests_mock, caplog):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="invalid-token",
            tokenExpirationDate=datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        invalid_token_response_json = {
            "code": 401,
            "message": "Invalid JWT Token",
        }
        expected_response = {"key": "value"}
        get_adapter = requests_mock.post(
            "https://cinema.example.com/example",
            [
                {"json": invalid_token_response_json, "status_code": 401},
                {
                    "json": expected_response,
                    "status_code": 204,
                    "headers": {"Content-Type": "application/json"},
                },
            ],
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        body = BaseModel(key=1)
        with caplog.at_level(logging.INFO):
            json_data = boost.post_resource(cinema_str_id, resource, body)
            assert caplog.records[1].message == "Caught exception, retrying"
            assert caplog.records[1].extra["exception"] == "BoostInvalidTokenException"

        assert login_adapter.call_count == 1
        assert get_adapter.call_count == 2
        assert get_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert json_data == expected_response


class BoostPutResourceTest:
    def test_with_valid_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="dG90bw==",
        )
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        resource = boost.ResourceBoost.EXAMPLE

        requests_mock.put(
            "https://cinema.example.com/example",
            status_code=204,
            json={"message": "OK"},
            headers={"Content-Type": "application/json"},
        )

        body = BaseModel(key=1)
        response = boost.put_resource(cinema_str_id, resource, body)

        assert requests_mock.last_request.url == "https://cinema.example.com/example"
        assert response == {"message": "OK"}

    def test_without_valid_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="old-token",
            tokenExpirationDate=datetime.datetime(2022, 10, 1),
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        adapter_response_data = {"key": "value"}
        put_adapter = requests_mock.put(
            "https://cinema.example.com/example",
            status_code=204,
            json=adapter_response_data,
            headers={"Content-Type": "application/json"},
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        body = BaseModel(key=1)
        response = boost.put_resource(cinema_str_id, resource, body)

        assert login_adapter.call_count == 1
        assert put_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert response == adapter_response_data

    def test_without_stored_token(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token=None,
            tokenExpirationDate=None,
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        adapter_response_data = {"key": "value"}
        put_adapter = requests_mock.put(
            "https://cinema.example.com/example",
            status_code=204,
            json=adapter_response_data,
            headers={"Content-Type": "application/json"},
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        body = BaseModel(key=1)
        response = boost.put_resource(cinema_str_id, resource, body)

        assert login_adapter.call_count == 1
        assert put_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert response == adapter_response_data

    def test_should_raise_if_error(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="token",
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider

        requests_mock.put(
            "https://cinema.example.com/example",
            status_code=417,
            reason="Expectation failed",
            json={"message": "Why must you fail me so often ?"},
        )

        with pytest.raises(boost_exceptions.BoostAPIException) as exc:
            body = BaseModel(key=1)
            boost.put_resource(cinema_str_id, resource, body)

        assert requests_mock.last_request.url == "https://cinema.example.com/example"
        assert requests_mock.last_request.headers["Authorization"] == "Bearer token"
        assert isinstance(exc.value, boost_exceptions.BoostAPIException)
        assert "token" not in str(exc.value)
        assert (
            "Error on Boost API on PUT ResourceBoost.EXAMPLE : Expectation failed - Why must you fail me so often ?"
            == str(exc.value)
        )

    def test_with_non_expired_invalid_token(self, requests_mock, caplog):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema.example.com/",
            token="invalid-token",
            tokenExpirationDate=datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        )
        resource = boost.ResourceBoost.EXAMPLE
        cinema_str_id = cinema_details.cinemaProviderPivot.idAtProvider
        invalid_token_response_json = {
            "code": 401,
            "message": "Invalid JWT Token",
        }
        expected_response = {"message": "OK"}
        get_adapter = requests_mock.put(
            "https://cinema.example.com/example",
            [
                {"json": invalid_token_response_json, "status_code": 401},
                {
                    "json": expected_response,
                    "status_code": 204,
                    "headers": {"Content-Type": "application/json"},
                },
            ],
        )
        login_response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        login_adapter = requests_mock.post("https://cinema.example.com/api/vendors/login", json=login_response_json)

        body = BaseModel(key=1)

        with caplog.at_level(logging.INFO):
            json_data = boost.put_resource(cinema_str_id, resource, body)
            assert caplog.records[1].message == "Caught exception, retrying"
            assert caplog.records[1].extra["exception"] == "BoostInvalidTokenException"

        assert login_adapter.call_count == 1
        assert get_adapter.call_count == 2
        assert get_adapter.last_request.headers["Authorization"] == "Bearer new-token"
        assert json_data == expected_response
