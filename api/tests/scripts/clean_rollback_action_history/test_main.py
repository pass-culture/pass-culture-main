import datetime
from unittest.mock import patch

import pytest

from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.scripts.clean_rollback_action_history.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_clean_action_history():
    venue_address = offerers_factories.VenueFactory(siret=None, comment="address venue")  # venue address without siret
    venue_with_siret = offerers_factories.VenueFactory(managingOfferer=venue_address.managingOfferer)
    author = users_factories.UserFactory()

    # Action history during regularization
    venue_regularization_action_history = history_factories.ActionHistoryFactory(
        actionType=history_models.ActionType.VENUE_REGULARIZATION,
        authorUser=None,
        comment=None,
        venueId=venue_address.id,
        extraData={"destination_venue_id": venue_with_siret.id},
        actionDate=datetime.datetime(2025, 8, 21),
    )
    venue_soft_deleted_action_history = history_factories.ActionHistoryFactory(
        authorUser=None,
        comment=None,
        venueId=venue_address.id,
        actionType=history_models.ActionType.VENUE_SOFT_DELETED,
        actionDate=datetime.datetime(2025, 8, 21),
    )

    # Action history during rollback (origin & destination has been switched)
    venue_regularization_action_history_incomplete = history_factories.ActionHistoryFactory(
        actionType=history_models.ActionType.VENUE_REGULARIZATION,
        authorUser=None,
        comment=None,
        venueId=venue_with_siret.id,  # we rolled back from venue_with_siret to former venue_address
        extraData={"destination_venue_id": venue_address.id},
        actionDate=datetime.datetime(2025, 10, 21),
    )
    history_factories.ActionHistoryFactory(
        authorUser=None,
        comment=None,
        venueId=venue_with_siret.id,
        actionType=history_models.ActionType.VENUE_SOFT_DELETED,
        actionDate=datetime.datetime(2025, 10, 21),
    )  # should not have been created

    # Some other venue's rollback
    another_address_venue = offerers_factories.VenueFactory(managingOfferer=venue_address.managingOfferer)
    history_factories.ActionHistoryFactory(
        actionType=history_models.ActionType.VENUE_REGULARIZATION,
        authorUser=None,
        comment=None,
        venueId=venue_with_siret.id,
        extraData={"destination_venue_id": another_address_venue.id},
        actionDate=datetime.datetime(2025, 10, 21),  # rollback the same day
    )

    assert venue_regularization_action_history_incomplete.authorUser is None

    mock_csv_rows = [
        {
            "jsonPayload.extra.origin_venue_id": str(venue_with_siret.id),
            "jsonPayload.extra.destination_venue_id": str(venue_address.id),
            "timestamp": "2025-10-21T12:53:58.399052765Z",
        },
        {
            "jsonPayload.extra.origin_venue_id": str(venue_with_siret.id),
            "jsonPayload.extra.destination_venue_id": str(venue_address.id),
            "timestamp": "2025-10-21T12:53:58.399052765Z",
        },  # just to be sure that duplicated lines do not alter the output
    ]

    with patch("pcapi.scripts.clean_rollback_action_history.main._read_csv_file", return_value=iter(mock_csv_rows)):
        main(not_dry=True, author=author, filename="test_file")

    venue_address_action_history = (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.venueId == venue_address.id)
        .count()
    )
    assert (
        venue_address_action_history == 3
    )  # the rollback action history has been moved from venue with siret to venue address

    venue_address_comment_count = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.venueId == venue_address.id,
            history_models.ActionHistory.actionType == history_models.ActionType.COMMENT,
        )
        .count()
    )
    assert venue_address_comment_count == 1

    venue_address_comment_count = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.venueId == venue_with_siret.id,
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_SOFT_DELETED,
        )
        .count()
    )
    assert venue_address_comment_count == 0  # VENUE_SOFT_DELETE action history has been removed from venue with siret

    # we didn't change this action history
    assert venue_soft_deleted_action_history.authorUser is None
    # we didn't change this action history either
    assert venue_regularization_action_history.authorUser is None

    assert venue_regularization_action_history_incomplete.authorUser == author  # should be updated
    assert (
        venue_regularization_action_history_incomplete.venueId == venue_address.id
    )  # should be updated with old venue ID
    assert (
        venue_regularization_action_history_incomplete.actionType == history_models.ActionType.COMMENT
    )  # should be updated
    assert (
        venue_regularization_action_history_incomplete.comment
        == "Rollback from Venue Regularization: Venue soft delete has been reverted."
    )
