# from unittest.mock import patch

# import pytest

# import pcapi.core.offerers.factories as offerers_factories
# import pcapi.core.offerers.models as offerers_models
# import pcapi.core.users.factories as users_factories

# from tests.conftest import clean_database


# class OffererTagViewTest:
#     @pytest.mark.parametrize("name", ["tag", "tag_with_underscores", "[tag]!", "tag_140ch_" * 14])
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_create_tag(self, mocked_validate_csrf_token, client, name):
#         users_factories.AdminFactory(email="admin@example.com")
#         category = offerers_factories.OffererTagCategoryFactory()

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post("/pc/back-office/offerertag/new/", form={"name": name, "categories": [category.id]})

#         assert response.status_code == 302
#         assert offerers_models.OffererTag.query.count() == 1
#         tag = offerers_models.OffererTag.query.first()
#         assert tag.name == name
#         assert tag.categories == [category]

#     @pytest.mark.parametrize(
#         "name", ["tag ", " tag", "t ag", "tag\t", "\ttag", "ta\tg", "\ntag", "t\nag", "\rtag", "tag\r", "t\rag"]
#     )
#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_create_tag_with_whitespace(self, mocked_validate_csrf_token, client, name):
#         users_factories.AdminFactory(email="admin@example.com")

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post("/pc/back-office/offerertag/new/", form={"name": name})

#         assert response.status_code == 200
#         assert "Le nom ne doit contenir aucun caractère d&#39;espacement" in response.data.decode("utf8")
#         assert offerers_models.OffererTag.query.count() == 0

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_create_tag_too_long(self, mocked_validate_csrf_token, client):
#         users_factories.AdminFactory(email="admin@example.com")

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post("/pc/back-office/offerertag/new/", form={"name": "x" * 141})

#         assert response.status_code == 200
#         assert "Le nom ne peut excéder 140 caractères" in response.data.decode("utf8")
#         assert offerers_models.OffererTag.query.count() == 0

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_edit_tag(self, mocked_validate_csrf_token, client):
#         users_factories.AdminFactory(email="admin@example.com")

#         category1 = offerers_factories.OffererTagCategoryFactory(name="comptage")
#         category2 = offerers_factories.OffererTagCategoryFactory(name="homologation")
#         tag = offerers_factories.OffererTagFactory(name="test_edit_tag", categories=[category1])
#         offerer = offerers_factories.OffererFactory(tags=[tag])

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post(
#             f"/pc/back-office/offerertag/edit/?id={offerer.tags[0].id}",
#             form={"name": "test_edit_tag", "categories": [category2.id]},
#         )

#         assert response.status_code == 302
#         assert len(offerer.tags) == 1
#         assert offerer.tags[0].name == "test_edit_tag"
#         assert offerer.tags[0].categories == [category2]

#     @clean_database
#     @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
#     def test_delete_tag(self, mocked_validate_csrf_token, client):
#         users_factories.AdminFactory(email="admin@example.com")

#         offerer = offerers_factories.OffererFactory(tags=[offerers_factories.OffererTagFactory(name="test_delete_tag")])

#         api_client = client.with_session_auth("admin@example.com")

#         response = api_client.post("/pc/back-office/offerertag/delete/", form={"id": offerer.tags[0].id})

#         assert response.status_code == 302
#         assert len(offerer.tags) == 0
