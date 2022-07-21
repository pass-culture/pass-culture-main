import logging

from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.exceptions import CulturalPartnerNotFoundException
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.routes.serialization import venues_serialize


logger = logging.getLogger(__name__)


class AdageLoggerClient(AdageClient):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation", data)
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)  # type: ignore [arg-type]

    def notify_offer_or_stock_edition(self, data: EducationalBookingEdition) -> AdageApiResult:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation-edit", data)
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        logger.info("Adage has been called at %s, with siren: %s", f"{self.base_url}/v1/partenaire-culturel", siren)

        if siren in ["950469494", "881457238", "851924100", "832321053"]:
            return [AdageVenue.parse_obj({"siret": "95046949400021"})]

        raise CulturalPartnerNotFoundException("Requested siren is not a known cultural partner for Adage")

    def notify_booking_cancellation_by_offerer(self, data: EducationalBookingResponse) -> AdageApiResult:
        logger.info(
            "Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation-annule", data
        )
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_cultural_partners(self) -> list[dict[str, str | int | float | None]]:
        logger.info("Adage has been called at %s", f"{self.base_url}/v1/partenaire-culturel")
        return [
            {
                "id": 1,
                "venueId": 12,
                "siret": 51234567900017,
                "regionId": 2,
                "academieId": "ac-versaille",
                "statutId": 2,
                "labelId": 3,
                "typeId": 1,
                "communeId": "Paris",
                "libelle": "a cultural partner",
                "adresse": "10 rue de la ville d'à coté",
                "siteWeb": 0,
                "latitude": 0,
                "longitude": 0,
                "statutLibelle": "Association",
                "labelLibelle": "pouet",
                "typeIcone": "image",
                "typeLibelle": "a type",
                "communeLibelle": "Paris",
                "communeDepartement": "Paris",
                "academieLibelle": "versaille",
                "regionLibelle": "ile de france",
                "domaines": "des domaines",
                "actif": 0,
                "dateModification": "2022-06-27T08:52:27.597Z",
                "synchroPass": 1,
            },
            {
                "id": 2,
                "venueId": 13,
                "siret": 65498732000011,
                "regionId": 3,
                "academieId": "un id d'academie",
                "statutId": 3,
                "labelId": 1,
                "typeId": 1,
                "communeId": "une comune",
                "libelle": "un libelle",
                "adresse": "1 impasse d'une ville lointaine",
                "siteWeb": 0,
                "latitude": 0,
                "longitude": 0,
                "statutLibelle": "entreprise privée",
                "labelLibelle": "sans label",
                "typeIcone": "film",
                "typeLibelle": "maison",
                "communeLibelle": "une commune libelle",
                "communeDepartement": "corse du sud",
                "academieLibelle": "Lille",
                "regionLibelle": "Corse",
                "domaines": "d'autres domaines",
                "actif": 0,
                "dateModification": "2022-06-27T08:52:27.597Z",
                "synchroPass": 1,
            },
        ]

    def notify_institution_association(self, data: AdageCollectiveOffer) -> AdageApiResult:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/offre-assoc", data)
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_cultural_partner(self, siret: str) -> venues_serialize.AdageCulturalPartner:
        logger.info("Adage has been called at %s", f"{self.base_url}/v1/etablissement-culturel/{siret}")
        if siret == "95046949400021":
            return venues_serialize.AdageCulturalPartner(
                id="128028",
                venueId=None,
                siret=siret,
                regionId=None,
                academieId=None,
                statutId=3,
                labelId=None,
                typeId="8",
                communeId="26324",
                libelle="Fête du livre jeunesse de St Paul les trois Châteaux",
                adresse="Place Charles Chausy",
                siteWeb="http://www.fetedulivrejeunesse.fr/",
                latitude="44.350457",
                longitude="4.765918",
                actif="1",
                dateModification="2021-09-01 00:00:00",
                statutLibelle="Association",
                labelLibelle=None,
                typeIcone="town",
                typeLibelle="Association ou fondation pour la promotion, le développement et la diffusion d\u0027oeuvres",
                communeLibelle="SAINT-PAUL-TROIS-CHATEAUX",
                communeDepartement="026",
                academieLibelle="GRENOBLE",
                regionLibelle="AUVERGNE-RHÔNE-ALPES",
                domaines="Univers du livre, de la lecture et des écritures",
                synchroPass=0,
            )
        raise CulturalPartnerNotFoundException("Requested cultural partner not found for Adage")
