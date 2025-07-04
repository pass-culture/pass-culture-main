import logging

from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_offerer_addresses() -> None:
    logger.info("create_industrial_offerer_addresses")
    offerer_with_addresses = offerers_factories.OffererFactory.create(name="2 - Structure avec plusieurs adresses")
    bercy_address = geography_factories.AddressFactory.create(
        street="8 Boulevard de Bercy",
        postalCode="75012",
        city="Paris",
        latitude=48.83925,
        longitude=2.3778,
        inseeCode="75112",
        banId="75112_0877_00008",
    )
    grevin_address = geography_factories.AddressFactory.create(
        street="10 Boulevard Montmartre",
        postalCode="75009",
        city="Paris",
        latitude=48.87185,
        longitude=2.342,
        inseeCode="75109",
        banId="75109_6510_00010",
    )
    lacigale_address = geography_factories.AddressFactory.create(
        street="120 Boulevard Marguerite de Rochechouart",
        postalCode="75018",
        city="Paris",
        latitude=48.88235,
        longitude=2.3402,
        inseeCode="75118",
        banId="75118_8288_00120",
    )
    offerer_adresses = [
        offerers_factories.OffererAddressFactory.create(
            label="Accor Arena", address=bercy_address, offerer=offerer_with_addresses
        ),
        offerers_factories.OffererAddressFactory.create(
            label="Musée Grévin", address=grevin_address, offerer=offerer_with_addresses
        ),
        offerers_factories.OffererAddressFactory.create(
            label="La cigale", address=lacigale_address, offerer=offerer_with_addresses
        ),
    ]
    venue_with_addresses = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_addresses, name="Lieu de la structure avec plusieurs adresses"
    )
    for offerer_address in offerer_adresses:
        offers_factories.OfferFactory.create(
            venue=venue_with_addresses,
            name=f"Offre localisée à {offerer_address.label}",
            offererAddress=offerer_address,
        )

    offerer_with_one_address = offerers_factories.OffererFactory.create(name="2 - Structure avec une adresse")
    offerer_address_one = offerers_factories.OffererAddressFactory.create(
        label="Bercy Accor Arena", address=bercy_address, offerer=offerer_with_one_address
    )
    venue_with_one_address = offerers_factories.VenueFactory.create(
        managingOfferer=offerer_with_one_address, name="Lieu de la structure avec une adresse"
    )
    offers_factories.OfferFactory.create(
        venue=venue_with_one_address, name="Offre avec une adresse", offererAddress=offerer_address_one
    )
