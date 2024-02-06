from dataclasses import dataclass
import logging

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.repository import repository


logger = logging.getLogger(__name__)


# Declare locations in various timezones: metropolitan France
# (UTC+1/+2), Guyane (UTC-3) and Wallis-et-Futuna (UTC+12).
@dataclass
class Location:
    address: str
    city: str
    latitude: float
    longitude: float
    postalCode: str


def create_E2E_offerer() -> dict[str, Offerer]:
    logger.info("create_E2E_offerer")

    # add a real offerer just for the inscription/validation API
    real_siren = "784340093"
    print("creating offerer 1")
    offerer = offerers_factories.OffererFactory(
        address="LIEU DIT CARTOUCHERIE",
        city="Paris 12",
        name="THEATRE DU SOLEIL",
        postalCode="75012",
        siren=real_siren,
    )

    repository.save(offerer)

    # offerer_location = (
    #     Location(address="Rue des Poilus", city="Drancy", latitude=48.928099, longitude=2.460249, postalCode="93700"),
    # )

    # offerer_name = "{} lat:{} lon:{}".format(222222222, offerer_location.latitude, offerer_location.longitude)

    # offerer = offerers_factories.OffererFactory(
    #     address=offerer_location.address.upper(),
    #     city=offerer_location.city,
    #     name="Herbert Marcuse Entreprise",
    #     postalCode=offerer_location.postalCode,
    #     siren=str(222222222),
    # )

    # objects_to_save = list(offerers_by_name.values())

    # repository.save(*objects_to_save)

    # logger.info("created %d offerers", len(offerers_by_name))
    return offerer
