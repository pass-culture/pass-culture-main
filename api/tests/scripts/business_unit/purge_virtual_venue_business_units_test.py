import pytest

from pcapi.core.finance.factories import BusinessUnitFactory
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.scripts.business_unit.purge_virtual_venue_business_units import purge_virtual_venue_business_units


@pytest.mark.usefixtures("db_session")
def test_purge_virtual_venue_business_units():
    expected_existing_bu = []
    expected_purged_bu = []
    expected_venues_without_bu = []

    # Delete business unit that containt a single virtual venue
    business_unit = BusinessUnitFactory(name="Business unit 1")
    virtual_venue = VenueFactory(isVirtual=True, siret=None, businessUnit=business_unit)
    expected_purged_bu.append(business_unit)
    expected_venues_without_bu.append(virtual_venue)

    # Delete business unit that containt a single virtual venue.
    # Even if it have a existing offer.
    business_unit = BusinessUnitFactory(name="Business unit 2")
    virtual_venue = VenueFactory(isVirtual=True, siret=None, businessUnit=business_unit)
    OfferFactory(venue=virtual_venue)
    expected_purged_bu.append(business_unit)
    expected_venues_without_bu.append(virtual_venue)

    # Do not delete business unit when it containe a least one physical venue.
    # Virtual venue without offer should be removed from the business unit.
    business_unit = BusinessUnitFactory(name="Business unit 3")
    VenueFactory(isVirtual=False, businessUnit=business_unit)
    virtual_venue = VenueFactory(isVirtual=True, siret=None, businessUnit=business_unit)
    expected_existing_bu.append(business_unit)
    expected_venues_without_bu.append(virtual_venue)

    # Do not delete business unit when it containe a least one physical venue.
    # Virtual venue with at least one offer can stay on the business unit.
    business_unit = BusinessUnitFactory(name="Business unit 4")
    VenueFactory(isVirtual=False, businessUnit=business_unit)
    virtual_venue = VenueFactory(isVirtual=True, siret=None, businessUnit=business_unit)
    OfferFactory(venue=virtual_venue)
    expected_existing_bu.append(business_unit)

    purge_virtual_venue_business_units()

    all_business_units = BusinessUnit.query.all()
    assert len(all_business_units) == len(expected_existing_bu)
    for business_unit in expected_existing_bu:
        assert business_unit.id in [bu.id for bu in all_business_units]

    all_venues = Venue.query.all()
    expected_venues_without_bu_ids = [v.id for v in expected_venues_without_bu]
    for venue in all_venues:
        if venue.id in expected_venues_without_bu_ids:
            assert venue.businessUnitId is None
        else:
            assert venue.businessUnitId is not None
