import pytest

import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetCategoriesTest:
    def test_list_sub_categories(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/subcategories"
        )

        # Then
        assert response.status_code == 200

        assert response.json == [
            {"id": "CINE_PLEIN_AIR", "label": "Cinéma plein air", "category": "Cinéma"},
            {"id": "FESTIVAL_CINE", "label": "Festival de cinéma", "category": "Cinéma"},
            {"id": "SEANCE_CINE", "label": "Séance de cinéma", "category": "Cinéma"},
            {"id": "EVENEMENT_CINE", "label": "Événement cinématographique", "category": "Cinéma"},
            {"id": "CONFERENCE", "label": "Conférence", "category": "Conférences, rencontres"},
            {"id": "RENCONTRE", "label": "Rencontre", "category": "Conférences, rencontres"},
            {"id": "RENCONTRE_EN_LIGNE", "label": "Rencontre en ligne", "category": "Conférences, rencontres"},
            {"id": "SALON", "label": "Salon, Convention", "category": "Conférences, rencontres"},
            {"id": "CONCOURS", "label": "Concours - jeux", "category": "Jeux"},
            {"id": "RENCONTRE_JEU", "label": "Rencontres - jeux", "category": "Jeux"},
            {"id": "EVENEMENT_JEU", "label": "Événements - jeux", "category": "Jeux"},
            {"id": "EVENEMENT_MUSIQUE", "label": "Autre type d'événement musical", "category": "Musique live"},
            {"id": "CONCERT", "label": "Concert", "category": "Musique live"},
            {"id": "FESTIVAL_MUSIQUE", "label": "Festival de musique", "category": "Musique live"},
            {"id": "VISITE", "label": "Visite", "category": "Musée, patrimoine, architecture, arts visuels"},
            {
                "id": "VISITE_GUIDEE",
                "label": "Visite guidée",
                "category": "Musée, patrimoine, architecture, arts visuels",
            },
            {
                "id": "EVENEMENT_PATRIMOINE",
                "label": "Événement et atelier patrimoine",
                "category": "Musée, patrimoine, architecture, arts visuels",
            },
            {
                "id": "ATELIER_PRATIQUE_ART",
                "label": "Atelier, stage de pratique artistique",
                "category": "Pratique artistique",
            },
            {"id": "SEANCE_ESSAI_PRATIQUE_ART", "label": "Séance d'essai", "category": "Pratique artistique"},
            {"id": "FESTIVAL_SPECTACLE", "label": "Festival", "category": "Spectacle vivant"},
            {"id": "SPECTACLE_REPRESENTATION", "label": "Spectacle, représentation", "category": "Spectacle vivant"},
        ]

    def test_list_sub_categories_user_auth_returns_401(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        response = client.with_session_auth(user_offerer.user.email).get("/v2/collective/subcategories")

        # Then
        assert response.status_code == 401

    def test_list_sub_categories_anonymous_returns_401(self, client):
        # Given

        # When
        response = client.get("/v2/collective/subcategories")

        # Then
        assert response.status_code == 401
