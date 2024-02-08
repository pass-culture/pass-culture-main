from datetime import datetime
from unittest.mock import patch

import requests_mock

from pcapi.core.educational.api import adage as educational_api_adage
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.core.testing import override_settings


@override_settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
)
def test_synchronize_adage_ids_on_venues(db_session):
    venue1 = offerers_factories.VenueFactory()
    venue2 = offerers_factories.VenueFactory()
    venue3 = offerers_factories.VenueFactory()
    venue4 = offerers_factories.VenueFactory()
    venue5 = offerers_factories.VenueFactory(adageId="11", adageInscriptionDate=datetime.utcnow())
    venue6 = offerers_factories.VenueFactory(adageId="1252", adageInscriptionDate=datetime.utcnow())

    BASE_DATA = {
        "siret": "",
        "regionId": None,
        "academieId": None,
        "statutId": None,
        "labelId": None,
        "typeId": 8,
        "communeId": "26324",
        "libelle": "Fête du livre jeunesse de St Paul les trois Châteaux",
        "adresse": "Place Charles Chausy",
        "siteWeb": "http://www.fetedulivrejeunesse.fr/",
        "latitude": 44.350457,
        "longitude": 4.765918,
        "actif": 1,
        "dateModification": "2021-09-01T00:00:00",
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
        "synchroPass": 1,
    }

    adage_id1 = 128028
    adage_id2 = 128029
    adage_id3 = 128030
    adage_id4 = 128031
    adage_id5 = 128032

    venue1_data = {**BASE_DATA, "id": adage_id1, "venueId": venue1.id}
    venue1_extra_data = {**BASE_DATA, "id": adage_id5, "venueId": venue1.id}
    venue2_data = {**BASE_DATA, "id": adage_id2, "venueId": venue2.id}
    venue3_data = {**BASE_DATA, "id": adage_id3, "venueId": venue3.id, "synchroPass": 0}
    venue4_data = {**BASE_DATA, "id": adage_id4, "venueId": None}
    venue5_data = {**BASE_DATA, "id": adage_id4, "venueId": venue5.id, "synchroPass": 1, "actif": None}
    venue6_data = {**BASE_DATA, "id": adage_id3, "venueId": venue6.id, "synchroPass": 0, "actif": None}

    email2 = get_emails_by_venue(venue2)

    with requests_mock.Mocker() as request_mock:
        request_mock.get(
            "https://adage-api-url/v1/partenaire-culturel",
            request_headers={
                "X-omogen-api-key": "adage-api-key",
            },
            status_code=200,
            json=[venue1_data, venue1_extra_data, venue2_data, venue3_data, venue4_data, venue5_data, venue6_data],
        )
        with patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email") as mock_activation_mail:
            educational_api_adage.synchronize_adage_ids_on_venues()

    # venue1 had not adageId and obtained two after synchronization
    # (venues merged)
    # -> two new AdageVenueAddress must have been created
    # -> the last adageId received is saved inside the Venue
    assert venue1.adageId == str(adage_id5)
    assert venue1.adageInscriptionDate is not None
    assert {ava.adageId for ava in venue1.adage_addresses} == {str(adage_id1), str(adage_id5)}
    assert {ava.adageInscriptionDate.date() for ava in venue1.adage_addresses} == {venue1.adageInscriptionDate.date()}

    # venue2 had not adageId and obtained one after synchronization
    # -> a new AdageVenueAddress must have been created
    assert venue2.adageId == str(adage_id2)
    assert venue2.adageInscriptionDate is not None
    assert {ava.adageId for ava in venue2.adage_addresses} == {str(adage_id2)}
    assert {ava.adageInscriptionDate.date() for ava in venue2.adage_addresses} == {venue2.adageInscriptionDate.date()}

    # venue3 had no known adageId, synchronization could have added one
    # but the synchroPass flag was false
    # -> no new AdageVenueAddress could have been created
    assert venue3.adageId is None
    assert venue3.adageInscriptionDate is None
    assert not venue3.adage_addresses

    # venue4 had no known adageId and did not obtain one from the
    # synchronization
    # -> no new AdageVenueAddress could have been created
    assert venue4.adageId is None
    assert venue4.adageInscriptionDate is None
    assert not venue4.adage_addresses

    # venue5 had a adageId and was marked as inactive by the
    # synchronization
    # -> it has a AdageVenueAddress that should have been updated
    #    (adageId and adageInscriptionDate)
    assert venue5.adageId is None
    assert venue5.adageInscriptionDate is None
    assert {ava.adageId for ava in venue5.adage_addresses} == {None}
    assert {ava.adageInscriptionDate for ava in venue5.adage_addresses} == {None}

    # venue6 had a adageId and the synchroPass was false
    # -> it has a AdageVenueAddress that should have been updated
    #    (adageId and adageInscriptionDate)
    assert venue6.adageId is None
    assert venue6.adageInscriptionDate is None
    assert {ava.adageId for ava in venue6.adage_addresses} == {None}
    assert {ava.adageInscriptionDate for ava in venue6.adage_addresses} == {None}

    assert mock_activation_mail.call_args.args[0] == venue2
    assert set(mock_activation_mail.call_args.args[1]) == set(email2)
