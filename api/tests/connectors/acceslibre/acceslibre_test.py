from pcapi.connectors import acceslibre
from pcapi.core.testing import override_settings

from tests.connectors.acceslibre import fixtures


class AcceslibreTest:
    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_venue_known_banid(self, requests_mock):
        name = "Le Bateau Livre"
        public_name = ""
        ban_id = "59350_5513_00154"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?ban_id=59350_5513_00154",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        uuid = acceslibre.find_venue_at_accessibility_provider(name=name, public_name=public_name, ban_id=ban_id)
        assert uuid == "5cfa5da3-5dac-494d-9061-6a0665072d18"

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_venue_has_siret_at_provider(self, requests_mock):
        siret = "84009386800015"
        name = "La Chouette Librairie"
        public_name = None
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?siret=84009386800015",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        uuid = acceslibre.find_venue_at_accessibility_provider(name=name, public_name=public_name, siret=siret)
        assert uuid == "3b35474c-9211-4afa-b3b0-85a7d7392d60"

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_find_venue_based_on_name(self, requests_mock):
        name = "Le Furet Du Nord"
        public_name = None
        city = "Lille"
        postal_code = "59800"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=Le+Furet+Du+Nord&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_BY_NAME,
        )
        uuid = acceslibre.find_venue_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code
        )
        assert uuid == "4e0c4078-0441-4118-9401-676fb733e307"

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_find_venue_based_on_public_name(self, requests_mock):
        name = "Un truc random qui échoue"
        public_name = "LE FURET DU NORD - LILLE"
        city = "Lille"
        postal_code = "59800"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=Un+truc+random+qui+%C3%A9choue&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_EMPTY,
        )
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=LE+FURET+DU+NORD+-+LILLE&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_BY_NAME,
        )
        uuid = acceslibre.find_venue_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code
        )
        assert uuid == "4e0c4078-0441-4118-9401-676fb733e307"
