import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class FailureTest:
    def test_failure(self):
        assert False, "Ceci est un échec"


class AutocompleteOfferersTest:
    def test_autocomplete_on_name(self, client):
        admin = users_factories.AdminFactory()
        offerer1 = offerers_factories.OffererFactory(name="Le Petit Rintintin", siren="12345")
        offerer2 = offerers_factories.OffererFactory(name="Le Grand Rintintin", siren="12346")
        offerers_factories.OffererFactory(name="La Grande Lassie")

        client = client.with_session_auth(admin.email)
        response = client.get("/pc/back-office/autocomplete/offerers?q=rintin")

        assert response.status_code == 200
        assert response.json == {
            "items": [
                {"id": offerer2.id, "text": "Le Grand Rintintin (12346)"},
                {"id": offerer1.id, "text": "Le Petit Rintintin (12345)"},
            ]
        }

    def test_autocomplete_on_siren(self, client):
        admin = users_factories.AdminFactory()
        offerer1 = offerers_factories.OffererFactory(name="O2", siren="12345678")
        offerer2 = offerers_factories.OffererFactory(name="O1", siren="23456781")
        offerers_factories.OffererFactory(name="O3", siren="1111111")

        client = client.with_session_auth(admin.email)
        response = client.get("/pc/back-office/autocomplete/offerers?q=45678")

        assert response.status_code == 200
        assert response.json == {
            "items": [
                {"id": offerer2.id, "text": "O1 (23456781)"},
                {"id": offerer1.id, "text": "O2 (12345678)"},
            ]
        }

    def test_forbidden_unless_admin(self, client):
        user = users_factories.UserFactory()
        client = client.with_session_auth(user.email)
        response = client.get("/pc/back-office/autocomplete/offerers?q=rintin")
        assert response.status_code == 403
