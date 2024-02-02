from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.core.offerers import factories as offerers_factories
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


class CheckOffererIsActiveTest:
    def test_active_offerer(self, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    @patch("pcapi.connectors.sirene.get_siren")
    def test_tag_inactive_offerer(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        mock_get_siren.return_value = sirene.SirenInfo(
            siren=offerer.siren,
            name=offerer.name,
            head_office_siret=offerer.siren + "00001",
            ape_code="6201Z",
            legal_category_code="1000",
            address=None,
            active=False,
            diffusible=True,
        )

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.tags == [siren_caduc_tag]

    @patch("pcapi.connectors.sirene.get_siren")
    def test_do_not_tag_inactive_offerer(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        mock_get_siren.return_value = sirene.SirenInfo(
            siren=offerer.siren,
            name=offerer.name,
            head_office_siret=offerer.siren + "00001",
            ape_code="6201Z",
            legal_category_code="1000",
            address=None,
            active=False,
            diffusible=True,
        )

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    @patch("pcapi.connectors.sirene.get_siren", side_effect=sirene.UnknownEntityException())
    def test_siren_not_found(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags
