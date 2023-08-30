import pytest

import pcapi.core.offerers.factories as offerers_factories



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
            {"id": "CINE_PLEIN_AIR", "label": "Cinéma plein air", "category": "Cinéma", "categoryId": "CINEMA"},
            {"id": "FESTIVAL_CINE", "label": "Festival de cinéma", "category": "Cinéma", "categoryId": "CINEMA"},
            {"id": "SEANCE_CINE", "label": "Séance de cinéma", "category": "Cinéma", "categoryId": "CINEMA"},
            {
                "id": "EVENEMENT_CINE",
                "label": "Évènement cinématographique",
                "category": "Cinéma",
                "categoryId": "CINEMA",
            },
            {
                "id": "CONFERENCE",
                "label": "Conférence",
                "category": "Conférences, rencontres",
                "categoryId": "CONFERENCE",
            },
            {
                "id": "RENCONTRE",
                "label": "Rencontre",
                "category": "Conférences, rencontres",
                "categoryId": "CONFERENCE",
            },
            {
                "id": "RENCONTRE_EN_LIGNE",
                "label": "Rencontre en ligne",
                "category": "Conférences, rencontres",
                "categoryId": "CONFERENCE",
            },
            {
                "id": "SALON",
                "label": "Salon, Convention",
                "category": "Conférences, rencontres",
                "categoryId": "CONFERENCE",
            },
            {"id": "CONCOURS", "label": "Concours - jeux", "category": "Jeux", "categoryId": "JEU"},
            {"id": "RENCONTRE_JEU", "label": "Rencontres - jeux", "category": "Jeux", "categoryId": "JEU"},
            {"id": "EVENEMENT_JEU", "label": "Évènements - jeux", "category": "Jeux", "categoryId": "JEU"},
            {
                "id": "EVENEMENT_MUSIQUE",
                "label": "Autre type d'évènement musical",
                "category": "Musique live",
                "categoryId": "MUSIQUE_LIVE",
            },
            {"id": "CONCERT", "label": "Concert", "category": "Musique live", "categoryId": "MUSIQUE_LIVE"},
            {
                "id": "FESTIVAL_MUSIQUE",
                "label": "Festival de musique",
                "category": "Musique live",
                "categoryId": "MUSIQUE_LIVE",
            },
            {
                "id": "FESTIVAL_ART_VISUEL",
                "label": "Festival d'arts visuels / arts numériques",
                "category": "Musée, patrimoine, architecture, arts visuels",
                "categoryId": "MUSEE",
            },
            {
                "id": "VISITE",
                "label": "Visite",
                "category": "Musée, patrimoine, architecture, arts visuels",
                "categoryId": "MUSEE",
            },
            {
                "id": "VISITE_GUIDEE",
                "label": "Visite guidée",
                "category": "Musée, patrimoine, architecture, arts visuels",
                "categoryId": "MUSEE",
            },
            {
                "id": "EVENEMENT_PATRIMOINE",
                "label": "Évènement et atelier patrimoine",
                "category": "Musée, patrimoine, architecture, arts visuels",
                "categoryId": "MUSEE",
            },
            {
                "id": "ATELIER_PRATIQUE_ART",
                "label": "Atelier, stage de pratique artistique",
                "category": "Pratique artistique",
                "categoryId": "PRATIQUE_ART",
            },
            {
                "id": "SEANCE_ESSAI_PRATIQUE_ART",
                "label": "Séance d'essai",
                "category": "Pratique artistique",
                "categoryId": "PRATIQUE_ART",
            },
            {
                "id": "FESTIVAL_SPECTACLE",
                "label": "Festival de spectacle vivant",
                "category": "Spectacle vivant",
                "categoryId": "SPECTACLE",
            },
            {
                "id": "SPECTACLE_REPRESENTATION",
                "label": "Spectacle, représentation",
                "category": "Spectacle vivant",
                "categoryId": "SPECTACLE",
            },
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
