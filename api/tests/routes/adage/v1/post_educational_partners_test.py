from unittest import mock

import pytest

from pcapi.core.educational import schemas
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def test_post_educational_partners_unauthenticated(client: TestClient):
    response = client.post(
        "/adage/v1/cultural-partners",
        json={
            "id": 999999,
            "venueId": 1,
            "libelle": "Unknown Venue",
            "dateModification": get_naive_utc_now().isoformat(),
            "synchroPass": 1,
            "actif": 1,
        },
    )
    assert response.status_code == 401, response.json


def test_post_educational_partners_with_unknown_venue(client: TestClient):
    assert db.session.query(offerers_models.Venue).count() == 0
    client.with_eac_token()
    response = client.post(
        "/adage/v1/cultural-partners",
        json={
            "id": 999999,
            "venueId": 1,
            "libelle": "Unknown Venue",
            "dateModification": get_naive_utc_now().isoformat(),
            "synchroPass": 1,
            "actif": 1,
        },
    )
    assert response.status_code == 204, response.json
    assert db.session.query(offerers_models.Venue).count() == 0


@mock.patch("pcapi.core.external.beamer.tasks.update_beamer_pro_attributes_task.delay", return_value=None)
@mock.patch("pcapi.tasks.sendinblue_tasks.update_sib_pro_attributes_task.delay", return_value=None)
def test_post_educational_partners_venue_now_has_adage_id(mocked_beamer, mocked_sib, client: TestClient):
    venue = offerers_factories.VenueFactory(adageId=None, managingOfferer__allowedOnAdage=False)
    venue_with_adage_id = offerers_factories.VenueFactory(adageId="999", managingOfferer=venue.managingOfferer)
    venue_without_adage_id = offerers_factories.VenueFactory(adageId=None, managingOfferer=venue.managingOfferer)
    venue_id = venue.id
    assert venue.managingOfferer.allowedOnAdage is False

    client.with_eac_token()

    num_queries = (
        0
        + 1  # Fetch venue that are closed on Adage
        + 1  # Fetch venues that are known on Adage and not closed
        + 1  # Get the emails associated to the venue
        + 1  # Update venue with new adageId/date
        + 1  # Add action history entry
        + 1  # Fetch allowed offerers
        + 1  # Fetch offerers with venue with adageId
        + 1  # Update offerer allowedOnAdage=True
        + 1  # Update offerer allowedOnAdage=False
    )
    with assert_num_queries(num_queries):
        response = client.post(
            "/adage/v1/cultural-partners",
            json={
                "id": 123456,
                "venueId": venue_id,
                "libelle": "libellule",
                "dateModification": get_naive_utc_now().isoformat(),
                "synchroPass": 1,
                "actif": 1,
            },
        )
        assert response.status_code == 204, response.json

    db.session.refresh(venue)
    assert venue.adageId == "123456"
    db.session.refresh(venue_with_adage_id)
    assert venue_with_adage_id.adageId == "999"
    db.session.refresh(venue_without_adage_id)
    assert venue_without_adage_id.adageId is None
    assert venue.managingOfferer.allowedOnAdage is True


@mock.patch("pcapi.core.educational.adage.client.get_adage_offerer", return_value=[])
def test_post_educational_partners_venue_deactivated_on_adage(
    mock_get_adage_offerer: mock.MagicMock, client: TestClient
):
    venue = offerers_factories.VenueFactory(adageId="123", managingOfferer__allowedOnAdage=False)

    client.with_eac_token()
    response = client.post(
        "/adage/v1/cultural-partners",
        json={
            "id": 123456,
            "venueId": venue.id,
            "libelle": "libellule",
            "dateModification": get_naive_utc_now().isoformat(),
            "synchroPass": 1,
            "actif": 0,
        },
    )
    assert response.status_code == 204, response.json
    mock_get_adage_offerer.assert_called_once()

    db.session.refresh(venue)
    assert venue.adageId is None
    assert venue.managingOfferer.allowedOnAdage is False


@mock.patch("pcapi.core.educational.adage.client.get_adage_offerer")
def test_post_educational_partners_venue_deactivated_on_adage_has_other_partner(
    mock_get_adage_offerer: mock.MagicMock, client: TestClient
):
    venue = offerers_factories.VenueFactory(
        adageId="123", managingOfferer__allowedOnAdage=True, managingOfferer__siren="123456789"
    )
    mock_get_adage_offerer.return_value = [
        schemas.AdageCulturalPartner(
            id=123457,
            venueId=None,
            libelle="libellule",
            dateModification=get_naive_utc_now().isoformat(),
            synchroPass=0,
            actif=1,
            siret="12345678912345",
        )
    ]

    client.with_eac_token()
    response = client.post(
        "/adage/v1/cultural-partners",
        json={
            "id": 123456,
            "venueId": venue.id,
            "libelle": "libellule",
            "dateModification": get_naive_utc_now().isoformat(),
            "synchroPass": 1,
            "actif": 0,
        },
    )
    assert response.status_code == 204, response.json
    mock_get_adage_offerer.assert_called_once_with(siren="123456789")

    # offerer was allowed on adage
    # venue is deactivated -> adageId becomes None
    # but there is another adage partner that matches the SIREN -> offerer keeps allowedOnAdage=True
    db.session.refresh(venue)
    assert venue.adageId is None
    assert venue.managingOfferer.allowedOnAdage is True


@mock.patch("pcapi.core.educational.adage.client.get_adage_offerer", return_value=[])
def test_post_educational_partners_venue_not_sync_with_pass(mock_get_adage_offerer: mock.MagicMock, client: TestClient):
    venue = offerers_factories.VenueFactory(adageId="123", managingOfferer__allowedOnAdage=True)

    client.with_eac_token()
    response = client.post(
        "/adage/v1/cultural-partners",
        json={
            "id": 123456,
            "venueId": venue.id,
            "libelle": "libellule",
            "dateModification": get_naive_utc_now().isoformat(),
            "synchroPass": 0,
            "actif": 1,
        },
    )
    assert response.status_code == 204, response.json
    mock_get_adage_offerer.assert_called_once_with(siren=venue.managingOfferer.siren)

    # offerer was allowed on adage
    # venue is deactivated -> adageId becomes None
    # there is no other adage partner that matches the SIREN -> offerer becomes allowedOnAdage=False
    db.session.refresh(venue)
    assert venue.adageId is None
    assert venue.managingOfferer.allowedOnAdage is False
