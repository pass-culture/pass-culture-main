import pytest

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.offerers.factories import OffererAddressFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import LocationType
from pcapi.core.offers.factories import OfferFactory


pytestmark = pytest.mark.usefixtures("db_session")


def test_basic(client):
    from pcapi.scripts.set_location_type_for_offers.main import main

    """on arrive a changer le type d'une localisation d'une offre sans affecter la locatlisation de la venue"""
    # venue1 = VenueFactory(offererAddress=VenueLocationFactory())
    venue1 = VenueFactory()
    venue1.offererAddress.venueId = venue1.id
    venue1.offererAddress.type = LocationType.VENUE_LOCATION
    offerer_with_offers = venue1.managingOfferer

    offer_indiv = OfferFactory(venue=venue1, offererAddress=OffererAddressFactory(offerer=offerer_with_offers))
    offer_collective = CollectiveOfferFactory(
        venue=venue1,
        locationType=educational_models.CollectiveLocationType.ADDRESS,
        offererAddress=OffererAddressFactory(offerer=offerer_with_offers),
    )
    offer_template = CollectiveOfferTemplateFactory(
        venue=venue1,
        locationType=educational_models.CollectiveLocationType.ADDRESS,
        offererAddress=OffererAddressFactory(offerer=offerer_with_offers),
    )

    assert offer_indiv.venueId == venue1.id
    assert offer_indiv.offererAddress.type is None
    assert offer_collective.offererAddress.type is None
    assert offer_template.offererAddress.type is None
    assert offer_indiv.offererAddress.venueId is None
    assert offer_collective.offererAddress.venueId is None
    assert offer_template.offererAddress.venueId is None
    assert offer_collective.locationType == educational_models.CollectiveLocationType.ADDRESS
    assert offer_template.locationType == educational_models.CollectiveLocationType.ADDRESS
    assert offer_indiv.offererAddress
    assert (
        offer_indiv.offererAddress != venue1.offererAddress
    )  # on prepare l'offre en verifiant qu'elle n'ait pas la meme oa que celle de la venue

    main(not_dry=True)

    assert offer_indiv.offererAddress.type == LocationType.OFFER_LOCATION
    assert offer_indiv.offererAddress.venueId == venue1.id
    assert offer_collective.offererAddress.type == LocationType.OFFER_LOCATION
    assert offer_collective.offererAddress.venueId == venue1.id
    assert offer_template.offererAddress.type == LocationType.OFFER_LOCATION
    assert offer_template.offererAddress.venueId == venue1.id
    assert (
        offer_indiv.offererAddress.type
        == offer_collective.offererAddress.type
        == offer_template.offererAddress.type
        == LocationType.OFFER_LOCATION
    )
    assert (
        offer_indiv.offererAddress.venueId
        == offer_collective.offererAddress.venueId
        == offer_template.offererAddress.venueId
        == venue1.id
    )
    assert venue1.offererAddress.type == LocationType.VENUE_LOCATION
    assert venue1.offererAddress.venueId == venue1.id


def test_multiple_venues(client):
    """2 venues pour 1 offerer, l'offre est associée a la bonne venue"""

    from pcapi.scripts.set_location_type_for_offers.main import main

    venue1 = VenueFactory()
    venue1.offererAddress.venueId = venue1.id
    venue1.offererAddress.type = LocationType.VENUE_LOCATION
    venue2 = VenueFactory(managingOffererId=venue1.managingOfferer.id)
    venue2.offererAddress.venueId = venue2.id
    venue2.offererAddress.type = LocationType.VENUE_LOCATION

    # venue1 = VenueFactory(offererAddress=VenueLocationFactory())
    # venue1.offererAddress.venueId = venue1.id
    # venue2 = VenueFactory(managingOffererId=venue1.managingOfferer.id, offererAddress=VenueLocationFactory())
    # venue2.offererAddress.venueId = venue2.id

    offerer_with_offers = venue1.managingOfferer

    offer_venue1 = OfferFactory(venue=venue2, offererAddress=OffererAddressFactory(offerer=offerer_with_offers))
    offer_venue1.offererAddress.venueId = None
    offer_venue1.offererAddress.type = None
    assert offer_venue1.offererAddress.type is None
    assert offer_venue1.offererAddress.venueId is None
    assert offer_venue1.offererAddress != venue1.offererAddress != venue2.offererAddress
    # on cree une offre attribuée a la venue2

    main(not_dry=True)

    assert offer_venue1.offererAddress.type == LocationType.OFFER_LOCATION
    assert offer_venue1.offererAddress.venueId == venue2.id
    assert venue1.offererAddress.type == LocationType.VENUE_LOCATION
    assert venue1.offererAddress.venueId == venue1.id
    # la localisation de l'offre a en venueId la venue2


def test_multiples_offers(client):
    from pcapi.scripts.set_location_type_for_offers.main import main

    """si plusieurs offres on le meme oa ils auront la venue de la 1ere offre trouvée"""
    # venue1 = VenueFactory(offererAddress=VenueLocationFactory())
    # venue1.offererAddress.venueId = venue1.id

    venue1 = VenueFactory()
    venue1.offererAddress.venueId = venue1.id
    venue1.offererAddress.type = LocationType.VENUE_LOCATION

    offer_venue1 = OfferFactory(venue=venue1, offererAddress=OffererAddressFactory())
    offer_venue2 = OfferFactory(venue=VenueFactory(), offererAddress=offer_venue1.offererAddress)
    offer_venue3 = OfferFactory(venue=VenueFactory(), offererAddress=offer_venue1.offererAddress)
    assert offer_venue2.offererAddress.type is None
    assert offer_venue3.offererAddress.venueId is None
    assert venue1.offererAddress.type is LocationType.VENUE_LOCATION
    assert venue1.offererAddress.venueId == venue1.id

    # on cree 3 offres attribuées 3 venues differentes avec la meme localisation

    main(not_dry=True)

    assert (
        offer_venue1.offererAddress.type
        == offer_venue2.offererAddress.type
        == offer_venue3.offererAddress.type
        == LocationType.OFFER_LOCATION
    )
    assert (
        offer_venue1.offererAddress.venueId
        == offer_venue2.offererAddress.venueId
        == offer_venue3.offererAddress.venueId
        == venue1.id
    )
    assert venue1.offererAddress.type == LocationType.VENUE_LOCATION
    assert venue1.offererAddress.venueId == venue1.id
    # les offres sont toutes attribuées a la venue1


def test_multiples_locations(client):
    from pcapi.scripts.set_location_type_for_offers.main import main

    """si oas identiques, la premiere gardée et la 2eme supprimée"""
    # venue1 = VenueFactory(offererAddress=VenueLocationFactory())
    # venue1.offererAddress.venueId = venue1.id

    venue1 = VenueFactory()
    venue1.offererAddress.venueId = venue1.id
    venue1.offererAddress.type = LocationType.VENUE_LOCATION

    offer_venue1 = OfferFactory(
        venue=venue1, offererAddress=OffererAddressFactory(offerer=venue1.managingOfferer, label=None)
    )
    offer_venue2 = OfferFactory(
        venue=venue1,
        offererAddress=OffererAddressFactory(
            address=offer_venue1.offererAddress.address, offerer=venue1.managingOfferer, label=None
        ),
    )
    assert offer_venue1.offererAddress.address == offer_venue2.offererAddress.address
    assert offer_venue1.offererAddress.offererId == offer_venue2.offererAddress.offererId
    assert offer_venue1.offererAddress.label == offer_venue2.offererAddress.label == None
    # assert offer_venue2.offererAddress.type is None
    assert venue1.offererAddress.type is LocationType.VENUE_LOCATION
    assert venue1.offererAddress.venueId == venue1.id

    main(not_dry=True)

    assert offer_venue1.offererAddress == offer_venue2.offererAddress

    assert venue1.offererAddress.type == LocationType.VENUE_LOCATION
    assert venue1.offererAddress.venueId == venue1.id
    # les offres sont toutes attribuées a la venue1
