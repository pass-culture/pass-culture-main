from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import OffererTag
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories

from tests.conftest import clean_database


class OffererTagViewTest:
    @pytest.mark.parametrize("name", ["tag", "tag_with_underscores", "[tag]!", "tag_140ch_" * 14])
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_tag(self, mocked_validate_csrf_token, client, name):
        users_factories.AdminFactory(email="admin@example.com")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post("/pc/back-office/offerertag/new/", form={"name": name})

        assert response.status_code == 302
        assert OffererTag.query.count() == 1
        assert OffererTag.query.first().name == name

    @pytest.mark.parametrize(
        "name", ["tag ", " tag", "t ag", "tag\t", "\ttag", "ta\tg", "\ntag", "t\nag", "\rtag", "tag\r", "t\rag"]
    )
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_tag_with_whitespace(self, mocked_validate_csrf_token, client, name):
        users_factories.AdminFactory(email="admin@example.com")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post("/pc/back-office/offerertag/new/", form={"name": name})

        assert response.status_code == 200
        assert "Le nom ne doit contenir aucun caractère d&#39;espacement" in response.data.decode("utf8")
        assert OffererTag.query.count() == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_tag_too_long(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post("/pc/back-office/offerertag/new/", form={"name": "x" * 141})

        assert response.status_code == 200
        assert "Le nom ne peut excéder 140 caractères" in response.data.decode("utf8")
        assert OffererTag.query.count() == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_tag(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        offerer = offerers_factories.OffererFactory()
        tag = offers_factories.OffererTagFactory(name="test_delete_tag")
        offers_factories.OffererTagMappingFactory(offerer=offerer, tag=tag)

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post("/pc/back-office/offerertag/delete/", form={"id": tag.id})

        assert response.status_code == 302
        assert len(offerer.tags) == 0
