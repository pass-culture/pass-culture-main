# import datetime
# from unittest.mock import patch

# from freezegun import freeze_time

# import pcapi.core.offerers.factories as offerers_factories
# import pcapi.core.providers.factories as providers_factories
# import pcapi.core.providers.models as providers_models
# import pcapi.core.providers.repository as providers_repository
# from pcapi.core.users.factories import AdminFactory

# from tests.conftest import TestClient
# from tests.conftest import clean_database


# class CreateBoostPivotTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_create_boost_information_api_ok(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="admin@example.fr")
#         venue = offerers_factories.VenueFactory()
#         requests_mock.post(
#             "https://test.com/api/vendors/login?ignore_device=True",
#             json={"message": "Login successful", "token": "jwt-token"},
#         )

#         data = {
#             "venue_id": venue.id,
#             "cinema_id": "12",
#             "username": "username_test",
#             "password": "password_test",
#             "cinema_url": "https://test.com",
#         }
#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post("/pc/back-office/boost/new", form=data)

#         assert response.status_code == 302
#         cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
#             providers_models.CinemaProviderPivot.venueId == venue.id
#         ).one()
#         assert cinema_provider_pivot.idAtProvider == "12"
#         boost_cinema_details = providers_models.BoostCinemaDetails.query.filter(
#             providers_models.BoostCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
#         ).one()
#         assert boost_cinema_details.username == "username_test"
#         assert boost_cinema_details.password == "password_test"
#         assert boost_cinema_details.cinemaUrl == "https://test.com/"
#         flash_mock.assert_called_once_with("Connexion à l'API OK.")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_create_boost_information_api_ko(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="admin@example.fr")
#         venue = offerers_factories.VenueFactory()
#         requests_mock.post(
#             "https://test.com/api/vendors/login?ignore_device=True",
#             status_code=401,
#             json={"message": "Login fail"},
#         )

#         data = {
#             "venue_id": venue.id,
#             "cinema_id": "12",
#             "username": "username_test",
#             "password": "password_test",
#             "cinema_url": "https://test.com",
#         }
#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post("/pc/back-office/boost/new", form=data)

#         assert response.status_code == 302
#         cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
#             providers_models.CinemaProviderPivot.venueId == venue.id
#         ).one()
#         assert cinema_provider_pivot.idAtProvider == "12"
#         boost_cinema_details = providers_models.BoostCinemaDetails.query.filter(
#             providers_models.BoostCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
#         ).one()
#         assert boost_cinema_details.username == "username_test"
#         assert boost_cinema_details.password == "password_test"
#         assert boost_cinema_details.cinemaUrl == "https://test.com/"
#         flash_mock.assert_called_once_with("Connexion à l'API KO.", "error")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_id_at_provider_unicity(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
#         _cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=boost_provider, idAtProvider="cinema_test"
#         )
#         venue_2 = offerers_factories.VenueFactory()

#         data = {
#             "venue_id": venue_2.id,
#             "account_id": "account_test",
#             "cinema_id": "cinema_test",
#             "api_token": "token_test",
#         }
#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post("/pc/back-office/boost/new", form=data)

#         assert response.status_code == 200
#         assert "Cet identifiant cinéma existe déjà pour un autre lieu" in response.data.decode("utf8")
#         assert providers_models.CinemaProviderPivot.query.count() == 1

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_create_boost_information_when_venue_already_has_cinema_provider(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
#         _cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=boost_provider, idAtProvider="cinema1_test"
#         )

#         data = {
#             "venue_id": venue.id,
#             "cinema_id": "cinema2_test",
#             "username": "username_test",
#             "password": "password_test",
#             "cinema_url": "https://test.com",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post("/pc/back-office/boost/new", form=data)
#         assert response.status_code == 200
#         assert "Des identifiants cinéma existent déjà pour ce lieu id=" in response.data.decode("utf8")
#         assert providers_models.CinemaProviderPivot.query.count() == 1


# class EditBoostPivotTest:
#     @clean_database
#     @freeze_time("2022-10-12 17:09:25")
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_update_boost_information(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="admin@example.fr")
#         boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
#         venue = offerers_factories.VenueFactory()
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=boost_provider, idAtProvider="12"
#         )
#         boost_cinema_details = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot,
#             cinemaUrl="https://test.com/",
#             username="username_test",
#             password="password_test",
#             token=None,
#         )
#         requests_mock.post(
#             "https://new-url.com/api/vendors/login?ignore_device=True",
#             json={"message": "Login successful", "token": "jwt-token"},
#         )

#         data = {
#             "venue_id": venue.id,
#             "cinema_id": "13",
#             "username": "new_username",
#             "password": "new_password",
#             "cinema_url": "https://new-url.com/",
#         }

#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post(f"/pc/back-office/boost/edit/?id={boost_cinema_details.id}", form=data)

#         assert response.status_code == 302
#         assert cinema_provider_pivot.idAtProvider == "13"
#         assert boost_cinema_details.username == "new_username"
#         assert boost_cinema_details.password == "new_password"
#         assert boost_cinema_details.cinemaUrl == "https://new-url.com/"
#         assert boost_cinema_details.token == "jwt-token"
#         assert boost_cinema_details.tokenExpirationDate == datetime.datetime(2022, 10, 13, 17, 9, 25)
#         flash_mock.assert_called_once_with("Connexion à l'API OK.")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_update_password_api_ok(self, flask_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         cinema_id = "cinema_test"
#         cinema_provider_pivot = providers_factories.BoostCinemaProviderPivotFactory(venue=venue, idAtProvider=cinema_id)
#         username = "cinema_test"
#         boost_cinema_details = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot,
#             cinemaUrl="https://example.com/",
#             username=username,
#             password="password_test",
#         )
#         requests_mock.post(
#             "https://example.com/api/vendors/login?ignore_device=True",
#             json={"message": "Login successful", "token": "jwt-token"},
#         )

#         data = {
#             "venue_id": venue.id,
#             "cinema_id": cinema_id,
#             "username": username,
#             "password": "toto",
#             "cinema_url": "https://example.com/",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/boost/edit/?id={boost_cinema_details.id}", form=data)

#         assert cinema_provider_pivot.idAtProvider == cinema_id
#         assert boost_cinema_details.cinemaUrl == "https://example.com/"
#         assert boost_cinema_details.username == username
#         assert boost_cinema_details.password == "toto"
#         assert response.status_code == 302
#         flask_mock.assert_called_once_with("Connexion à l'API OK.")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_update_password_api_ko(self, flask_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         cinema_id = "cinema_test"
#         cinema_provider_pivot = providers_factories.BoostCinemaProviderPivotFactory(venue=venue, idAtProvider=cinema_id)
#         username = "cinema_test"
#         boost_cinema_details = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot,
#             cinemaUrl="https://example.com/",
#             username=username,
#             password="password_test",
#         )
#         requests_mock.post(
#             "https://example.com/api/vendors/login?ignore_device=True",
#             status_code=401,
#             json={"message": "Login fail"},
#         )

#         data = {
#             "venue_id": venue.id,
#             "cinema_id": cinema_id,
#             "username": username,
#             "password": "toto",
#             "cinema_url": "https://example.com/",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/boost/edit/?id={boost_cinema_details.id}", form=data)

#         assert cinema_provider_pivot.idAtProvider == cinema_id
#         assert boost_cinema_details.cinemaUrl == "https://example.com/"
#         assert boost_cinema_details.username == username
#         assert boost_cinema_details.password == "toto"
#         assert response.status_code == 302
#         flask_mock.assert_called_once_with("Connexion à l'API KO.", "error")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_cannot_reuse_cinema_id_at_provider(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="user@example.com")
#         boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")

#         venue_1 = offerers_factories.VenueFactory()
#         cinema_id_1 = "cinema_1"
#         cinema_provider_pivot_1 = providers_factories.BoostCinemaProviderPivotFactory(
#             venue=venue_1, provider=boost_provider, idAtProvider=cinema_id_1
#         )
#         username_1 = "cinema_test"
#         _boost_cinema_details_1 = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot_1,
#             cinemaUrl="https://example.com/",
#             username=username_1,
#             password="password_test",
#         )
#         venue_2 = offerers_factories.VenueFactory()
#         cinema_id_2 = "cinema_2"
#         cinema_provider_pivot_2 = providers_factories.CinemaProviderPivotFactory(
#             venue=venue_2, provider=boost_provider, idAtProvider=cinema_id_2
#         )
#         username_2 = "cinema_2"
#         boost_cinema_details_2 = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot_2,
#             cinemaUrl="https://another-example.com/",
#             username=username_2,
#             password="another_password",
#         )

#         data = {
#             "venue_id": venue_2.id,
#             "cinema_id": cinema_id_1,
#             "username": username_2,
#             "password": "another_password",
#             "cinema_url": "https://another-example.com/",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/boost/edit/?id={boost_cinema_details_2.id}", form=data)

#         # no changes
#         assert cinema_provider_pivot_2.idAtProvider == cinema_id_2
#         assert boost_cinema_details_2.cinemaUrl == "https://another-example.com/"
#         assert boost_cinema_details_2.username == username_2
#         assert boost_cinema_details_2.password == "another_password"
#         assert response.status_code == 200  # no redirect
#         assert "Cet identifiant cinéma existe déjà pour un autre lieu" in response.data.decode("utf8")


# class DeleteBoostPivotTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_delete_boost_information(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="admin@example.fr")
#         boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
#         venue = offerers_factories.VenueFactory()
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=boost_provider, idAtProvider="12"
#         )
#         boost_cinema_details = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot,
#             cinemaUrl="https://test.com/",
#             username="username_test",
#             password="password_test",
#         )

#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post("/pc/back-office/boost/delete", form={"id": boost_cinema_details.id})

#         assert response.status_code == 302
#         assert providers_models.BoostCinemaDetails.query.count() == 0
#         assert providers_models.CinemaProviderPivot.query.count() == 0

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_should_not_delete_boost_pivot_when_venue_provider_exist(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="admin@example.fr")
#         boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
#         venue = offerers_factories.VenueFactory()
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=boost_provider, idAtProvider="12"
#         )
#         boost_cinema_details = providers_factories.BoostCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot,
#             cinemaUrl="https://test.com/",
#             username="username_test",
#             password="password_test",
#         )
#         providers_factories.VenueProviderFactory(venue=venue, provider=boost_provider)

#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post("/pc/back-office/boost/delete", form={"id": boost_cinema_details.id})

#         assert response.status_code == 302
#         assert providers_models.BoostCinemaDetails.query.count() == 1
#         assert providers_models.CinemaProviderPivot.query.count() == 1
