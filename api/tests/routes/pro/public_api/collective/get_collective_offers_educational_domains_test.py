from operator import itemgetter

from flask import url_for
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetEducationalDomainsTest:
    def test_list_educational_domains(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        domain1 = educational_factories.EducationalDomainFactory(name="Arts numériques")
        domain2 = educational_factories.EducationalDomainFactory(name="Cinéma, audiovisuel")

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_educational_domains")
        )

        # Then
        assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        assert response_list == [
            {"id": domain1.id, "name": "Arts numériques"},
            {"id": domain2.id, "name": "Cinéma, audiovisuel"},
        ]

    def test_list_educational_domains_empty(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_educational_domains")
        )

        # Then
        assert response.status_code == 200
        assert response.json == []

    def test_list_educational_domains_user_auth_returns_401(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        response = client.with_session_auth(user_offerer.user.email).get(
            url_for("pro_public_api_v2.list_educational_domains")
        )

        # Then
        assert response.status_code == 401

    def test_list_educational_domains_anonymous_returns_401(self, client):
        # Given
        educational_factories.EducationalDomainFactory(name="Musique")

        # When
        response = client.get(url_for("pro_public_api_v2.list_educational_domains"))

        # Then
        assert response.status_code == 401
