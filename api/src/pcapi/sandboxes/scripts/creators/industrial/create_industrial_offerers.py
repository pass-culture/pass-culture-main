from dataclasses import dataclass
import logging

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.models import db
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.educational_siren_mocks import MOCK_ADAGE_ELIGIBLE_SIREN
from pcapi.sandboxes.scripts.mocks.offerer_mocks import MOCK_NAMES


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


OFFERER_LOCATIONS = [
    Location(address="Rue des Poilus", city="Drancy", latitude=48.928099, longitude=2.460249, postalCode="93700"),
    Location(address="Rue de Nieuport", city="Drancy", latitude=48.91683, longitude=2.438839, postalCode="93700"),
    Location(address="Rue Francois Rude", city="Drancy", latitude=48.926432, longitude=2.432279, postalCode="93700"),
    Location(address="Rue Pollet", city="Aulnay-sous-Bois", latitude=48.945379, longitude=2.502902, postalCode="93600"),
    Location(
        address="Rue de Pimodan", city="Aulnay-sous-Bois", latitude=48.926299, longitude=2.490079, postalCode="93600"
    ),
    Location(
        address="Rue de Pologne", city="Aulnay-sous-Bois", latitude=48.940826, longitude=2.479869, postalCode="93600"
    ),
    Location(address="Rue Pasteur", city="Kourou", latitude=5.170549, longitude=-52.649077, postalCode="97310"),
    Location(address="Rue de Cali", city="Kourou", latitude=5.158387, longitude=-52.637413, postalCode="97310"),
    Location(address="Rue de Paris", city="Kourou", latitude=5.161934, longitude=-52.639804, postalCode="97310"),
    Location(address="Rue Panacoco", city="Cayenne", latitude=4.916571, longitude=-52.319168, postalCode="97300"),
    Location(address="Rue Aristote", city="Cayenne", latitude=4.934074, longitude=-52.297176, postalCode="97300"),
    Location(address="Cayenne", city="Cayenne", latitude=4.925246, longitude=-52.311586, postalCode="97300"),
    Location(
        address="RT3", city="Matāʻutu", latitude=-13.282339262455315, longitude=-176.1771062948854, postalCode="98600"
    ),
]


def create_industrial_offerers() -> dict[str, Offerer]:
    logger.info("create_industrial_offerers")

    offerers_by_name = {}

    # add a real offerer just for the inscription/validation API
    real_siren = "784340093"
    if not db.session.query(db.session.query(Offerer.id).filter(Offerer.siren == real_siren).exists()):
        print("creating offerer 1")
        offerer_name = "784340093 lat:48.8 lon:1.48"
        offerer = offerers_factories.OffererFactory.create(
            street="LIEU DIT CARTOUCHERIE",
            city="Paris 12",
            name="THEATRE DU SOLEIL",
            postalCode="75012",
            siren=real_siren,
        )
        offerers_by_name[offerer_name] = offerer

    # loop on locations to create offerers
    incremented_siren = 222222222
    starting_index = 0

    for location_index, location in enumerate(OFFERER_LOCATIONS):
        create_educational_offerer = location_index == 0

        mock_index = location_index % len(MOCK_NAMES) + starting_index

        offerer_name = "{} lat:{} lon:{}".format(incremented_siren, location.latitude, location.longitude)

        offerer = offerers_factories.OffererFactory.create(
            street=location.address.upper(),
            city=location.city,
            name=MOCK_NAMES[mock_index],
            postalCode=location.postalCode,
            siren=str(incremented_siren),
        )

        if create_educational_offerer:
            offerer.siren = str(MOCK_ADAGE_ELIGIBLE_SIREN)
            offerers_factories.VenueFactory.create(
                managingOfferer=offerer,
                street=offerer.street,
                bookingEmail="fake@email.com",
                city=offerer.city,
                comment="Salle de cinéma",
                name=offerer.name + " - Salle 1",
                postalCode=offerer.postalCode,
                siret="88145723811111",
                venueTypeCode=VenueTypeCode.MOVIE,
            )

        offerers_by_name[offerer_name] = offerer

        incremented_siren += 1

    objects_to_save = list(offerers_by_name.values())

    repository.save(*objects_to_save)

    logger.info("created %d offerers", len(offerers_by_name))
    return offerers_by_name
