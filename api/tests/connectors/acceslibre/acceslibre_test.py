from pcapi.connectors import acceslibre
from pcapi.core.testing import override_settings

from tests.connectors.acceslibre import fixtures


class AcceslibreTest:
    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_venue_known_banid(self, requests_mock):
        name = "Le Livre Bateau"
        public_name = ""
        ban_id = "59350_5513_abcde"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?ban_id=59350_5513_abcde",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        slug = acceslibre.find_venue_at_accessibility_provider(name=name, public_name=public_name, ban_id=ban_id)
        assert slug == "le-bateau-livre"

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_venue_has_siret_at_provider(self, requests_mock):
        siret = "23456789012345"
        name = "La Librairie Chouette"
        public_name = None
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?siret=23456789012345",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        slug = acceslibre.find_venue_at_accessibility_provider(name=name, public_name=public_name, siret=siret)
        assert slug == "la-librairie-chouette"

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_find_venue_based_on_name(self, requests_mock):
        name = "La Belette Du Nord"
        public_name = None
        city = "Lille"
        postal_code = "59800"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=La+Belette+Du+Nord&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_BY_NAME,
        )
        slug = acceslibre.find_venue_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code
        )
        assert slug == "belette-du-nord"

    @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
    def test_find_venue_based_on_public_name(self, requests_mock):
        name = "Un truc random qui échoue"
        public_name = "LA BELETTE DU NORD - LILLE"
        city = "Lille"
        postal_code = "59800"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=Un+truc+random+qui+%C3%A9choue&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_EMPTY,
        )
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=LA+BELETTE+DU+NORD+-+LILLE&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_BY_NAME,
        )
        slug = acceslibre.find_venue_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code
        )
        assert slug == "belette-du-nord"
