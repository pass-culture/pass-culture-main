import pytest

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.offerers.factories import OfferLocationFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import LocationType
from pcapi.core.offers.factories import OfferFactory


pytestmark = pytest.mark.usefixtures("db_session")


def test_check_incorrect_offer_location_venueid():
    venue1 = VenueFactory()
    venue2 = VenueFactory(managingOfferer=venue1.managingOfferer)
    offer1 = OfferFactory(
        venue=venue1,
        offererAddress=OfferLocationFactory(
            venue=venue1, offerer=venue1.managingOfferer, type=LocationType.OFFER_LOCATION
        ),
    )
    offer2 = OfferFactory(venue=venue2, offererAddress=offer1.offererAddress)
    offer3 = CollectiveOfferFactory(
        venue=venue2,
        offererAddress=offer1.offererAddress,
        locationType=educational_models.CollectiveLocationType.ADDRESS,
    )
    offer4 = CollectiveOfferTemplateFactory(
        venue=venue2,
        offererAddress=offer1.offererAddress,
        locationType=educational_models.CollectiveLocationType.ADDRESS,
    )
    from pcapi.scripts.check_offer_location_venueid.main import main

    main(is_dry=False)

    assert offer2.offererAddress.venueId == offer2.venueId
    assert offer2.offererAddress != offer1.venueId
    assert offer3.offererAddress.venueId == offer2.venueId
    assert offer3.offererAddress != offer1.venueId
    assert offer4.offererAddress.venueId == offer2.venueId
    assert offer4.offererAddress != offer1.venueId
    assert offer1.offererAddress.venueId == offer1.venueId


def test_does_not_check_when_only_one_venue():
    venue1 = VenueFactory()
    offer1 = OfferFactory(
        venue=venue1,
        offererAddress=OfferLocationFactory(
            venue=venue1, offerer=venue1.managingOfferer, type=LocationType.OFFER_LOCATION
        ),
    )
    from pcapi.scripts.check_offer_location_venueid.main import main

    main(is_dry=False)

    assert offer1.offererAddress.venueId == offer1.venueId
