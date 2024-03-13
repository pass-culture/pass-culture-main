from dateutil import parser

from pcapi.connectors import acceslibre
from pcapi.core.testing import override_settings

from tests.connectors.acceslibre import fixtures


@override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
class AcceslibreTest:
    def test_venue_known_banid(self, requests_mock):
        name = "Le Livre Bateau"
        public_name = ""
        ban_id = "59350_5513_abcde"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/?ban_id={ban_id}",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        slug = acceslibre.get_id_at_accessibility_provider(name=name, public_name=public_name, ban_id=ban_id)
        assert slug == "le-bateau-livre"

    def test_venue_has_siret_at_provider(self, requests_mock):
        siret = "23456789012345"
        name = "La Librairie Chouette"
        public_name = None
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/?siret={siret}",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        slug = acceslibre.get_id_at_accessibility_provider(name=name, public_name=public_name, siret=siret)
        assert slug == "la-librairie-chouette"

    def test_find_venue_based_on_name_and_address(self, requests_mock):
        name = "La Belette Du Nord"
        public_name = None
        city = "Lille"
        postal_code = "59800"
        address = "30 Fausse rue"
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=La+Belette+Du+Nord&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_BY_NAME,
        )
        slug = acceslibre.get_id_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code, address=address
        )
        assert slug == "belette-du-nord"

    def test_find_venue_based_on_public_name_and_address(self, requests_mock):
        name = "Un truc random qui échoue"
        public_name = "LA BELETTE DU NORD - LILLE"
        city = "Lille"
        postal_code = "59800"
        address = "28 Fausse rue"  # wrong address on purpose
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=Un+truc+random+qui+%C3%A9choue&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_EMPTY,
        )
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?q=LA+BELETTE+DU+NORD+-+LILLE&commune=Lille&code_postal=59800&page_size=50",
            json=fixtures.ACCESLIBRE_RESULTS_BY_NAME,
        )
        slug = acceslibre.get_id_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code, address=address
        )
        assert slug == "belette-du-nord"

    def test_check_last_update(self, requests_mock):
        slug = "0850bc16-b240-47dc-93b6-efc7d8de2037"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/{slug}",
            json=fixtures.ACCESLIBRE_RESULTS_BY_SLUG,
        )
        last_update = acceslibre.get_last_update_at_provider(slug=slug)
        assert last_update == parser.isoparse("2023-04-13T15:10:25.612731+02:00")

    def test_get_accessibility_infos_from_widget(self, requests_mock):
        slug = "mon-super-slug"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/{slug}/widget",
            json=fixtures.ACCESLIBRE_WIDGET_RESULT,
        )
        accessibility_infos = acceslibre.get_accessibility_infos(slug)
        assert accessibility_infos.trained_personnal == ["Personnel sensibilisé / formé"]
        assert accessibility_infos.access_modality == ["Chemin d'accès de plain pied", "Entrée de plain pied"]
