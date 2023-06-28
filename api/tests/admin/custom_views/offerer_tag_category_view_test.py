# from unittest.mock import patch

# import pcapi.core.offerers.factories as offerers_factories
# import pcapi.core.offerers.models as offerers_models
# import pcapi.core.users.factories as users_factories

# from tests.conftest import clean_database


# class OffererTagCategoryViewTest:
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_create_tag_category(self, mocked_validate_csrf_token, client):
#         users_factories.AdminFactory(email="admin@example.com")

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post("/pc/back-office/offerertagcategory/new/", form={"name": "test-category"})

#         assert response.status_code == 302
#         assert offerers_models.OffererTagCategory.query.count() == 1
#         category = offerers_models.OffererTagCategory.query.first()
#         assert category.name == "test-category"

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_edit_tag_category(self, mocked_validate_csrf_token, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         category = offerers_factories.OffererTagCategoryFactory()

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post(
#             f"/pc/back-office/offerertagcategory/edit/?id={category.id}",
#             form={"name": "updated-category", "label": "Catégorie de test"},
#         )

#         assert response.status_code == 302
#         assert category.name == "updated-category"
#         assert category.label == "Catégorie de test"

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_delete_tag_category(self, mocked_validate_csrf_token, client):
#         users_factories.AdminFactory(email="admin@example.com")
#         category = offerers_factories.OffererTagCategoryFactory()

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post("/pc/back-office/offerertagcategory/delete/", form={"id": category.id})

#         assert response.status_code == 302
#         assert offerers_models.OffererTagCategory.query.count() == 0
