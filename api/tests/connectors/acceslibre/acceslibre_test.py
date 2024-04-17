from unittest.mock import patch

from dateutil import parser
import pytest

from pcapi.connectors import acceslibre
from pcapi.connectors.acceslibre import AcceslibreActivity
from pcapi.connectors.acceslibre import AcceslibreWidgetData
from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.testing import override_settings
from pcapi.utils import requests

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
        acceslibre_infos = acceslibre.get_id_at_accessibility_provider(
            name=name, public_name=public_name, ban_id=ban_id
        )
        assert acceslibre_infos["slug"] == "le-livre-bateau"
        assert (
            acceslibre_infos["url"] == "https://acceslibre.beta.gouv.fr/app/59-lille/a/librairie/erp/le-livre-bateau/"
        )

    def test_venue_has_siret_at_provider(self, requests_mock):
        siret = "23456789012345"
        name = "La Librairie Chouette"
        public_name = None
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/?siret={siret}",
            json=fixtures.ACCESLIBRE_RESULTS,
        )
        acceslibre_infos = acceslibre.get_id_at_accessibility_provider(name=name, public_name=public_name, siret=siret)
        assert acceslibre_infos["slug"] == "la-librairie-chouette"
        assert (
            acceslibre_infos["url"]
            == "https://acceslibre.beta.gouv.fr/app/59-lille/a/librairie/erp/la-librairie-chouette/"
        )

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
        acceslibre_infos = acceslibre.get_id_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code, address=address
        )
        assert acceslibre_infos["slug"] == "belette-du-nord"
        assert (
            acceslibre_infos["url"] == "https://acceslibre.beta.gouv.fr/app/59-lille/a/librairie/erp/belette-du-nord/"
        )

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
        acceslibre_infos = acceslibre.get_id_at_accessibility_provider(
            name=name, public_name=public_name, city=city, postal_code=postal_code, address=address
        )
        assert acceslibre_infos["slug"] == "belette-du-nord"
        assert (
            acceslibre_infos["url"] == "https://acceslibre.beta.gouv.fr/app/59-lille/a/librairie/erp/belette-du-nord/"
        )

    def test_check_last_update(self, requests_mock):
        slug = "office-du-tourisme-4"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/{slug}/",
            json=fixtures.ACCESLIBRE_RESULTS_BY_SLUG,
        )
        last_update = acceslibre.get_last_update_at_provider(slug=slug)
        assert last_update == parser.isoparse("2023-04-13T15:10:25.612731+02:00")

    @patch("pcapi.connectors.acceslibre.AcceslibreBackend._fetch_request")
    def test_catch_connection_error(self, requests_mock):
        slug = "office-du-tourisme-4"
        requests_mock.side_effect = [requests.exceptions.ConnectionError]
        with pytest.raises(acceslibre.AccesLibreApiException) as exception:
            acceslibre.get_last_update_at_provider(slug=slug)
        assert (
            str(exception.value)
            == f"Error connecting AccesLibre API for https://acceslibre.beta.gouv.fr/api/erps/{slug}/ and query parameters: None"
        )

    def test_get_accessibility_infos(self):
        accesslibre_data_list = [
            {
                "title": "stationnement",
                "labels": ["Stationnement adapté dans l'établissement"],
            },
            {
                "title": "accès",
                "labels": ["Chemin d'accès de plain pied", "Entrée de plain pied"],
            },
            {
                "title": "personnel",
                "labels": ["Personnel sensibilisé / formé"],
            },
            {
                "title": "audiodescription",
                "labels": ["avec équipement occasionnel selon la programmation"],
            },
            {
                "title": "sanitaire",
                "labels": ["Sanitaire adapté"],
            },
        ]
        acceslibre_data = [
            AcceslibreWidgetData(title=str(item["title"]), labels=[str(label) for label in item["labels"]])
            for item in accesslibre_data_list
        ]
        accessibility_infos = acceslibre.acceslibre_to_accessibility_infos(acceslibre_data)

        assert accessibility_infos == acceslibre.AccessibilityInfo(
            access_modality=[acceslibre_enum.EXTERIOR_ONE_LEVEL, acceslibre_enum.ENTRANCE_ONE_LEVEL],
            audio_description=[acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL],
            deaf_and_hard_of_hearing_amenities=[],
            facilities=[acceslibre_enum.FACILITIES_ADAPTED],
            sound_beacon=[],
            trained_personnel=[acceslibre_enum.PERSONNEL_TRAINED],
            transport_modality=[acceslibre_enum.PARKING_ADAPTED],
        )

    def test_get_accessibility_infos_from_widget(self, requests_mock):
        slug = "mon-slug-acceslibre"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/{slug}/widget/",
            json=fixtures.ACCESLIBRE_WIDGET_RESULT,
        )
        accessibility_infos = acceslibre.get_accessibility_infos(slug)
        assert accessibility_infos.trained_personnel == [acceslibre_enum.PERSONNEL_TRAINED]
        assert accessibility_infos.access_modality == [
            acceslibre_enum.EXTERIOR_ONE_LEVEL,
            acceslibre_enum.ENTRANCE_RAMP,
        ]
        assert accessibility_infos.audio_description == [
            acceslibre_enum.AUDIODESCRIPTION_PERMANENT_SMARTPHONE,
            acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL,
        ]
        assert accessibility_infos.deaf_and_hard_of_hearing_amenities == [
            acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP,
            acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SIGN_LANGUAGE,
        ]

    def test_get_last_entries_by_activity(self, requests_mock):
        activity = AcceslibreActivity.BIBLIOTHEQUE
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?activite=bibliotheque-mediatheque&created_or_updated_in_last_days=7&page_size=50&page=1",
            json=fixtures.ACCESLIBRE_ACTIVITY_RESULT,
        )
        requests_mock.get(
            "https://acceslibre.beta.gouv.fr/api/erps/?activite=bibliotheque-mediatheque&created_or_updated_in_last_days=7&page_size=1",
            json=fixtures.ACCESLIBRE_ACTIVITY_RESULT,
        )

        activity_results = acceslibre.find_new_entries_by_activity(activity)
        assert activity_results
        matching_venue = acceslibre.match_venue_with_acceslibre(
            acceslibre_results=activity_results,
            venue_address="2 Place des Thermes",
            venue_name="Bibliothèque Municipale de Truchan-les-Bains",
        )
        assert (
            matching_venue.web_url
            == "https://acceslibre.info/app/11-tuchan/a/bibliotheque-mediatheque/erp/bibliotheque-municipale-de-truchan-les-bains/"
        )

    def test_should_raise_error_when_slug_is_none(self, requests_mock):
        name = "Le Livre Bateau"
        public_name = ""
        ban_id = "59350_5513_abcde"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/?ban_id={ban_id}",
            json=fixtures.ACCESLIBRE_BAD_SLUG,
        )
        with pytest.raises(acceslibre.AccesLibreApiException) as exception:
            acceslibre.get_id_at_accessibility_provider(name=name, public_name=public_name, ban_id=ban_id)
        assert str(exception.value) == "Acceslibre returned None for: slug"

    def test_should_raise_error_when_activity_is_not_a_dict(self, requests_mock):
        name = "Le Livre Bateau"
        public_name = ""
        ban_id = "59350_5513_abcde"
        requests_mock.get(
            f"https://acceslibre.beta.gouv.fr/api/erps/?ban_id={ban_id}",
            json=fixtures.ACCESLIBRE_BAD_ACTIVITY,
        )
        with pytest.raises(acceslibre.AccesLibreApiException) as exception:
            acceslibre.get_id_at_accessibility_provider(name=name, public_name=public_name, ban_id=ban_id)
        assert str(exception.value) == "Acceslibre activite should be a dict, but received: Chaîne de caracteres"
