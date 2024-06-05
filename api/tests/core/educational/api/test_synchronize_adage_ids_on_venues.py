from datetime import datetime
from datetime import timedelta
from datetime import timezone
import logging
import sys
from unittest.mock import patch

from pydantic.v1 import parse_obj_as
import requests_mock

from pcapi.core.educational.api import adage as educational_api_adage
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.core.testing import override_settings
from pcapi.models import db
from pcapi.routes.serialization import venues_serialize


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

    db.session.refresh(venue1)
    db.session.refresh(venue2)
    db.session.refresh(venue3)
    db.session.refresh(venue4)
    db.session.refresh(venue5)
    db.session.refresh(venue6)

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

    expected_emails = get_emails_by_venue(venue1) | get_emails_by_venue(venue2)
    expected_venues = {venue1.id, venue2.id}

    calls_args = mock_activation_mail.call_args_list
    called_venues = {call[0][0].id for call in calls_args}
    called_emails = {call[0][1][0] for call in calls_args}

    assert called_emails == expected_emails
    assert called_venues == expected_venues


@override_settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
)
def test_synchronize_adage_ids_on_venues_with_unknown_venue(db_session):
    """Test the synchronization is not blocked (no error) if the adage
    client returns an unknown venue id.
    """
    venue = offerers_factories.VenueFactory()

    adage_id1 = 128028
    adage_id2 = 128029
    adage_id3 = 128030

    unknown_venue_id = -1

    venue_data = {**BASE_DATA, "id": adage_id1, "venueId": venue.id}
    venue_extra_data = {**BASE_DATA, "id": adage_id3, "venueId": venue.id}
    venue2_data = {**BASE_DATA, "id": adage_id2, "venueId": unknown_venue_id}

    with requests_mock.Mocker() as request_mock:
        request_mock.get(
            "https://adage-api-url/v1/partenaire-culturel",
            request_headers={
                "X-omogen-api-key": "adage-api-key",
            },
            status_code=200,
            json=[venue_data, venue_extra_data, venue2_data],
        )
        with patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email"):
            educational_api_adage.synchronize_adage_ids_on_venues()

    db.session.refresh(venue)

    # venue had no adageId and obtained two after synchronization
    # (venues merged)
    # -> two new AdageVenueAddress must have been created
    # -> the last adageId received is saved inside the Venue
    assert venue.adageId == str(adage_id3)
    assert {ava.adageId for ava in venue.adage_addresses} == {str(adage_id1), str(adage_id3)}


@override_settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
)
def test_synchronize_adage_ids_on_venues_with_venue_id_missing(db_session, caplog):
    """Test the synchronization is not blocked (no error) if the adage
    client returns venue with no venue id.
    """
    adage_id1 = 128028
    adage_id_with_missing_venue_id = 128030

    venue = offerers_factories.VenueFactory()
    _venue_with_adage = offerers_factories.VenueFactory(adageId=str(adage_id_with_missing_venue_id))

    venue_data = {**BASE_DATA, "id": adage_id1, "venueId": venue.id}
    venue_data_without_venueId = {**BASE_DATA, "id": adage_id_with_missing_venue_id, "venueId": sys.maxsize}

    with requests_mock.Mocker() as request_mock:
        request_mock.get(
            "https://adage-api-url/v1/partenaire-culturel",
            request_headers={
                "X-omogen-api-key": "adage-api-key",
            },
            status_code=200,
            json=[venue_data, venue_data_without_venueId],
        )
        with patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email"):
            with caplog.at_level(logging.WARNING):
                educational_api_adage.synchronize_adage_ids_on_venues()

                assert "is not present in Adage" in caplog.records[0].message

    # venue had venue_id
    assert venue.adageId == str(adage_id1)


@override_settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
)
def test_synchronize_adage_ids_on_offerers(db_session):
    # venue1's offerer should be allowed because its venue siret matches the venue1_data
    # venue2's offerer should be allowed because its venue siret matches the venue2_data
    # venue3's offerer should be allowed because its venue siret matches the venue3_data though not synchronized with Pass
    # venue4's offerer should be allowed because its venue siret matches the venue4_data though not matching venueId
    # venue5's offerer should be allowed because its venue has an adageId (despite not being active)
    # venue6's offerer should be allowed because its venue has an adageId (despite not being active)
    # venue7's offerer should not be allowed because it is not active and has no adageId
    # venue8's offerer should not be allowed because it is not active and has no adageId
    venue1 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
    venue2 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
    venue3 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
    venue4 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
    venue5 = offerers_factories.VenueFactory(
        managingOfferer__allowedOnAdage=False, adageId="11", adageInscriptionDate=datetime.utcnow()
    )
    venue6 = offerers_factories.VenueFactory(
        managingOfferer__allowedOnAdage=False, adageId="1252", adageInscriptionDate=datetime.utcnow()
    )
    venue7 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
    venue8 = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)

    venue1_data = {**BASE_DATA, "id": 128028, "siret": venue1.siret, "venueId": venue1.id}
    venue2_data = {**BASE_DATA, "id": 128029, "siret": venue2.siret, "venueId": venue2.id}
    venue3_data = {**BASE_DATA, "id": 128030, "siret": venue3.siret, "venueId": venue3.id, "synchroPass": 0}
    venue4_data = {**BASE_DATA, "id": 128031, "siret": venue4.siret, "venueId": None, "synchroPass": 0}
    venue5_data = {
        **BASE_DATA,
        "id": 128030,
        "siret": venue5.siret,
        "venueId": venue5.id,
        "synchroPass": 1,
        "actif": None,
    }
    venue6_data = {
        **BASE_DATA,
        "id": 128030,
        "siret": venue6.siret,
        "venueId": venue6.id,
        "synchroPass": 0,
        "actif": None,
    }
    venue7_data = {
        **BASE_DATA,
        "id": 128030,
        "siret": venue7.siret,
        "venueId": venue7.id,
        "synchroPass": 1,
        "actif": None,
    }
    venue8_data = {
        **BASE_DATA,
        "id": 128030,
        "siret": venue8.siret,
        "venueId": venue8.id,
        "synchroPass": 0,
        "actif": None,
    }

    assert not venue1.managingOfferer.allowedOnAdage
    assert not venue2.managingOfferer.allowedOnAdage
    assert not venue3.managingOfferer.allowedOnAdage
    assert not venue4.managingOfferer.allowedOnAdage
    assert not venue5.managingOfferer.allowedOnAdage
    assert not venue6.managingOfferer.allowedOnAdage
    assert not venue7.managingOfferer.allowedOnAdage
    assert not venue8.managingOfferer.allowedOnAdage

    partners = parse_obj_as(
        venues_serialize.AdageCulturalPartners,
        {
            "partners": [
                venue1_data,
                venue2_data,
                venue3_data,
                venue4_data,
                venue5_data,
                venue6_data,
                venue7_data,
                venue8_data,
            ]
        },
    ).partners

    educational_api_adage.synchronize_adage_ids_on_offerers(partners)
    db.session.commit()

    assert venue1.managingOfferer.allowedOnAdage
    assert venue2.managingOfferer.allowedOnAdage
    assert venue3.managingOfferer.allowedOnAdage
    assert venue4.managingOfferer.allowedOnAdage
    assert venue5.managingOfferer.allowedOnAdage
    assert venue6.managingOfferer.allowedOnAdage
    assert not venue7.managingOfferer.allowedOnAdage
    assert not venue8.managingOfferer.allowedOnAdage


@override_settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
)
def test_synchronize_adage_ids_on_offerers_for_tricky_case(db_session):
    # Let's say we have a venue that has a SIRET and is synchronized with Adage
    # but Adage has another SIRET for it.
    # The synchronize_adage_ids_on_venues should fill the Venue with an AdageId
    # and it should be set on the offerer despite the difference in SIRET

    ADAGE_ID = 128028
    venue1 = offerers_factories.VenueFactory(
        siret="24567870500000", adageId=ADAGE_ID, managingOfferer__allowedOnAdage=False
    )

    venue1_data = {**BASE_DATA, "id": ADAGE_ID, "siret": "35678980500000", "venueId": venue1.id}

    assert not venue1.managingOfferer.allowedOnAdage

    partners = parse_obj_as(
        venues_serialize.AdageCulturalPartners,
        {"partners": [venue1_data]},
    ).partners

    educational_api_adage.synchronize_adage_ids_on_offerers(partners)
    db.session.commit()

    assert venue1.managingOfferer.allowedOnAdage

    educational_api_adage.synchronize_adage_ids_on_offerers(partners)
    db.session.commit()

    assert venue1.managingOfferer.allowedOnAdage


@override_settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="pcapi.core.educational.adage_backends.adage.AdageHttpClient",
)
@patch("pcapi.core.educational.api.adage.send_eac_offerer_activation_email")
def test_synchronize_adage_ids_on_venues_with_timestamp_filter(mock_send_eac_email, db_session):
    venue1 = offerers_factories.VenueFactory()
    venue2 = offerers_factories.VenueFactory(adageId="11", adageInscriptionDate=datetime.utcnow())

    adage_id1 = 128028
    adage_id2 = 128029

    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()  # pylint: disable=datetime-now
    a_month_ago = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()  # pylint: disable=datetime-now

    venue1_data = {**BASE_DATA, "id": adage_id1, "venueId": venue1.id, "dateModification": yesterday}
    venue2_data = {**BASE_DATA, "id": adage_id2, "venueId": venue2.id, "dateModification": a_month_ago}

    with requests_mock.Mocker() as request_mock:
        request_mock.get(
            "https://adage-api-url/v1/partenaire-culturel",
            request_headers={
                "X-omogen-api-key": "adage-api-key",
            },
            status_code=200,
            json=[venue1_data, venue2_data],
        )

        from pcapi.core.educational.adage_backends.adage import AdageHttpClient

        orig_get_cultural_partners = AdageHttpClient().get_cultural_partners
        rows = orig_get_cultural_partners()
        mocked_cultural_partners = [next(row for row in rows if row["venueId"] == venue1.id)]

        mock_path = "pcapi.core.educational.api.adage.adage_client"
        with patch(mock_path) as mock_adage_client:
            mock_adage_client.get_cultural_partners.return_value = mocked_cultural_partners
            educational_api_adage.synchronize_adage_ids_on_venues()

    db.session.refresh(venue1)
    db.session.refresh(venue2)

    # venue1 had not adageId and obtained one after synchronization
    # -> a new AdageVenueAddress must have been created
    assert venue1.adageId == str(adage_id1)
    assert venue1.adageInscriptionDate is not None
    assert {ava.adageId for ava in venue1.adage_addresses} == {str(adage_id1)}
    assert {ava.adageInscriptionDate.date() for ava in venue1.adage_addresses} == {venue1.adageInscriptionDate.date()}

    # venue2 had not adageId and obtained none after synchronization
    # -> it has been (arbitrarily) ignored because of its `dateModification`
    assert venue2.adageId == "11"
    assert venue2.adageInscriptionDate is not None
    assert len(venue2.adage_addresses) == 1
