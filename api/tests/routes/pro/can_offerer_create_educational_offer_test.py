from typing import Any
import unittest

import pytest
import requests_mock

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories


@override_settings(ADAGE_API_URL="https://adage-api-url")
@override_settings(ADAGE_API_KEY="adage-api-key")
@override_settings(ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient")
@pytest.mark.usefixtures("db_session")
class CanOffererCreateEducationalOfferTest:
    def test_offerer_can_create_educational_offer(self, client: Any) -> None:
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()

        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/partenaire-culturel/{offerer.siren}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                status_code=200,
                json=[
                    {
                        "id": "125334",
                        "siret": "18004623700012",
                        "regionId": "1",
                        "academieId": "25",
                        "statutId": "2",
                        "labelId": "4",
                        "typeId": "4",
                        "communeId": "75101",
                        "libelle": "Musée du Louvre",
                        "adresse": "Rue de Rivoli",
                        "siteWeb": "https://www.louvre.fr/",
                        "latitude": "48.861863",
                        "longitude": "2.338081",
                        "actif": "1",
                        "dateModification": "2021-09-01 00:00:00",
                        "statutLibelle": "Établissement public",
                        "labelLibelle": "Musée de France",
                        "typeIcone": "museum",
                        "typeLibelle": "Musée, domaine ou monument",
                        "communeLibelle": "PARIS  1ER ARRONDISSEMENT",
                        "domaines": "Architecture|Arts visuels, arts plastiques, arts appliqués|Patrimoine et archéologie|Photographie",
                    }
                ],
            )

            response = client.with_session_auth(pro.email).get(f"/offerers/{offerer.id}/eac-eligibility")

        assert response.status_code == 200

    def test_offerer_can_create_educational_offer_already_known(self, client: Any) -> None:
        venue = offerers_factories.VenueFactory(adageId="pouet")
        pro = users_factories.ProFactory()

        with unittest.mock.patch("pcapi.core.educational.adage_backends") as adage_client:
            response = client.with_session_auth(pro.email).get(f"/offerers/{venue.managingOffererId}/eac-eligibility")
            adage_client.assert_not_called()

        assert response.status_code == 200

    def test_offerer_cannot_create_educational_offer_because_not_in_adage(self, client: Any) -> None:
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()

        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/partenaire-culturel/{offerer.siren}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                status_code=404,
            )

            response = client.with_session_auth(pro.email).get(f"/offerers/{offerer.id}/eac-eligibility")

        assert response.status_code == 200
        assert response.json == {"canCreate": False}

    def test_offerer_cannot_create_educational_offer_because_adage_failed(self, client: Any) -> None:
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()

        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/partenaire-culturel/{offerer.siren}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                status_code=500,
            )

            response = client.with_session_auth(pro.email).get(f"/offerers/{offerer.id}/eac-eligibility")

        assert response.status_code == 500
        assert response.json == {"adage_api": "error"}
