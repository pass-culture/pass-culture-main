# from unittest.mock import patch

# from pcapi.admin.custom_views.pro_user_view import ProUserView
# import pcapi.core.users.factories as users_factories
# from pcapi.core.users.models import User

# from tests.conftest import TestClient
# from tests.conftest import clean_database


# class ProUserViewTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_pro_user_edition(self, mocked_validate_csrf_token, app):
#         # Given
#         admin_user = users_factories.AdminFactory()
#         pro_user = users_factories.ProFactory()

#         data = dict(
#             csrf_token="token",
#             firstName=pro_user.firstName,
#             lastName=pro_user.lastName,
#             dateOfBirth="",
#             departementCode="06",
#             postalCode="06000",
#             comment="",
#             email=pro_user.email,
#             phoneNumber="0601020304",
#         )

#         # When
#         client = TestClient(app.test_client()).with_session_auth(admin_user.email)
#         response = client.post(f"/pc/back-office/pro_users/edit?id={pro_user.id}", form=data)

#         # Then
#         assert response.status_code == 302

#         updated_user = User.query.filter_by(email=pro_user.email).first()
#         assert updated_user.firstName == pro_user.firstName
#         assert updated_user.lastName == pro_user.lastName
#         assert updated_user.dateOfBirth is None
#         assert updated_user.departementCode == "06"
#         assert updated_user.postalCode == "06000"
#         assert updated_user.phoneNumber == "+33601020304"

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_pro_user_edition_phone_number_error(self, mocked_validate_csrf_token, app):
#         # Given
#         admin_user = users_factories.AdminFactory()
#         pro_user = users_factories.ProFactory()

#         data = dict(
#             csrf_token="token",
#             firstName=pro_user.firstName,
#             lastName=pro_user.lastName,
#             dateOfBirth="",
#             departementCode="06",
#             postalCode="06000",
#             comment="",
#             email=pro_user.email,
#             phoneNumber="+++123",
#         )

#         # When
#         client = TestClient(app.test_client()).with_session_auth(admin_user.email)
#         response = client.post(f"/pc/back-office/pro_users/edit?id={pro_user.id}", form=data)

#         # Then
#         assert response.status_code == 200

#         assert "Numéro de téléphone invalide" in response.data.decode("utf8")

#         updated_user = User.query.filter_by(email=pro_user.email).first()
#         assert updated_user.departementCode == pro_user.departementCode
#         assert updated_user.postalCode == pro_user.postalCode
#         assert updated_user.phoneNumber == pro_user.phoneNumber

#     def test_order_by_works(self, app, db_session):
#         view = ProUserView(model=User, session=db_session)
#         view.get_list(page=1, sort_column="email", sort_desc="", search="", filters="")

#     @clean_database
#     # FIXME (dbaty, 2020-12-16): I could not find a quick way to
#     # generate a valid CSRF token in tests. This should be fixed.
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_suspend_pro(self, mocked_validate_csrf_token, app):
#         admin = users_factories.AdminFactory(email="admin15@example.com")
#         pro = users_factories.ProFactory(email="user15@example.com")

#         client = TestClient(app.test_client()).with_session_auth(admin.email)
#         url = f"/pc/back-office/pro_users/suspend?user_id={pro.id}"
#         data = {
#             "reason": "fraud suspicion",
#             "csrf_token": "token",
#         }
#         response = client.post(url, form=data)

#         assert response.status_code == 302
#         assert not pro.isActive

#     @clean_database
#     # FIXME (dbaty, 2020-12-16): I could not find a quick way to
#     # generate a valid CSRF token in tests. This should be fixed.
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_unsuspend_pro(self, mocked_validate_csrf_token, app):
#         admin = users_factories.AdminFactory(email="admin15@example.com")
#         pro = users_factories.ProFactory(email="user15@example.com", isActive=False)

#         client = TestClient(app.test_client()).with_session_auth(admin.email)
#         url = f"/pc/back-office/pro_users/unsuspend?user_id={pro.id}"
#         data = {
#             "reason": "fraud",
#             "csrf_token": "token",
#         }
#         response = client.post(url, form=data)

#         assert response.status_code == 302
#         assert pro.isActive
