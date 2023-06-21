from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational import exceptions
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveRequest
from pcapi.core.educational.adage_backends.serialize import AdageEducationalInstitution
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.serialization import venues_serialize

from .. import testing


class AdageSpyClient(AdageClient):
    def notify_prebooking(self, data: prebooking.EducationalBookingResponse) -> None:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation", "sent_data": data})

    def notify_offer_or_stock_edition(self, data: prebooking.EducationalBookingResponse) -> None:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-edit", "sent_data": data})

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise RuntimeError("Do not use the spy for this method, mock the get request instead")

    def notify_booking_cancellation_by_offerer(self, data: prebooking.EducationalBookingResponse) -> None:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-annule", "sent_data": data})

    def get_cultural_partners(self) -> list[dict[str, str | int | float | None]]:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/partenaire-culturel", "sent_data": ""})
        return [
            {
                "id": "128029",
                "venueId": None,
                "siret": "21260324500011",
                "regionId": None,
                "academieId": None,
                "statutId": None,
                "labelId": "4",
                "typeId": "4",
                "communeId": "26324",
                "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                "adresse": "Place de Castellane",
                "siteWeb": "http://www.musat.fr/",
                "latitude": "44.349098",
                "longitude": "4.768178",
                "actif": "1",
                "dateModification": "2021-09-01 00:00:00",
                "statutLibelle": None,
                "labelLibelle": "Musée de France",
                "typeIcone": "museum",
                "typeLibelle": "Musée, domaine ou monument",
                "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                "communeDepartement": "026",
                "academieLibelle": "GRENOBLE",
                "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                "domaines": "Patrimoine, mémoire, archéologie",
                "domaineIds": "13",
                "synchroPass": 0,
            },
            {
                "id": "128028",
                "venueId": None,
                "siret": "",
                "regionId": None,
                "academieId": None,
                "statutId": None,
                "labelId": None,
                "typeId": "8",
                "communeId": "26324",
                "libelle": "Fête du livre jeunesse de St Paul les trois Châteaux",
                "adresse": "Place Charles Chausy",
                "siteWeb": "http://www.fetedulivrejeunesse.fr/",
                "latitude": "44.350457",
                "longitude": "4.765918",
                "actif": "1",
                "dateModification": "2021-09-01 00:00:00",
                "statutLibelle": None,
                "labelLibelle": None,
                "typeIcone": "town",
                "typeLibelle": "Association ou fondation pour la promotion, le développement et la diffusion d\u0027oeuvres",
                "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                "communeDepartement": "026",
                "academieLibelle": "GRENOBLE",
                "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                "domaines": "Univers du livre, de la lecture et des écritures",
                "domaineIds": "11",
                "synchroPass": 0,
            },
        ]

    def notify_institution_association(self, data: AdageCollectiveOffer) -> None:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/offre-assoc", "sent_data": data})

    def get_cultural_partner(self, siret: str) -> venues_serialize.AdageCulturalPartner:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/partenaire-culturel/{siret}", "sent_data": ""})
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
            domaines="Architecture|Univers du livre, de la lecture et des écritures",
            domaineIds="1,11",
            synchroPass=0,
        )

    def get_adage_educational_institutions(self, ansco: str) -> list[AdageEducationalInstitution]:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/etablissement-culturel/{ansco}", "sent_data": ""})
        return [
            AdageEducationalInstitution(
                uai="0470009E",
                sigle="COLLEGE",
                libelle="DE LA TOUR0",
                communeLibelle="PARIS",
                courriel="contact+collegelatour@example.com",
                telephone="0600000000",
                codePostal="75000",
            ),
            AdageEducationalInstitution(
                uai="0470010E",
                sigle="CLG",
                libelle="Balamb Garden",
                communeLibelle="Balamb",
                courriel="contact+squall@example.com",
                telephone="0600000000",
                codePostal="75001",
            ),
        ]

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        api_url = f"{self.base_url}/v1/redacteurs-projets/{uai}"
        testing.adage_requests.append({"url": api_url, "sent_data": ""})
        if uai == "0470009E":
            return [
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
                    "mail": "henri.pointcare@example.com",
                },
                {
                    "civilite": "M.",
                    "nom": "HENMAR",
                    "prenom": "CONFUSION",
                    "mail": "confusion.raymar@example.com",
                },
            ]
        raise exceptions.EducationalRedactorNotFound("No educational redactor found for the given UAI")

    def notify_reimburse_collective_booking(self, data: prebooking.AdageReibursementNotification) -> None:
        api_url = f"{self.base_url}/v1/reservation-remboursement"
        testing.adage_requests.append({"url": api_url, "sent_data": ""})

    def notify_redactor_when_collective_request_is_made(self, data: AdageCollectiveRequest) -> None:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/offre-vitrine", "sent_data": data})
