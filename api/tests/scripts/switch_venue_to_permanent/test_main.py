import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.scripts.switch_venue_to_permanent.main import main


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize(
    "siret, comment, is_open_to_public, should_become_permanent",
    [
        ["1234567891234", None, False, True],  # venue with siret -> permanent
        ["1234567891234", None, True, True],  # venue with siret and open to public -> permanent
        [None, "no siret", True, True],  # venue without siret open to public -> permanent
        [None, "no siret", False, False],  # venue without siret closed to public -> should not change
    ],
)
def test_basic(siret, comment, is_open_to_public, should_become_permanent):
    venue = offerers_factories.VenueFactory(
        siret=siret,
        comment=comment,
        isPermanent=False,
        isOpenToPublic=is_open_to_public,
    )

    main(commit=True)

    assert venue.isPermanent == should_become_permanent
    assert venue.isOpenToPublic == is_open_to_public  # should not change
    assert venue.isSoftDeleted == False  # should not change


@pytest.mark.parametrize(
    "siret, comment, is_permanent, is_open_to_public",
    [
        ["1234567891234", None, False, False],  # venue soft deleted, no change even with siret
        [None, "no siret", False, True],  # venue soft deleted, no change
        [None, "no siret", True, False],  # venue soft deleted, no change
    ],
)
def test_with_soft_deleted_venues(siret, comment, is_permanent, is_open_to_public):
    venue = offerers_factories.VenueFactory(
        siret=siret,
        comment=comment,
        isPermanent=is_permanent,
        isOpenToPublic=is_open_to_public,
    )
    venue_id = venue.id
    venue.isSoftDeleted = True

    main(commit=True)
    venue = db.session.query(Venue).filter(Venue.id == venue_id).execution_options(include_deleted=True).one()
    assert venue.isPermanent == is_permanent  # should not change
    assert venue.isOpenToPublic == is_open_to_public  # should not change
    assert venue.isSoftDeleted == True  # should not change


def test_dry_run_should_not_commit():
    venue = offerers_factories.VenueFactory(
        siret="1234567891234",
        comment=None,
        isPermanent=False,
        isOpenToPublic=True,
    )

    main(commit=False)

    assert venue.isPermanent == False  # should not change
    assert venue.isOpenToPublic == True  # should not change
    assert venue.isSoftDeleted == False  # should not change
