import pytest

from pcapi.core.educational import schemas
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")

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


@pytest.mark.settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="AdageHttpClient",
)
def test_synchronize_adage_ids_on_offerers():
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
        managingOfferer__allowedOnAdage=False, adageId="11", adageInscriptionDate=date_utils.get_naive_utc_now()
    )
    venue6 = offerers_factories.VenueFactory(
        managingOfferer__allowedOnAdage=False, adageId="1252", adageInscriptionDate=date_utils.get_naive_utc_now()
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

    partners = [
        schemas.AdageCulturalPartner(**partner_data)
        for partner_data in (
            venue1_data,
            venue2_data,
            venue3_data,
            venue4_data,
            venue5_data,
            venue6_data,
            venue7_data,
            venue8_data,
        )
    ]

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


@pytest.mark.settings(
    ADAGE_API_URL="https://adage-api-url",
    ADAGE_API_KEY="adage-api-key",
    ADAGE_BACKEND="AdageHttpClient",
)
def test_synchronize_adage_ids_on_offerers_for_tricky_case():
    # Let's say we have a venue that has a SIRET and is synchronized with Adage
    # but Adage has another SIRET for it.
    # The synchronize_adage_partners should fill the Venue with an AdageId
    # and it should be set on the offerer despite the difference in SIRET

    ADAGE_ID = 128028
    venue1 = offerers_factories.VenueFactory(
        siret="24567870500000", adageId=ADAGE_ID, managingOfferer__allowedOnAdage=False
    )

    venue1_data = {**BASE_DATA, "id": ADAGE_ID, "siret": "35678980500000", "venueId": venue1.id}

    assert not venue1.managingOfferer.allowedOnAdage

    partners = [schemas.AdageCulturalPartner(**venue1_data)]

    educational_api_adage.synchronize_adage_ids_on_offerers(partners)
    db.session.commit()

    assert venue1.managingOfferer.allowedOnAdage

    educational_api_adage.synchronize_adage_ids_on_offerers(partners)
    db.session.commit()

    assert venue1.managingOfferer.allowedOnAdage


@pytest.mark.parametrize("initial_allowed_on_adage", (True, False))
def test_synchronize_adage_ids_on_offerers_soft_deleted_venue(initial_allowed_on_adage):
    ADAGE_ID = 128028
    offerer = offerers_factories.OffererFactory(allowedOnAdage=initial_allowed_on_adage)
    venue = offerers_factories.VenueFactory(adageId=ADAGE_ID, managingOfferer=offerer)
    venue.isSoftDeleted = True
    db.session.add(venue)

    assert offerer.allowedOnAdage is initial_allowed_on_adage

    educational_api_adage.synchronize_adage_ids_on_offerers([])
    db.session.commit()

    assert offerer.allowedOnAdage
