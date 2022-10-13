import datetime

from freezegun import freeze_time
import pytest

from pcapi.connectors import boost
import pcapi.core.external_bookings.boost.exceptions as boost_exceptions
import pcapi.core.providers.factories as providers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class CineDigitalServiceBuildUrlTest:
    def test_build_url(self):
        cinema_url = "https://cinema.example.com/"
        resource = boost.ResourceBoost.EXAMPLE

        url = boost._build_url(cinema_url, resource)

        assert url == "https://cinema.example.com/example"


@freeze_time("2022-10-12 17:09:25")
class BoostLoginTest:
    def test_login(self, requests_mock):
        cinema_details = providers_factories.BoostCinemaDetailsFactory(cinemaUrl="https://cinema.example.com/")
        response_json = {"code": 200, "message": "Login successful", "token": "new-token"}
        requests_mock.post("https://cinema.example.com/api/vendors/login", json=response_json)

        token = boost.login(cinema_details)

        assert requests_mock.last_request.json() == {
            "password": cinema_details.password,
            "username": cinema_details.username,
        }
        assert requests_mock.last_request.url == "https://cinema.example.com/api/vendors/login?ignore_device=False"
        assert token == cinema_details.token == "new-token"
        assert cinema_details.tokenExpirationDate == datetime.datetime(2022, 10, 13, 17, 9, 25)

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
            "password": cinema_details.password,
            "username": cinema_details.username,
        }
        assert requests_mock.last_request.url == "https://cinema.example.com/api/vendors/login?ignore_device=False"
        assert cinema_details.token == "old-token"
        assert cinema_details.tokenExpirationDate == datetime.datetime(2022, 10, 1)
        assert (
            str(exc.value) == "Unexpected 400 response from Boost API on "
            "https://cinema.example.com/api/vendors/login?ignore_device=False: Vendor login failed. Wrong password!"
        )


class BoostGetResourceTest:
    def test_with_valid_stored_token(self, requests_mock):
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

    def test_without_valid_stored_token(self, requests_mock):
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
