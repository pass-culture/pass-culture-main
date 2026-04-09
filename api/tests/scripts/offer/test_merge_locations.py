import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveLocationType
from pcapi.core.offerers.factories import OfferLocationFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import OfferFactory


pytestmark = pytest.mark.usefixtures("db_session")


def test_merge_offer_locations_with_null_label_into_labelled_one() -> None:
    venue = VenueFactory(publicName="toto")
    offerer_address_1 = OfferLocationFactory(venue=venue, label=None, address=venue.offererAddress.address)
    offerer_address_2 = OfferLocationFactory(venue=venue, label=venue.publicName, address=venue.offererAddress.address)
    offer1 = OfferFactory(venue=venue, offererAddress=offerer_address_1)
    offer2 = OfferFactory(venue=venue, offererAddress=offerer_address_2)
    offer3 = CollectiveOfferFactory(
        venue=venue, offererAddress=offerer_address_2, locationType=CollectiveLocationType.ADDRESS
    )
    offer4 = CollectiveOfferTemplateFactory(
        venue=venue, offererAddress=offerer_address_2, locationType=CollectiveLocationType.ADDRESS
    )

    from pcapi.scripts.merge_offer_locations_with_null_label_into_labelled_one.main import main_func

    main_func(apply=False)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId != offerer_address_1.id
    assert offer3.offererAddressId != offerer_address_1.id
    assert offer4.offererAddressId != offerer_address_1.id

    main_func(apply=True)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId == offerer_address_1.id
    assert offer3.offererAddressId == offerer_address_1.id
    assert offer4.offererAddressId == offerer_address_1.id


def test_no_merge_if_label_not_venue_publicname() -> None:
    venue = VenueFactory(publicName="toto")
    offerer_address_1 = OfferLocationFactory(venue=venue, label=None, address=venue.offererAddress.address)
    offerer_address_2 = OfferLocationFactory(venue=venue, label="Awesome Cat", address=venue.offererAddress.address)
    offer1 = OfferFactory(venue=venue, offererAddress=offerer_address_1)
    offer2 = OfferFactory(venue=venue, offererAddress=offerer_address_2)

    from pcapi.scripts.merge_offer_locations_with_null_label_into_labelled_one.main import main_func

    main_func(apply=True)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId == offerer_address_2.id


def test_no_merge_if_not_venue_address() -> None:
    venue = VenueFactory(publicName="toto")
    offerer_address_1 = OfferLocationFactory(venue=venue, label=None, address=venue.offererAddress.address)
    offerer_address_2 = OfferLocationFactory(venue=venue, label=venue.publicName, address=venue.offererAddress.address)
    offerer_address_3 = OfferLocationFactory(venue=venue, label=None)
    offerer_address_4 = OfferLocationFactory(venue=venue, label=venue.publicName)
    offer1 = OfferFactory(venue=venue, offererAddress=offerer_address_1)
    offer2 = OfferFactory(venue=venue, offererAddress=offerer_address_2)
    offer3 = OfferFactory(venue=venue, offererAddress=offerer_address_3)
    offer4 = OfferFactory(venue=venue, offererAddress=offerer_address_4)

    from pcapi.scripts.merge_offer_locations_with_null_label_into_labelled_one.main import main_func

    main_func(apply=True)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId == offerer_address_1.id
    assert offer3.offererAddressId == offerer_address_3.id
    assert offer4.offererAddressId == offerer_address_4.id


def test_no_merge_if_not_same_venue() -> None:
    venue1 = VenueFactory(publicName="toto")
    venue2 = VenueFactory(publicName="toto")
    offerer_address_1 = OfferLocationFactory(
        venue=venue1, label=venue1.publicName, address=venue1.offererAddress.address
    )
    offerer_address_2 = OfferLocationFactory(
        venue=venue2, label=venue2.publicName, address=venue1.offererAddress.address
    )
    offer1 = OfferFactory(venue=venue1, offererAddress=offerer_address_1)
    offer2 = OfferFactory(venue=venue2, offererAddress=offerer_address_2)

    from pcapi.scripts.merge_offer_locations_with_null_label_into_labelled_one.main import main_func

    main_func(apply=True)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId == offerer_address_2.id


def test_merge_offer_locations_batch() -> None:
    venue = VenueFactory(publicName="toto")
    offerer_address_1 = OfferLocationFactory(venue=venue, label=None, address=venue.offererAddress.address)
    offerer_address_2 = OfferLocationFactory(venue=venue, label=venue.publicName, address=venue.offererAddress.address)
    offer1 = OfferFactory(venue=venue, offererAddress=offerer_address_1)
    offer2 = OfferFactory(venue=venue, offererAddress=offerer_address_2)
    for _ in range(1000):
        OfferFactory(venue=venue, offererAddress=offerer_address_1)

    from pcapi.scripts.merge_offer_locations_with_null_label_into_labelled_one.main import main_func

    main_func(apply=False)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId != offerer_address_1.id

    main_func(apply=True)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId == offerer_address_1.id


def test_merge_offer_locations_specific_location() -> None:
    venue = VenueFactory(publicName="toto")
    offerer_address_1 = OfferLocationFactory(venue=venue, label=None, address=venue.offererAddress.address)
    offerer_address_2 = OfferLocationFactory(venue=venue, label=venue.publicName, address=venue.offererAddress.address)
    offer1 = OfferFactory(venue=venue, offererAddress=offerer_address_1)
    offer2 = OfferFactory(venue=venue, offererAddress=offerer_address_2)

    from pcapi.scripts.merge_offer_locations_with_null_label_into_labelled_one.main import handle_specific_locations

    handle_specific_locations(apply=False, venueId=venue.id, addressId=venue.offererAddress.address.id)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId != offerer_address_1.id

    handle_specific_locations(apply=True, venueId=venue.id, addressId=venue.offererAddress.address.id)

    assert offer1.offererAddressId == offerer_address_1.id
    assert offer2.offererAddressId == offerer_address_1.id
