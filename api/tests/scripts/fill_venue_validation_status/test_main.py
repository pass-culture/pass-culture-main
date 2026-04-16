import pytest

from pcapi.core.offerers import factories
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.scripts.fill_venue_validation_status.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_one_venue_without_validation_status():
    venue = factories.VenueFactory(validationStatus=None)
    main(apply=True)

    db.session.refresh(venue)
    assert venue.validationStatus == venue.managingOfferer.validationStatus


def test_only_updates_venues_without_validation_status():
    venue_to_update = factories.VenueFactory(validationStatus=None)
    venue_to_ignore = factories.VenueFactory(
        managingOfferer__validationStatus=ValidationStatus.NEW, validationStatus=ValidationStatus.VALIDATED
    )

    main(apply=True)

    db.session.refresh(venue_to_update)
    db.session.refresh(venue_to_ignore)

    assert venue_to_update.validationStatus == venue_to_update.managingOfferer.validationStatus
    assert venue_to_ignore.validationStatus == ValidationStatus.VALIDATED


def test_nothing_is_updated_when_apply_is_fals():
    venue_to_update = factories.VenueFactory(validationStatus=None)
    venue_to_ignore = factories.VenueFactory(validationStatus=ValidationStatus.VALIDATED)

    main(apply=False)

    db.session.refresh(venue_to_update)
    db.session.refresh(venue_to_ignore)

    assert not venue_to_update.validationStatus
    assert venue_to_ignore.validationStatus == ValidationStatus.VALIDATED
