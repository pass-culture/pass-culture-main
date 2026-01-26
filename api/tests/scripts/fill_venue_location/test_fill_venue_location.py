import pytest

import pcapi.core.geography.factories as geography_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.models import db
from pcapi.scripts.fill_venue_location.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_location_addition():
    # First offerer: one venue, one location
    venue_alone = offerers_factories.VenueFactory(offererAddress=None)
    location_alone = offerers_factories.OffererAddressFactory(offerer=venue_alone.managingOfferer, type=None)
    assert venue_alone.offererAddress is None

    # Second offerer: one venue, 2 locations that both have offers, use the location of the first offer
    offerer1 = offerers_factories.OffererFactory()
    offerer1_venue1 = offerers_factories.VenueFactory(offererAddress=None, managingOfferer=offerer1)
    offerer1_venue2 = offerers_factories.VenueFactory(offererAddress=None, managingOfferer=offerer1)
    offer1a = offers_factories.OfferFactory(
        venue=offerer1_venue1, offererAddress=offerers_factories.OffererAddressFactory(offerer=offerer1, type=None)
    )
    offer1b = offers_factories.OfferFactory(
        venue=offerer1_venue1, offererAddress=offerers_factories.OffererAddressFactory(offerer=offerer1, type=None)
    )
    offer2 = offers_factories.OfferFactory(
        venue=offerer1_venue2, offererAddress=offerers_factories.OffererAddressFactory(offerer=offerer1, type=None)
    )
    assert offerer1_venue1.offererAddress is None
    assert offerer1_venue2.offererAddress is None
    assert offer1a.offererAddress.type is None
    assert offer1a.offererAddress.offerer == offerer1

    # Third offerer: 2 venue, 2 locations, no offers -> no way to know which is linked to which, goes to defaults
    offerer2 = offerers_factories.OffererFactory()
    offerer2_venue1 = offerers_factories.VenueFactory(offererAddress=None, managingOfferer=offerer2)
    offerer2_venue2 = offerers_factories.VenueFactory(offererAddress=None, managingOfferer=offerer2)
    offerers_factories.OffererAddressFactory(offerer=offerer2, type=None)
    offerers_factories.OffererAddressFactory(offerer=offerer2, type=None)

    # Fourth offerer: 1 venue with its location
    offerer3_venue1 = offerers_factories.VenueFactory()
    assert offerer3_venue1.offererAddress
    offerer3_offerer_address = offerer3_venue1.offererAddress

    # Add fake OA #1509
    geography_factories.AddressFactory(id=1509)
    db.session.flush()
    main(not_dry=True)
    db.session.flush()

    db.session.refresh(venue_alone)
    assert venue_alone.offererAddress
    assert venue_alone.offererAddress.type == offerers_models.LocationType.VENUE_LOCATION
    assert venue_alone.offererAddress.addressId == location_alone.addressId
    assert venue_alone.offererAddress.offererId == venue_alone.managingOffererId

    db.session.refresh(offerer1_venue1)
    db.session.refresh(offer1a)
    db.session.refresh(offer1b)
    assert offerer1_venue1.offererAddress
    assert offerer1_venue1.offererAddress.type == offerers_models.LocationType.VENUE_LOCATION
    assert offerer1_venue1.offererAddress.addressId == offer1a.offererAddress.addressId
    assert offerer1_venue1.offererAddress.offererId == offerer1_venue1.managingOffererId
    assert offer1a.offererAddress != offerer1_venue1.offererAddress
    assert offer1a.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION
    assert offer1b.offererAddress != offerer1_venue1.offererAddress
    assert offer1b.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION

    db.session.refresh(offerer1_venue2)
    db.session.refresh(offer2)
    assert offerer1_venue2.offererAddress
    assert offerer1_venue2.offererAddress.type == offerers_models.LocationType.VENUE_LOCATION
    assert offerer1_venue2.offererAddress.addressId == offer2.offererAddress.addressId
    assert offerer1_venue2.offererAddress.offererId == offerer1_venue2.managingOffererId
    assert offer2.offererAddress != offerer1_venue1.offererAddress
    assert offer2.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION

    db.session.refresh(offerer2_venue1)
    db.session.refresh(offerer2_venue2)
    assert offerer2_venue1.offererAddress
    assert offerer2_venue1.offererAddress.addressId == 1509
    assert offerer2_venue2.offererAddress.addressId == 1509

    db.session.refresh(offerer3_venue1)
    assert offerer3_venue1.offererAddress == offerer3_offerer_address
