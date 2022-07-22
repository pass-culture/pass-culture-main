from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.routes.serialization import venues_serialize

from .. import testing


class AdageSpyClient(AdageClient):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation", "sent_data": data})
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)  # type: ignore [arg-type]

    def notify_offer_or_stock_edition(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-edit", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise Exception("Do not use the spy for this method, mock the get request instead")

    def notify_booking_cancellation_by_offerer(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-annule", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

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

    def notify_institution_association(self, data: AdageCollectiveOffer) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/offre-assoc", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

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
