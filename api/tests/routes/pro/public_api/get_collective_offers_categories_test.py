from flask import url_for
import pytest

import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetCategoriesTest:
    def test_list_categories(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_categories")
        )

        # Then
        assert response.status_code == 200

        assert response.json == [
            {"id": "BEAUX_ARTS", "name": "Beaux-arts"},
            {"id": "CARTE_JEUNES", "name": "Carte jeunes"},
            {"id": "CINEMA", "name": "Cinéma"},
            {"id": "CONFERENCE", "name": "Conférences, rencontres"},
            {"id": "FILM", "name": "Films, vidéos"},
            {"id": "INSTRUMENT", "name": "Instrument de musique"},
            {"id": "JEU", "name": "Jeux"},
            {"id": "LIVRE", "name": "Livre"},
            {"id": "MEDIA", "name": "Médias"},
            {"id": "MUSEE", "name": "Musée, patrimoine, architecture, arts visuels"},
            {"id": "MUSIQUE_ENREGISTREE", "name": "Musique enregistrée"},
            {"id": "MUSIQUE_LIVE", "name": "Musique live"},
            {"id": "PRATIQUE_ART", "name": "Pratique artistique"},
            {"id": "SPECTACLE", "name": "Spectacle vivant"},
        ]

    def test_list_categories_user_auth_returns_401(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        response = client.with_session_auth(user_offerer.user.email).get(url_for("pro_public_api_v2.list_categories"))

        # Then
        assert response.status_code == 401

    def test_list_categories_anonymous_returns_401(self, client):
        # Given

        # When
        response = client.get(url_for("pro_public_api_v2.list_categories"))

        # Then
        assert response.status_code == 401
