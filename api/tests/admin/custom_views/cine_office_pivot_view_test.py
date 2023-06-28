# from unittest.mock import patch

# import pcapi.core.offerers.factories as offerers_factories
# import pcapi.core.providers.factories as providers_factories
# import pcapi.core.providers.models as providers_models
# from pcapi.core.providers.repository import get_provider_by_local_class
# from pcapi.core.users.factories import AdminFactory

# from tests.conftest import TestClient
# from tests.conftest import clean_database


# class CreateCineOfficePivotTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_create_cine_office_information_api_ok(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         requests_mock.get("https://account_test.test_cds_url/vad/rating?api_token=token_test", json=[])

#         data = {
#             "venue_id": venue.id,
#             "account_id": "account_test",
#             "cinema_id": "cinema_test",
#             "api_token": "token_test",
#         }
#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post("/pc/back-office/cine-office/new", form=data)

#         assert response.status_code == 302
#         cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
#             providers_models.CinemaProviderPivot.venueId == venue.id
#         ).one()
#         assert cinema_provider_pivot.idAtProvider == "cinema_test"
#         cds_cinema_details = providers_models.CDSCinemaDetails.query.filter(
#             providers_models.CDSCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
#         ).one()
#         assert cds_cinema_details.accountId == "account_test"
#         assert cds_cinema_details.cinemaApiToken == "token_test"
#         assert requests_mock.call_count == 1
#         flash_mock.assert_called_once_with("Connexion à l'API OK.")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_create_cine_office_information_api_ko(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         requests_mock.get(
#             "https://account_test.test_cds_url/vad/rating?api_token=token_test",
#             status_code=401,
#             reason="CONNECTION_ERROR : AUTHENTIFICATION_FAILED",
#         )

#         data = {
#             "venue_id": venue.id,
#             "account_id": "account_test",
#             "cinema_id": "cinema_test",
#             "api_token": "token_test",
#         }
#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post("/pc/back-office/cine-office/new", form=data)

#         assert response.status_code == 302
#         cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
#             providers_models.CinemaProviderPivot.venueId == venue.id
#         ).one()
#         assert cinema_provider_pivot.idAtProvider == "cinema_test"
#         cds_cinema_details = providers_models.CDSCinemaDetails.query.filter(
#             providers_models.CDSCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
#         ).one()
#         assert cds_cinema_details.accountId == "account_test"
#         assert cds_cinema_details.cinemaApiToken == "token_test"
#         assert requests_mock.call_count == 1
#         flash_mock.assert_called_once_with("Connexion à l'API KO.", "error")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_id_at_provider_unicity(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="user@example.com")
#         venue_1 = offerers_factories.VenueFactory()
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         _cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue_1, provider=cds_provider, idAtProvider="cinema_test"
#         )

#         venue_2 = offerers_factories.VenueFactory()

#         data = {
#             "venue_id": venue_2.id,
#             "account_id": "account_test",
#             "cinema_id": "cinema_test",
#             "api_token": "token_test",
#         }
#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post("/pc/back-office/cine-office/new", form=data)

#         assert response.status_code == 200
#         assert "Cet identifiant cinéma existe déjà pour un autre lieu" in response.data.decode("utf8")
#         assert providers_models.CinemaProviderPivot.query.count() == 1

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_create_cine_office_information_when_venue_already_has_cinema_provider(
#         self, _mocked_validate_csrf_token, app
#     ):
#         AdminFactory(email="user@example.com")
#         venue_1 = offerers_factories.VenueFactory()
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         _cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue_1, provider=cds_provider, idAtProvider="cinema1_test"
#         )

#         data = {
#             "venue_id": venue_1.id,
#             "account_id": "account2_test",
#             "cinema_id": "cinema2_test",
#             "api_token": "token2_test",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post("/pc/back-office/cine-office/new", form=data)

#         assert response.status_code == 200
#         assert "Des identifiants cinéma existent déjà pour ce lieu id=" in response.data.decode("utf8")
#         assert providers_models.CinemaProviderPivot.query.count() == 1


# class EditCineOfficePivotTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_update_editable_attributes_api_ok(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=cds_provider, idAtProvider="cinema_test"
#         )
#         cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
#         )
#         requests_mock.get("https://new_account_id.test_cds_url/vad/rating?api_token=new_token_id", json=[])

#         data = {
#             "venue_id": venue.id,
#             "account_id": "new_account_id",
#             "cinema_id": "new_cinema_id",
#             "api_token": "new_token_id",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/cine-office/edit/?id={cds_cinema_details.id}", form=data)

#         assert response.status_code == 302
#         assert cinema_provider_pivot.idAtProvider == "new_cinema_id"
#         assert cds_cinema_details.accountId == "new_account_id"
#         assert cds_cinema_details.cinemaApiToken == "new_token_id"
#         assert requests_mock.call_count == 1
#         flash_mock.assert_called_once_with("Connexion à l'API OK.")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_update_editable_attributes_api_ko(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=cds_provider, idAtProvider="cinema_test"
#         )
#         cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
#         )
#         requests_mock.get(
#             "https://new_account_id.test_cds_url/vad/rating?api_token=new_token_id",
#             status_code=401,
#             reason="CONNECTION_ERROR : AUTHENTIFICATION_FAILED",
#         )

#         data = {
#             "venue_id": venue.id,
#             "account_id": "new_account_id",
#             "cinema_id": "new_cinema_id",
#             "api_token": "new_token_id",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/cine-office/edit/?id={cds_cinema_details.id}", form=data)

#         assert response.status_code == 302
#         assert cinema_provider_pivot.idAtProvider == "new_cinema_id"
#         assert cds_cinema_details.accountId == "new_account_id"
#         assert cds_cinema_details.cinemaApiToken == "new_token_id"
#         assert requests_mock.call_count == 1
#         flash_mock.assert_called_once_with("Connexion à l'API KO.", "error")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     @patch("flask.flash")
#     def test_update_token(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
#         AdminFactory(email="user@example.com")
#         venue = offerers_factories.VenueFactory()
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         cinema_id = "cinema_test"
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=cds_provider, idAtProvider=cinema_id
#         )
#         account_id = "cinema_test"
#         cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot, accountId=account_id, cinemaApiToken="token_test"
#         )
#         requests_mock.get("https://cinema_test.test_cds_url/vad/rating?api_token=new_token_id", json=[])

#         data = {
#             "venue_id": venue.id,
#             "account_id": account_id,
#             "cinema_id": cinema_id,
#             "api_token": "new_token_id",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/cine-office/edit/?id={cds_cinema_details.id}", form=data)

#         assert cinema_provider_pivot.idAtProvider == cinema_id
#         assert cds_cinema_details.accountId == account_id
#         assert cds_cinema_details.cinemaApiToken == "new_token_id"
#         assert response.status_code == 302
#         assert requests_mock.call_count == 1
#         flash_mock.assert_called_once_with("Connexion à l'API OK.")

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_cannot_reuse_cinema_id_at_provider(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="user@example.com")
#         venue_1 = offerers_factories.VenueFactory()
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         cinema_id_1 = "cinema_1"
#         cinema_provider_pivot_1 = providers_factories.CinemaProviderPivotFactory(
#             venue=venue_1, provider=cds_provider, idAtProvider=cinema_id_1
#         )
#         account_id_1 = "cinema_1"
#         _cds_cinema_details_1 = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot_1, accountId=account_id_1, cinemaApiToken="token_test_1"
#         )
#         venue_2 = offerers_factories.VenueFactory()
#         cinema_id_2 = "cinema_2"
#         cinema_provider_pivot_2 = providers_factories.CinemaProviderPivotFactory(
#             venue=venue_2, provider=cds_provider, idAtProvider=cinema_id_2
#         )
#         account_id_2 = "cinema_2"
#         cds_cinema_details_2 = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot_2, accountId=account_id_2, cinemaApiToken="token_test_2"
#         )

#         data = {
#             "venue_id": venue_2.id,
#             "account_id": account_id_2,
#             "cinema_id": cinema_id_1,
#             "api_token": "token_test_2",
#         }

#         client = TestClient(app.test_client()).with_session_auth("user@example.com")
#         response = client.post(f"/pc/back-office/cine-office/edit/?id={cds_cinema_details_2.id}", form=data)

#         # no changes
#         assert cinema_provider_pivot_2.idAtProvider == cinema_id_2
#         assert cds_cinema_details_2.accountId == account_id_2
#         assert cds_cinema_details_2.cinemaApiToken == "token_test_2"
#         assert response.status_code == 200  # no redirect
#         assert "Cet identifiant cinéma existe déjà pour un autre lieu" in response.data.decode("utf8")


# class DeleteCineOfficePivotTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_delete_cine_office_information(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="admin@example.fr")
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         venue = offerers_factories.VenueFactory()
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=cds_provider, idAtProvider="cinema_test"
#         )
#         cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
#         )

#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post("/pc/back-office/cine-office/delete", form={"id": cds_cinema_details.id})

#         assert response.status_code == 302
#         assert providers_models.CDSCinemaDetails.query.count() == 0
#         assert providers_models.CinemaProviderPivot.query.count() == 0

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_should_not_delete_cine_office_pivot_when_venue_provider_exist(self, _mocked_validate_csrf_token, app):
#         AdminFactory(email="admin@example.fr")
#         cds_provider = get_provider_by_local_class("CDSStocks")
#         venue = offerers_factories.VenueFactory()
#         cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
#             venue=venue, provider=cds_provider, idAtProvider="cinema_test"
#         )
#         cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
#             cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
#         )
#         providers_factories.VenueProviderFactory(venue=venue, provider=cds_provider)

#         client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
#         response = client.post("/pc/back-office/cine-office/delete", form={"id": cds_cinema_details.id})

#         assert response.status_code == 302
#         assert providers_models.CDSCinemaDetails.query.count() == 1
#         assert providers_models.CinemaProviderPivot.query.count() == 1
