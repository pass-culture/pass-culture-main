"""
A client for API Acceslibre.
Documentation of the API: https://acceslibre.beta.gouv.fr/api/docs/
Further explanations at: https://schema.data.gouv.fr/MTES-MCT/acceslibre-schema/0.0.14/documentation.html
"""

from datetime import datetime
import enum
import json
import logging
import uuid

from dateutil import parser
import pydantic.v1 as pydantic_v1
from rapidfuzz import fuzz

from pcapi import settings
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)

ACCESLIBRE_REQUEST_TIMEOUT = 3
REQUEST_PAGE_SIZE = 50
ADDRESS_MATCHING_RATIO = 80
NAME_MATCHING_RATIO = 45


class AcceslibreActivity(enum.Enum):
    """
    The following are Acceslibre activities that we can use in our matching algorithm
    """

    ADMINISTRATION_PUBLIQUE = "administration-publique"
    AQUARIUM = "aquarium"
    ART = "art"
    ARTISANAT = "artisanat"
    ASSOCIATION = "association"
    BIBLIOTHEQUE = "bibliotheque-mediatheque"
    CENTRE_CULTUREL = "centre-culturel"
    CHATEAU = "chateau"
    CINEMA = "cinema"
    COLLECTIVITE_TERRITORIALE = "collectivite-territoriale"
    CONSERVATOIRE_ET_ECOLE_DE_MUSIQUE = "conservatoire-et-ecole-de-musique"
    DISQUAIRE = "disquaire"
    ECOLE_DE_DANSE = "ecole-de-danse"
    ENCADREUR_ENLUMINEUR = "encadreur-enlumineur"
    EVENEMENT_CULTUREL = "evenement-culturel"
    GALERIE_D_ART = "salle-dexposition"
    GYMNASE = "gymnase"
    INSTRUMENT_ET_MATERIEL_DE_MUSIQUE = "instruments-et-materiel-de-musique"
    JARDIN_BOTANIQUE_ETOU_ZOOLOGIQUE = "jardin-botanique-etou-zoologique"
    LIBRAIRIE = "librairie"
    LIEU_DE_VISITE = "lieu-de-visite"
    LOISIRS_CREATIFS = "loisirs-creatifs"
    MENUISERIE = "menuiserie-ebenisterie"
    MONUMENT_HISTORIQUE = "monument-historique"
    MUSEE = "musee"
    MUSIQUE = "musique"
    OFFICE_DU_TOURISME = "office-du-tourisme"
    OPERA = "opera"
    PAPETERIE_PRESSE_JOURNAUX = "papeterie-presse-journaux"
    PARC_DES_EXPOSITIONS = "parc-des-expositions"
    SALLE_DE_CONCERT = "salle-de-concert"
    SALLE_DE_DANSE = "salle-de-danse"
    SALLE_DES_FETES = "salle-des-fetes"
    SALLE_DE_SPECTACLE = "salle-de-spectacle"
    THEATRE = "theatre"


class AccesLibreApiException(Exception):
    pass


class AccessibilityParsingException(Exception):
    pass


class AccessibilityInfo(pydantic_v1.BaseModel):
    access_modality: list[str] = pydantic_v1.Field(default_factory=list)
    audio_description: list[str] = pydantic_v1.Field(default_factory=list)
    deaf_and_hard_of_hearing_amenities: list[str] = pydantic_v1.Field(default_factory=list)
    facilities: list[str] = pydantic_v1.Field(default_factory=list)
    sound_beacon: list[str] = pydantic_v1.Field(default_factory=list)
    trained_personnal: list[str] = pydantic_v1.Field(default_factory=list)
    transport_modality: list[str] = pydantic_v1.Field(default_factory=list)

    @pydantic_v1.root_validator(pre=True)
    def set_default_to_empty_list(cls, values: dict) -> dict:
        for field_name, field_value in values.items():
            if field_value is None:
                values[field_name] = []
        return values


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.ACCESLIBRE_BACKEND)
    return backend_class()


def find_venue_at_accessibility_provider(
    name: str,
    public_name: str | None = None,
    siret: str | None = None,
    ban_id: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
    address: str | None = None,
) -> dict | None:
    """Try to find the entry at acceslibre that matches our venue
    Returns acceslibre venue
    """
    return _get_backend().find_venue_at_accessibility_provider(
        name=name,
        public_name=public_name,
        siret=siret,
        ban_id=ban_id,
        city=city,
        postal_code=postal_code,
        address=address,
    )


def get_id_at_accessibility_provider(
    name: str,
    public_name: str | None = None,
    siret: str | None = None,
    ban_id: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
    address: str | None = None,
) -> str | None:
    """
    Returns the slug (unique ID at acceslibre) of the venue at acceslibre
    """
    return _get_backend().get_id_at_accessibility_provider(
        name=name,
        public_name=public_name,
        siret=siret,
        ban_id=ban_id,
        city=city,
        postal_code=postal_code,
        address=address,
    )


def get_last_update_at_provider(slug: str) -> datetime:
    return _get_backend().get_last_update_at_provider(slug)


def get_accessibility_infos(slug: str) -> AccessibilityInfo:
    """Fetch accessibility data from acceslibre and save them in an AccessibilityInfo object
    This object will then be saved in db in the AccessibilityProvider.externalAccessibilityData JSONB
    """
    return _get_backend().get_accessibility_infos(slug=slug)


def extract_street_name(address: str | None = None, city: str | None = None, postal_code: str | None = None) -> str:
    if address and city and postal_code:
        return address.lower().replace(postal_code, "").replace(city.lower(), "").rstrip()
    return ""


def match_venue_with_acceslibre(
    acceslibre_results: list[dict],
    venue_name: str,
    venue_public_name: str | None,
    venue_address: str | None,
    venue_ban_id: str | None,
    venue_siret: str | None,
) -> dict[str, str] | None:
    """
    From the results we get from requesting acceslibre API, we try a match with our venue
    by comparing the name and address using a fuzzy matching algorithm.
    We also check that the activity of the venue at acceslibre is in the enum AcceslibreActivity
    """
    venue_name = venue_name.lower()
    venue_public_name = venue_public_name.lower() if venue_public_name else "PUBLIC_NAME_MISSING"
    venue_address = venue_address.lower() if venue_address else "ADDRESS_MISSING"

    for result in acceslibre_results:
        acceslibre_name = result["nom"].lower()
        acceslibre_address = extract_street_name(result["adresse"], result["commune"], result["code_postal"])
        acceslibre_activity = result["activite"]["slug"]
        acceslibre_ban_id = result["ban_id"]
        acceslibre_siret = result["siret"]
        # check siret matching
        if venue_siret and venue_siret == acceslibre_siret:
            return result
        if (  # pylint: disable=too-many-boolean-expressions
            # check activity is valid
            acceslibre_activity in [a.value for a in AcceslibreActivity]
            # name matching
            and (
                acceslibre_name in venue_name
                or venue_name in acceslibre_name
                or venue_public_name in acceslibre_name
                or acceslibre_name in venue_public_name
                or fuzz.ratio(acceslibre_name, venue_name) > NAME_MATCHING_RATIO
                or fuzz.ratio(acceslibre_name, venue_public_name) > NAME_MATCHING_RATIO
            )
            # check if BAN id or address matching
            and (
                (venue_ban_id and venue_ban_id == acceslibre_ban_id)
                or (
                    venue_address
                    and acceslibre_address
                    and fuzz.ratio(acceslibre_address, venue_address) > ADDRESS_MATCHING_RATIO
                )
            )
        ):
            return result
    return None


def acceslibre_to_accessibility_infos(response: dict) -> AccessibilityInfo:
    accessibility_infos = AccessibilityInfo()
    for section in response["sections"]:
        if section["title"] == "accès":
            accessibility_infos.access_modality = section["labels"]
        elif section["title"] == "audiodescription":
            accessibility_infos.audio_description = section["labels"]
        elif section["title"] == "équipements sourd et malentendant":
            accessibility_infos.deaf_and_hard_of_hearing_amenities = section["labels"]
        elif section["title"] == "sanitaire":
            accessibility_infos.facilities = section["labels"]
        elif section["title"] == "balise sonore":
            accessibility_infos.sound_beacon = section["labels"]
        elif section["title"] == "personnel":
            accessibility_infos.trained_personnal = section["labels"]
        elif section["title"] == "stationnement":
            accessibility_infos.transport_modality = section["labels"]
    return accessibility_infos


class BaseBackend:
    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> dict | None:
        raise NotImplementedError()

    def get_id_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> str | None:
        raise NotImplementedError()

    def get_last_update_at_provider(self, slug: str) -> datetime:
        raise NotImplementedError()

    def get_accessibility_infos(self, slug: str) -> AccessibilityInfo:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> dict | None:
        return {
            "slug": "mon-lieu-chez-acceslibre",
            "uuid": str(uuid.uuid4()),
            "nom": "Un lieu",
            "adresse": "3 Rue de Valois 75001 Paris",
            "activite": {"nom": "Bibliothèque Médiathèque", "slug": "bibliotheque-mediatheque"},
            "siret": "",
            "updated_at": "2023-04-13T15:10:25.612731+02:00",
        }

    def get_id_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> str | None:
        return "mon-lieu-chez-acceslibre"

    def get_last_update_at_provider(self, slug: str) -> datetime:
        return datetime(2024, 3, 1, 0, 0)

    def get_accessibility_infos(self, slug: str) -> AccessibilityInfo:
        return AccessibilityInfo(sound_beacon=["Balise sonore"])


class AcceslibreBackend(BaseBackend):
    def _send_request(
        self,
        query_params: dict[str, str],
    ) -> dict:
        api_key = settings.ACCESLIBRE_API_KEY
        url = settings.ACCESLIBRE_API_URL
        headers = {"Authorization": f"Api-Key {api_key}"}
        try:
            response = requests.get(url, headers=headers, params=query_params, timeout=ACCESLIBRE_REQUEST_TIMEOUT)
        except requests.exceptions.RequestException:
            raise AccesLibreApiException(
                f"Error connecting AccesLibre API for {url} and query parameters: {query_params}"
            )
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error(
                "Got non-JSON or malformed JSON response from AccesLibre",
                extra={"url": response.url, "response": response.content},
            )
            raise AccesLibreApiException(f"Non-JSON response from AccesLibre API for {response.url}")

    def _send_request_with_slug(
        self,
        slug: str,
        request_widget_infos: bool | None = False,
    ) -> dict:
        """
        Acceslibre has a specific GET route /api/erps/{slug} that
        we can requested when a venue slug is known. This slug is saved in the
        Venue.accessibilityProvider.externalAccessibilityId field on our side.
        """
        api_key = settings.ACCESLIBRE_API_KEY
        url = settings.ACCESLIBRE_API_URL + slug
        if request_widget_infos:
            url += "/widget"
        headers = {"Authorization": f"Api-Key {api_key}"}
        try:
            response = requests.get(url, headers=headers, timeout=ACCESLIBRE_REQUEST_TIMEOUT)
        except requests.exceptions.RequestException:
            raise AccesLibreApiException(f"Error connecting AccesLibre API for {url}")
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error(
                "Got non-JSON or malformed JSON response from AccesLibre",
                extra={"url": response.url, "response": response.content},
            )
            raise AccesLibreApiException(f"Non-JSON response from AccesLibre API for {response.url}")

    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> dict | None:
        search_criteria: list[dict] = [
            {"siret": siret},
            {"ban_id": ban_id},
            {
                "q": name,
                "commune": city,
                "code_postal": postal_code,
                "page_size": REQUEST_PAGE_SIZE,
            },
            {
                "q": public_name,
                "commune": city,
                "code_postal": postal_code,
                "page_size": REQUEST_PAGE_SIZE,
            },
        ]

        for criterion in search_criteria:
            if all(v is not None for v in criterion.values()):
                response = self._send_request(query_params=criterion)
                if response["count"] and (
                    matching_venue := match_venue_with_acceslibre(
                        acceslibre_results=response["results"],
                        venue_name=name,
                        venue_public_name=public_name,
                        venue_address=address,
                        venue_ban_id=ban_id,
                        venue_siret=siret,
                    )
                ):
                    return matching_venue
        return None

    def get_id_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> str | None:
        matching_venue = find_venue_at_accessibility_provider(
            name, public_name, siret, ban_id, city, postal_code, address
        )
        if matching_venue:
            return matching_venue["slug"]
        return None

    def get_last_update_at_provider(self, slug: str) -> datetime:
        response = self._send_request_with_slug(slug=slug)
        created_at = parser.isoparse(response["created_at"])
        updated_at = parser.isoparse(response["updated_at"])
        if updated_at > created_at:
            return updated_at
        return created_at

    def get_accessibility_infos(self, slug: str) -> AccessibilityInfo:
        accesslibre_data = self._send_request_with_slug(slug=slug, request_widget_infos=True)
        return acceslibre_to_accessibility_infos(accesslibre_data)
