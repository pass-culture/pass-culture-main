"""
A client for API Acceslibre.
Documentation of the API: https://acceslibre.beta.gouv.fr/api/docs/
Further explanations at: https://schema.data.gouv.fr/MTES-MCT/acceslibre-schema/0.0.14/documentation.html
"""

from datetime import datetime
import enum
import json
import logging
from math import ceil
import time
from typing import Any
from typing import TypedDict

from dateutil import parser
import pydantic.v1 as pydantic_v1
from rapidfuzz import fuzz

from pcapi import settings
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)

ACCESLIBRE_REQUEST_TIMEOUT = 6
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


class ExpectedFieldsEnum(enum.Enum):
    UNKNOWN = "Non renseigné"
    PARKING_ADAPTED = "Stationnement adapté dans l'établissement"
    PARKING_NEARBY = "Stationnement adapté à proximité"
    PARKING_UNAVAILABLE = "Pas de stationnement adapté à proximité"
    EXTERIOR_ONE_LEVEL = "Chemin d'accès de plain pied"
    EXTERIOR_ACCESS_RAMP = "Chemin rendu accessible (rampe)"
    EXTERIOR_ACCESS_ELEVATOR = "Chemin rendu accessible (ascenseur)"
    EXTERIOR_ACCESS_HAS_DIFFICULTIES = "Difficulté sur le chemin d'accès"
    ENTRANCE_ONE_LEVEL = "Entrée de plain pied"
    ENTRANCE_ONE_LEVEL_NARROW = "Entrée de plain pied mais étroite"
    ENTRANCE_NOT_ONE_LEVEL = "L'entrée n'est pas de plain-pied"
    ENTRANCE_HUMAN_HELP = "L'entrée n'est pas de plain-pied\n Aide humaine possible"
    ENTRANCE_ELEVATOR = "Accès à l'entrée par ascenseur"
    ENTRANCE_ELEVATOR_NARROW = "Entrée rendue accessible par ascenseur mais étroite"
    ENTRANCE_RAMP = "Accès à l'entrée par une rampe"
    ENTRANCE_RAMP_NARROW = "Entrée rendue accessible par rampe mais étroite"
    ENTRANCE_PRM = "Entrée spécifique PMR"
    PERSONNEL_MISSING = "Aucun personnel"
    PERSONNEL_UNTRAINED = "Personnel non formé"
    PERSONNEL_TRAINED = "Personnel sensibilisé / formé"
    SOUND_BEACON = "Balise sonore"
    DEAF_AND_HARD_OF_HEARING_FIXED_INDUCTION_LOOP = "boucle à induction magnétique fixe"
    DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP = "boucle à induction magnétique portative"
    DEAF_AND_HARD_OF_HEARING_SIGN_LANGUAGE = "langue des signes française (LSF)"
    DEAF_AND_HARD_OF_HEARING_CUED_SPEECH = "langue française parlée complétée (LFPC)"
    DEAF_AND_HARD_OF_HEARING_SUBTITLE = "sous-titrage ou transcription simultanée"
    DEAF_AND_HARD_OF_HEARING_OTHER = "autres"
    FACILITIES_ADAPTED = "Sanitaire adapté"
    FACILITIES_UNADAPTED = "Sanitaire non adapté"
    AUDIODESCRIPTION_PERMANENT = "avec équipement permanent, casques et boîtiers disponibles à l’accueil"
    AUDIODESCRIPTION_PERMANENT_SMARTPHONE = (
        "avec équipement permanent nécessitant le téléchargement d'une application sur smartphone"
    )
    AUDIODESCRIPTION_OCCASIONAL = "avec équipement occasionnel selon la programmation"
    AUDIODESCRIPTION_NO_DEVICE = "sans équipement, audiodescription audible par toute la salle (selon la programmation)"

    @classmethod
    def find_enum_from_string(cls, input_string: str) -> list:
        """
        Acceslibre may return a combinaison of several fields, comma separated
        """
        # FIXME: ogeber 03.04.2024 I've ask acceslibre to return fields in a list instead of a comma separated string
        # When done, we can delete this method and use `if label not in [item.value for item in ExpectedFieldsEnum]` instead
        enum_list: list[ExpectedFieldsEnum] = []
        for enum_option in cls:
            if enum_option.value in input_string:
                enum_list.append(enum_option)
        # Reorder enum_list according to its order in the input_string
        enum_indexes = {
            enum_option: input_string.index(enum_option.value)
            for enum_option in enum_list
            if enum_option.value in input_string
        }
        sorted_enum_list = sorted(enum_list, key=lambda x: enum_indexes[x])
        return sorted_enum_list


class AccesLibreApiException(Exception):
    pass


class AccessibilityInfo(pydantic_v1.BaseModel):
    access_modality: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)
    audio_description: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)
    deaf_and_hard_of_hearing_amenities: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)
    facilities: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)
    sound_beacon: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)
    trained_personnel: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)
    transport_modality: list[ExpectedFieldsEnum] = pydantic_v1.Field(default_factory=list)

    @pydantic_v1.root_validator(pre=True)
    def set_default_to_empty_list(cls, values: dict) -> dict:
        for field_name, field_value in values.items():
            if field_value is None:
                values[field_name] = []
        return values


class AcceslibreInfos(TypedDict):
    slug: str
    url: str


class AcceslibreResult(pydantic_v1.BaseModel):
    activite: dict[str, str]
    nom: str
    slug: str
    web_url: str
    adresse: str | None
    commune: str | None
    code_postal: str | None
    ban_id: str | None
    siret: str | None

    @pydantic_v1.validator("activite", pre=True)
    def activite_must_be_dict(cls, value: dict) -> dict:
        if not isinstance(value, dict):
            raise AccesLibreApiException(f"Acceslibre activite should be a dict, but received: {value}")
        return value

    @pydantic_v1.validator("nom", "slug", "web_url", pre=True)
    def non_empty_string(cls, value: str, field: Any) -> str:
        if value is None or not isinstance(value, str):
            raise AccesLibreApiException(f"Acceslibre returned None for: {field.name}")
        return value


class AcceslibreWidgetData(TypedDict):
    title: str
    labels: list[str]


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
) -> AcceslibreResult | None:
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


def find_new_entries_by_activity(
    activity: AcceslibreActivity, n_days_to_fetch: int = 7
) -> list[AcceslibreResult] | None:
    """
    Requests acceslibre for last week new entries for a given activity
    """
    return _get_backend().find_new_entries_by_activity(activity=activity, n_days_to_fetch=n_days_to_fetch)


def id_exists_at_acceslibre(slug: str) -> bool:
    """This method requests acceslibre for a given slug, and returns True if this
    slug exists on their side."""
    return _get_backend().id_exists_at_acceslibre(slug=slug)


def get_id_at_accessibility_provider(
    name: str,
    public_name: str | None = None,
    siret: str | None = None,
    ban_id: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
    address: str | None = None,
) -> AcceslibreInfos | None:
    """
    Returns the slug (unique ID at acceslibre) of the venue at acceslibre and its web url
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


def get_accessibility_infos(slug: str) -> tuple[datetime | None, AccessibilityInfo | None]:
    """Fetch last update and accessibility data from acceslibre and save them in an AccessibilityInfo object
    This object will then be saved in db in the AccessibilityProvider.LastUpdateAtProvider and
    AccessibilityProvider.externalAccessibilityData JSONB
    """
    return _get_backend().get_accessibility_infos(slug=slug)


def extract_street_name(address: str | None = None, city: str | None = None, postal_code: str | None = None) -> str:
    if address and city and postal_code:
        return address.lower().replace(postal_code, "").replace(city.lower(), "").rstrip()
    return ""


def address_match(
    acceslibre_address: str | None = None,
    acceslibre_city: str | None = None,
    acceslibre_postal_code: str | None = None,
    acceslibre_ban_id: str | None = None,
    venue_address: str | None = None,
    venue_city: str | None = None,
    venue_postal_code: str | None = None,
    venue_ban_id: str | None = None,
) -> bool:
    if venue_ban_id and venue_ban_id == acceslibre_ban_id:
        return True
    # If cities / postal codes are given, they must match.
    if (venue_city and venue_city != acceslibre_city) or (
        venue_postal_code and venue_postal_code != acceslibre_postal_code
    ):
        return False
    return bool(
        venue_address and acceslibre_address and fuzz.ratio(acceslibre_address, venue_address) > ADDRESS_MATCHING_RATIO
    )


def name_match(acceslibre_name: str, venue_name: str, venue_public_name: str) -> bool:
    return bool(
        acceslibre_name in venue_name
        or venue_name in acceslibre_name
        or venue_public_name in acceslibre_name
        or acceslibre_name in venue_public_name
        or fuzz.ratio(acceslibre_name, venue_name) > NAME_MATCHING_RATIO
        or fuzz.ratio(acceslibre_name, venue_public_name) > NAME_MATCHING_RATIO
    )


def match_venue_with_acceslibre(
    acceslibre_results: list[AcceslibreResult],
    venue_name: str,
    venue_public_name: str | None = None,
    venue_address: str | None = None,
    venue_city: str | None = None,
    venue_postal_code: str | None = None,
    venue_ban_id: str | None = None,
    venue_siret: str | None = None,
) -> AcceslibreResult | None:
    """
    From the results we get from requesting acceslibre API, we try a match with our venue
    by comparing the name and address using a fuzzy matching algorithm.
    We also check that the activity of the venue at acceslibre is in the enum AcceslibreActivity
    """
    venue_name = venue_name.lower()
    venue_public_name = venue_public_name.lower() if venue_public_name else "PUBLIC_NAME_MISSING"
    venue_address = venue_address.lower() if venue_address else "ADDRESS_MISSING"

    for result in acceslibre_results:
        acceslibre_name = result.nom.lower()
        acceslibre_address = extract_street_name(result.adresse, result.commune, result.code_postal)
        acceslibre_city = result.commune
        acceslibre_postal_code = result.code_postal
        acceslibre_activity = result.activite["slug"]
        acceslibre_ban_id = result.ban_id
        acceslibre_siret = result.siret
        if venue_siret and venue_siret == acceslibre_siret:
            return result
        if (
            acceslibre_activity in [a.value for a in AcceslibreActivity]
            and name_match(acceslibre_name, venue_name, venue_public_name)
            and (
                address_match(
                    acceslibre_address=acceslibre_address,
                    acceslibre_city=acceslibre_city,
                    acceslibre_postal_code=acceslibre_postal_code,
                    acceslibre_ban_id=acceslibre_ban_id,
                    venue_address=venue_address,
                    venue_city=venue_city,
                    venue_postal_code=venue_postal_code,
                    venue_ban_id=venue_ban_id,
                )
            )
        ):
            return result
    return None


def acceslibre_to_accessibility_infos(acceslibre_data: list[AcceslibreWidgetData]) -> AccessibilityInfo:
    accessibility_infos = AccessibilityInfo()
    acceslibre_mapping = {
        "accès": "access_modality",
        "audiodescription": "audio_description",
        "équipements sourd et malentendant": "deaf_and_hard_of_hearing_amenities",
        "sanitaire": "facilities",
        "balise sonore": "sound_beacon",
        "personnel": "trained_personnel",
        "stationnement": "transport_modality",
    }

    for section in acceslibre_data:
        try:
            title = section["title"]
            labels = section["labels"]
        except KeyError:
            raise AccesLibreApiException(
                "'title' or 'labels' key is missing in one of the sections. Check API response or contact Acceslibre"
            )
        attribute_name = acceslibre_mapping.get(title)
        if not attribute_name:
            continue
        labels_enum = []
        for label in labels:
            if label not in [item.value for item in ExpectedFieldsEnum]:
                # If this exception is raised, you should probably set the ExpectedFieldsEnum for the given label
                # according to acceslibre API schema, at https://github.com/MTES-MCT/acceslibre/blob/master/erp/views.py
                raise AccesLibreApiException(f"Acceslibre API returned an unexpected value: {label} for {title}")
            labels_enum.append(ExpectedFieldsEnum(label))
        setattr(accessibility_infos, attribute_name, labels_enum)
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
    ) -> AcceslibreResult | None:
        raise NotImplementedError()

    def find_new_entries_by_activity(
        self, activity: AcceslibreActivity, n_days_to_fetch: int
    ) -> list[AcceslibreResult] | None:
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
    ) -> AcceslibreInfos | None:
        raise NotImplementedError()

    def get_accessibility_infos(self, slug: str) -> tuple[datetime | None, AccessibilityInfo | None]:
        raise NotImplementedError()

    def id_exists_at_acceslibre(self, slug: str) -> bool:
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
    ) -> AcceslibreResult | None:
        return AcceslibreResult(
            slug="mon-lieu-chez-acceslibre",
            web_url="https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/",
            nom="Un lieu",
            adresse="3 Rue de Valois 75001 Paris",
            code_postal="75001",
            commune="Paris",
            ban_id="75001_1234_abcde",
            activite={"nom": "Bibliothèque Médiathèque", "slug": "bibliotheque-mediatheque"},
            siret="",
        )

    def find_new_entries_by_activity(
        self, activity: AcceslibreActivity, n_days_to_fetch: int
    ) -> list[AcceslibreResult] | None:
        return [
            AcceslibreResult(
                slug="mon-lieu-chez-acceslibre",
                web_url="https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/",
                nom="Un lieu",
                adresse="3 Rue de Valois 75001 Paris",
                code_postal="75001",
                commune="Paris",
                ban_id="75001_1234_abcde",
                activite={"nom": "Bibliothèque Médiathèque", "slug": "bibliotheque-mediatheque"},
                siret="",
            )
        ]

    def get_id_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> AcceslibreInfos | None:
        return AcceslibreInfos(
            slug="mon-lieu-chez-acceslibre",
            url="https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/",
        )

    def get_accessibility_infos(self, slug: str) -> tuple[datetime | None, AccessibilityInfo | None]:
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
        last_update = datetime(2024, 3, 1, 0, 0)
        return last_update, acceslibre_to_accessibility_infos(acceslibre_data)

    def id_exists_at_acceslibre(self, slug: str) -> bool:
        return True


class AcceslibreBackend(BaseBackend):
    @staticmethod
    def _build_url(slug: str | None = None, request_widget_infos: bool | None = False) -> str:
        base_url = settings.ACCESLIBRE_API_URL
        if slug:
            return base_url + slug + "/widget/" if request_widget_infos else base_url + slug + "/"
        return base_url

    @staticmethod
    def _fetch_request(
        url: str, headers: dict | None = None, params: dict[str, str | int] | None = None
    ) -> requests.Response:
        return requests.get(url, headers=headers, params=params, timeout=ACCESLIBRE_REQUEST_TIMEOUT)

    def _send_request(
        self,
        query_params: dict[str, str | int] | None = None,
        slug: str | None = None,
        request_widget_infos: bool | None = False,
    ) -> dict | None:
        """
        Acceslibre has a specific GET route /api/erps/{slug} that
        we can requested when a venue slug is known. This slug is saved in the
        Venue.accessibilityProvider.externalAccessibilityId field on our side.
        """
        api_key = settings.ACCESLIBRE_API_KEY
        url = self._build_url(slug=slug, request_widget_infos=request_widget_infos)
        headers = {"Authorization": f"Api-Key {api_key}"}
        try:
            response = self._fetch_request(url, headers, query_params)
        except requests.exceptions.RequestException:
            raise AccesLibreApiException(
                f"Error connecting AccesLibre API for {url} and query parameters: {query_params}"
            )
        if settings.ACCESLIBRE_SHOULD_AVOID_TOO_MANY_REQUESTS:
            time.sleep(0.3)  # request limit on acceslibre side is 3 per seconds
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(
                    "Got non-JSON or malformed JSON response from AccesLibre",
                    extra={"url": response.url, "response": response.content},
                )
                raise AccesLibreApiException(f"Non-JSON response from AccesLibre API for {response.url}")
        return None

    def find_venue_at_accessibility_provider(
        self,
        name: str,
        public_name: str | None = None,
        siret: str | None = None,
        ban_id: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        address: str | None = None,
    ) -> AcceslibreResult | None:
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
                if response and response.get("count"):
                    results = [
                        AcceslibreResult(
                            activite=item["activite"],
                            nom=item["nom"],
                            adresse=item["adresse"],
                            commune=item["commune"],
                            code_postal=item["code_postal"],
                            ban_id=item["ban_id"],
                            siret=item["siret"],
                            slug=item["slug"],
                            web_url=item["web_url"],
                        )
                        for item in response["results"]
                    ]
                    if matching_venue := match_venue_with_acceslibre(
                        acceslibre_results=results,
                        venue_name=name,
                        venue_public_name=public_name,
                        venue_address=address,
                        venue_ban_id=ban_id,
                        venue_siret=siret,
                    ):
                        return matching_venue
        return None

    def find_new_entries_by_activity(
        self, activity: AcceslibreActivity, n_days_to_fetch: int
    ) -> list[AcceslibreResult] | None:
        query_params = {
            "activite": activity.value,
            "created_or_updated_in_last_days": n_days_to_fetch,
            "page_size": 1,
        }
        response = self._send_request(query_params=query_params)
        if response and (new_entries_count := response.get("count")):
            num_pages = ceil(new_entries_count / REQUEST_PAGE_SIZE)
            activity_results: list[AcceslibreResult] = []
            for i in range(num_pages):
                query_params = {
                    "activite": activity.value,
                    "created_or_updated_in_last_days": n_days_to_fetch,
                    "page_size": REQUEST_PAGE_SIZE,
                    "page": i + 1,
                }
                new_entries = self._send_request(query_params=query_params)
                try:
                    if new_entries and new_entries.get("count"):
                        activity_results.extend(
                            [
                                AcceslibreResult(
                                    activite=item["activite"],
                                    nom=item["nom"],
                                    adresse=item["adresse"],
                                    commune=item["commune"],
                                    code_postal=item["code_postal"],
                                    ban_id=item["ban_id"],
                                    siret=item["siret"],
                                    slug=item["slug"],
                                    web_url=item["web_url"],
                                )
                                for item in new_entries["results"]
                            ]
                        )
                except:
                    raise AccesLibreApiException("Could not find required informations")
            return activity_results
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
    ) -> AcceslibreInfos | None:
        matching_venue = find_venue_at_accessibility_provider(
            name, public_name, siret, ban_id, city, postal_code, address
        )
        if matching_venue:
            return AcceslibreInfos(slug=matching_venue.slug, url=matching_venue.web_url)
        return None

    def get_accessibility_infos(self, slug: str) -> tuple[datetime | None, AccessibilityInfo | None]:
        if response := self._send_request(slug=slug, request_widget_infos=True):
            try:
                response_list = response["sections"]
            except KeyError:
                raise AccesLibreApiException(
                    "'sections' key is missing in the response from acceslibre. Check API response or contact Acceslibre"
                )
            created_at = parser.isoparse(response["created_at"])
            updated_at = parser.isoparse(response["updated_at"])
            last_update = updated_at if updated_at > created_at else created_at

            acceslibre_data = [
                AcceslibreWidgetData(
                    title=str(item["title"]),
                    labels=[str(label) for label in item["labels"]],
                )
                for item in response_list
            ]
            accessibility_infos = acceslibre_to_accessibility_infos(acceslibre_data)
            return (last_update, accessibility_infos)
        return (None, None)

    def id_exists_at_acceslibre(self, slug: str) -> bool:
        response = self._send_request(slug=slug)
        return bool(response and response.get("slug"))
