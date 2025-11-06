from typing import Any
from unittest import mock

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now


pytestmark = pytest.mark.usefixtures("db_session")


def test_post_educational_partners_unauthenticated(client: Any) -> None:
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


def test_post_educational_partners_with_unknown_venue(client: Any) -> None:
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


@mock.patch("pcapi.tasks.beamer_tasks.update_beamer_pro_attributes_task.delay", return_value=None)
@mock.patch("pcapi.tasks.sendinblue_tasks.update_sib_pro_attributes_task.delay", return_value=None)
def test_post_educational_partners_venue_now_has_adage_id(mocked_beamer, mocked_sib, client: Any) -> None:
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
        + 1  # FF from update_external_pro
        + 1  # Send EAC offerer activation email
        + 1  # Update venue with new adageId/date
        + 1  # Add action history entry
        + 1  # Update offerer allowedOnAdage
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


def test_post_educational_partners_venue_deactivated_on_adage(client: Any) -> None:
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

    db.session.refresh(venue)
    assert venue.adageId is None
    assert venue.managingOfferer.allowedOnAdage is False


def test_post_educational_partners_venue_not_sync_with_pass(client: Any) -> None:
    venue = offerers_factories.VenueFactory(adageId="123", managingOfferer__allowedOnAdage=False)

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

    db.session.refresh(venue)
    assert venue.adageId is None
    assert venue.managingOfferer.allowedOnAdage is False
