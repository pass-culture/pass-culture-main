import pcapi.core.categories.categories as categories
import pcapi.core.categories.subcategories as subcategories
import pcapi.core.users.factories as users_factories


class CategoryViewTest:
    def test_authorized_user(self, app, db_session, client):
        admin = users_factories.AdminFactory(email="admin@example.com")
        client.with_session_auth(admin.email)

        response = client.get("/pc/back-office/categories")

        assert response.status_code == 200
        assert any(c.id in response.data.decode("utf-8") for c in categories.ALL_CATEGORIES)


class SubcategoryViewTest:
    def test_authorized_user(self, app, db_session, client):
        admin = users_factories.AdminFactory(email="admin@example.com")
        client.with_session_auth(admin.email)

        response = client.get("/pc/back-office/subcategories")

        assert response.status_code == 200
        assert any(s.id in response.data.decode("utf-8") for s in subcategories.ALL_SUBCATEGORIES)
