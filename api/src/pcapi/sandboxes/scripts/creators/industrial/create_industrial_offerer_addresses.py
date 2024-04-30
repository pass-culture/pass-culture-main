import logging

from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories


logger = logging.getLogger(__name__)


def create_industrial_offerer_addresses() -> None:
    logger.info("create_industrial_offerer_addresses")
    offerer_with_addresses = offerers_factories.OffererFactory(name="2 - Structure avec plusieurs adresses")
    bercy_address = geography_factories.AddressFactory(
        street="8 Boulevard de Bercy",
        postalCode="75012",
        city="Paris",
        latitude=48.83925,
        longitude=2.3778,
        inseeCode="75112",
        banId="75112_0877_00008",
    )
    offerers_factories.OffererAddressFactory(label="Accor Arena", address=bercy_address, offerer=offerer_with_addresses)
    grevin_address = geography_factories.AddressFactory(
        street="10 Boulevard Montmartre",
        postalCode="75009",
        city="Paris",
        latitude=48.87185,
        longitude=2.342,
        inseeCode="75109",
        banId="75109_6510_00010",
    )
    offerers_factories.OffererAddressFactory(
        label="Musée Grévin", address=grevin_address, offerer=offerer_with_addresses
    )
    lacigale_address = geography_factories.AddressFactory(
        street="120 Boulevard Marguerite de Rochechouart",
        postalCode="75018",
        city="Paris",
        latitude=48.88235,
        longitude=2.3402,
        inseeCode="75118",
        banId="75118_8288_00120",
    )
    offerers_factories.OffererAddressFactory(
        label="La cigale", address=lacigale_address, offerer=offerer_with_addresses
    )

    offerer_with_one_address = offerers_factories.OffererFactory(name="2 - Structure avec une adresse")
    offerers_factories.OffererAddressFactory(
        label="Bercy Accor Arena", address=bercy_address, offerer=offerer_with_one_address
    )
