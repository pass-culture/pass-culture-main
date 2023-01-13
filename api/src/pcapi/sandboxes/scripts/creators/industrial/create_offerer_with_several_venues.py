import logging

from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory


logger = logging.getLogger(__name__)


def create_offerer_with_several_venues() -> None:
    user_offerer = UserOffererFactory(offerer__name="Offerer avec plusieurs lieux")
    VenueFactory(
        name="Lieu de l'offerer avec plusieurs lieux 1",
        managingOfferer=user_offerer.offerer,
    )
    VenueFactory(
        name="Lieu de l'offerer avec plusieurs lieux 2",
        managingOfferer=user_offerer.offerer,
    )
    VenueFactory(
        name="Lieu de l'offerer avec plusieurs lieux 3",
        managingOfferer=user_offerer.offerer,
    )
    # offerers have always a virtual venue so we have to create one to match reality
    VirtualVenueFactory(name="Lieu virutel de l'offerer avec plusieurs lieux ", managingOfferer=user_offerer.offerer)

    logger.info("create_offerer with several venues")
