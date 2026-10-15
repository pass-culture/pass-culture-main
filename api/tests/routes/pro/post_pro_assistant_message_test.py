from unittest import mock

import pytest

from pcapi.connectors import pro_assistant as pro_assistant_connector
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.features(WIP_ENABLE_PRO_ASSISTANT=True)
class PostProAssistantMessageTest:
    def test_answer(self, client):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        response = client.with_session_auth(user.email).post(
            "/assistant/messages",
            json={"message": "Comment créer une offre ?", "offererId": offerer.id, "currentPath": "/accueil"},
        )

        assert response.status_code == 200
        assert len(response.json["conversationId"]) == 32
        # Answer of the testing backend
        assert response.json["answer"].startswith("Pour créer une offre individuelle")
        assert response.json["links"] == [
            {"label": "Créer une offre individuelle", "path": "/offre/individuelle/creation/description"}
        ]
        assert response.json["helpArticles"] == []
        assert response.json["outOfScope"] is False

    def test_continue_conversation(self, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(user.email)
        first_response = client.post("/assistant/messages", json={"message": "Bonjour"})

        response = client.post(
            "/assistant/messages",
            json={"message": "Et ensuite ?", "conversationId": first_response.json["conversationId"]},
        )

        assert response.status_code == 200
        assert response.json["conversationId"] == first_response.json["conversationId"]

    def test_user_without_access_to_offerer(self, client):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()

        response = client.with_session_auth(user.email).post(
            "/assistant/messages", json={"message": "Bonjour", "offererId": offerer.id}
        )

        assert response.status_code == 404

    def test_anonymous_user(self, client):
        response = client.post("/assistant/messages", json={"message": "Bonjour"})

        assert response.status_code == 401

    @pytest.mark.parametrize(
        "body",
        [
            {"message": ""},
            {"message": "a" * 501},
            {"message": "Bonjour", "conversationId": "../../other-key"},
            {"message": "Bonjour", "unexpected": "field"},
        ],
    )
    def test_invalid_body(self, client, body):
        user = users_factories.ProFactory()

        response = client.with_session_auth(user.email).post("/assistant/messages", json=body)

        assert response.status_code == 400

    @pytest.mark.settings(PRO_ASSISTANT_RATE_LIMIT_SHORT_MAX=1)
    def test_rate_limited(self, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(user.email)
        client.post("/assistant/messages", json={"message": "Bonjour"})

        response = client.post("/assistant/messages", json={"message": "Bonjour"})

        assert response.status_code == 429
        assert response.json == {"global": "Vous avez posé beaucoup de questions. Merci de réessayer un peu plus tard."}

    @pytest.mark.settings(PRO_ASSISTANT_MAX_TURNS=1)
    def test_conversation_too_long(self, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(user.email)
        first_response = client.post("/assistant/messages", json={"message": "Bonjour"})

        response = client.post(
            "/assistant/messages",
            json={"message": "Et ensuite ?", "conversationId": first_response.json["conversationId"]},
        )

        assert response.status_code == 400

    @pytest.mark.features(WIP_ENABLE_PRO_ASSISTANT=False)
    def test_feature_disabled(self, client):
        user = users_factories.ProFactory()

        response = client.with_session_auth(user.email).post("/assistant/messages", json={"message": "Bonjour"})

        assert response.status_code == 403

    @mock.patch(
        "pcapi.connectors.pro_assistant.generate",
        side_effect=pro_assistant_connector.ProAssistantApiException("status 400"),
    )
    def test_llm_unavailable(self, _generate_mock, client):
        user = users_factories.ProFactory()

        response = client.with_session_auth(user.email).post("/assistant/messages", json={"message": "Bonjour"})

        # Not a 503, which would redirect the user to the maintenance page
        assert response.status_code == 424
        assert response.json == {"global": "L'assistant est momentanément indisponible. Merci de réessayer plus tard."}
