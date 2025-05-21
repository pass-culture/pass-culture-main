import datetime
import decimal
import logging

from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational import exceptions
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.serialization.educational.adage import shared as adage_serialize


logger = logging.getLogger(__name__)


class AdageLoggerClient(AdageClient):
    def notify_prebooking(self, data: adage_serialize.EducationalBookingResponse) -> None:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation", data)

    def notify_offer_or_stock_edition(self, data: adage_serialize.EducationalBookingEdition) -> None:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation-edit", data)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        logger.info("Adage has been called at %s, with siren: %s", f"{self.base_url}/v1/partenaire-culturel", siren)

        if siren in ["123456782", "881457238", "851924100", "832321053"]:
            return [AdageVenue.parse_obj({"siret": "12345678200010"})]

        raise exceptions.CulturalPartnerNotFoundException("Requested siren is not a known cultural partner for Adage")

    def notify_booking_cancellation_by_offerer(self, data: adage_serialize.EducationalBookingResponse) -> None:
        logger.info(
            "Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation-annule", data
        )

    def get_cultural_partners(
        self, since_date: datetime.datetime | None = None
    ) -> list[dict[str, str | int | float | None]]:
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
                "domaineIds": "1",
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
                "domaineIds": "1",
                "actif": 0,
                "dateModification": "2022-06-27T08:52:27.597Z",
                "synchroPass": 1,
            },
        ]

    def notify_institution_association(self, data: adage_serialize.AdageCollectiveOffer) -> None:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/offre-assoc", data)

    def get_cultural_partner(self, siret: str) -> adage_serialize.AdageCulturalPartner:
        logger.info("Adage has been called at %s", f"{self.base_url}/v1/etablissement-culturel/{siret}")
        if siret == "12345678200010":
            return adage_serialize.AdageCulturalPartner(
                id=128028,
                venueId=None,
                siret=siret,
                regionId=None,
                academieId=None,
                statutId=3,
                labelId=None,
                typeId=8,
                communeId="26324",
                libelle="Fête du livre jeunesse de St Paul les trois Châteaux",
                adresse="Place Charles Chausy",
                siteWeb="http://www.fetedulivrejeunesse.fr/",
                latitude=44.350457,
                longitude=4.765918,
                actif=1,
                dateModification=datetime.datetime(2021, 9, 1),
                statutLibelle="Association",
                labelLibelle=None,
                typeIcone="town",
                typeLibelle="Association ou fondation pour la promotion, le développement et la diffusion d\u0027oeuvres",
                communeLibelle="SAINT-PAUL-TROIS-CHATEAUX",
                communeDepartement="026",
                academieLibelle="GRENOBLE",
                regionLibelle="AUVERGNE-RHÔNE-ALPES",
                domaines="Architecture|Univers du livre, de la lecture et des écritures",
                domaineIds="1,11",
                synchroPass=0,
            )
        raise exceptions.CulturalPartnerNotFoundException("Requested cultural partner not found for Adage")

    def get_adage_educational_institutions(self, ansco: str) -> list[adage_serialize.AdageEducationalInstitution]:
        logger.info("Adage has been called at %s", f"{self.base_url}/v1/etablissement-culturel/?ansco={ansco}")
        if ansco == "6":
            return [
                adage_serialize.AdageEducationalInstitution(
                    uai="0470009E",
                    sigle="COLLEGE",
                    libelle="DE LA TOUR0",
                    communeLibelle="PARIS",
                    courriel="contact+collegelatour@example.com",
                    telephone="0600000000",
                    codePostal="75000",
                    latitude=decimal.Decimal("48.8534"),
                    longitude=decimal.Decimal("2.3488"),
                )
            ]
        raise exceptions.AdageEducationalInstitutionNotFound("Requested educational institution not found for Adage")

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        api_url = f"{self.base_url}/v1/redacteurs-projets/{uai}"
        logger.info("Adage has been called at %s", api_url)

        if uai == "0470009E":
            response_content = [
                {
                    "civilite": "Mme.",
                    "nom": "SKLODOWSKA",
                    "prenom": "MARIA",
                    "mail": "maria.sklodowska@example.com",
                },
                {
                    "civilite": "M.",
                    "nom": "POINTCARE",
                    "prenom": "HENRI",
                    "mail": "raymond.pointcare@example.com",
                },
                {
                    "civilite": "M.",
                    "nom": "HENMAR",
                    "prenom": "CONFUSION",
                    "mail": "confusion.raymar@example.com",
                },
            ]
        elif uai == "0560071Y":
            response_content = [
                {
                    "civilite": "Mme.",
                    "nom": "COMPTE",
                    "prenom": "TEST",
                    "mail": "compte.test@example.com",
                },
            ]
        else:
            raise exceptions.EducationalRedactorNotFound("No educational redactor found for the given UAI")

        return response_content

    def notify_reimburse_collective_booking(self, data: adage_serialize.AdageReimbursementNotification) -> None:
        api_url = f"{self.base_url}/v1/reservation-remboursement"
        logger.info("Adage has been called at %s", api_url)

    def notify_redactor_when_collective_request_is_made(self, data: adage_serialize.AdageCollectiveRequest) -> None:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/offre-vitrine", data)
