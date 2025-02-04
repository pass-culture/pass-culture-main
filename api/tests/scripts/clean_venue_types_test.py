import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.schemas as offerers_schemas
from pcapi.models import db
import pcapi.scripts.clean_venue_types_step1.main as clean_venue_types


pytestmark = pytest.mark.usefixtures("db_session")


def test_updates_venue_types():
    venue1 = offerers_factories.VenueFactory(venueTypeCode=offerers_schemas.VenueTypeCode.FESTIVAL)
    venue2 = offerers_factories.VenueFactory(venueTypeCode=offerers_schemas.VenueTypeCode.FESTIVAL)
    venue3 = offerers_factories.VenueFactory(venueTypeCode=offerers_schemas.VenueTypeCode.FESTIVAL)
    venue4 = offerers_factories.VenueFactory(venueTypeCode=offerers_schemas.VenueTypeCode.FESTIVAL)
    venue_not_updated = offerers_factories.VenueFactory(venueTypeCode=offerers_schemas.VenueTypeCode.FESTIVAL)

    update_data = [
        {
            clean_venue_types.VENUE_ID_HEADER: venue1.id,
            clean_venue_types.NEW_VENUE_TYPE_HEADER: "Librairie",
        },
        {
            clean_venue_types.VENUE_ID_HEADER: venue2.id,
            clean_venue_types.NEW_VENUE_TYPE_HEADER: "Cours et pratique artistiques",
        },
        {
            clean_venue_types.VENUE_ID_HEADER: venue3.id,
            clean_venue_types.NEW_VENUE_TYPE_HEADER: "Librairie",
        },
        {
            clean_venue_types.VENUE_ID_HEADER: venue4.id,
            clean_venue_types.NEW_VENUE_TYPE_HEADER: "toto",
        },
    ]

    clean_venue_types.process_file(update_data)

    for venue in (venue1, venue2, venue3, venue4, venue_not_updated):
        db.session.refresh(venue)
    assert venue1.venueTypeCode == offerers_schemas.VenueTypeCode.BOOKSTORE
    assert venue2.venueTypeCode == offerers_schemas.VenueTypeCode.ARTISTIC_COURSE
    assert venue3.venueTypeCode == offerers_schemas.VenueTypeCode.BOOKSTORE
    assert venue4.venueTypeCode == offerers_schemas.VenueTypeCode.FESTIVAL
    assert venue_not_updated.venueTypeCode == offerers_schemas.VenueTypeCode.FESTIVAL
