from unittest.mock import patch

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db

from tests.conftest import clean_database


class OffererViewTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_offerer_add_tags(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        offerer = offers_factories.OffererFactory()
        tag1 = offers_factories.OffererTagFactory(name="test_tag_1")
        tag2 = offers_factories.OffererTagFactory(name="test_tag_2")

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": "Updated offerer",
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                "tags": [tag1.id, tag2.id],  # Add both tags
            },
        )

        assert response.status_code == 302
        db.session.refresh(offerer)
        assert offerer.name == "Updated offerer"
        assert {tag.name for tag in offerer.tags} == {tag1.name, tag2.name}

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_edit_offerer_remove_tags(self, mocked_validate_csrf_token, client):
        users_factories.AdminFactory(email="admin@example.com")

        offerer = offers_factories.OffererFactory()
        offers_factories.OffererTagMappingFactory(offerer=offerer)
        offers_factories.OffererTagMappingFactory(offerer=offerer)

        api_client = client.with_session_auth("admin@example.com")

        response = api_client.post(
            f"/pc/back-office/offerer/edit/?id={offerer.id}",
            form={
                "name": "Updated offerer",
                "siren": offerer.siren,
                "city": offerer.city,
                "postalCode": offerer.postalCode,
                "address": offerer.address,
                "tags": [],  # Remove both tags
            },
        )

        assert response.status_code == 302
        db.session.refresh(offerer)
        assert offerer.name == "Updated offerer"
        assert len(offerer.tags) == 0
