from dataclasses import dataclass
import logging

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.offerer_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_DOMAINS
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES
from pcapi.sandboxes.scripts.utils.helpers import get_email


logger = logging.getLogger(__name__)


ATTACHED_PRO_USERS_COUNT = 2


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
    Location(address="Rue des Poilus DATA", city="Drancy", latitude=48.928099, longitude=2.460249, postalCode="93700"),
    Location(address="Rue de Nieuport DATA", city="Drancy", latitude=48.91683, longitude=2.438839, postalCode="93700"),
    Location(
        address="Rue Francois Rude DATA", city="Drancy", latitude=48.926432, longitude=2.432279, postalCode="93700"
    ),
    Location(
        address="Rue Pollet DATA", city="Aulnay-sous-Bois", latitude=48.945379, longitude=2.502902, postalCode="93600"
    ),
    Location(
        address="Rue de Pimodan DATA",
        city="Aulnay-sous-Bois",
        latitude=48.926299,
        longitude=2.490079,
        postalCode="93600",
    ),
    Location(
        address="Rue de Pologne DATA",
        city="Aulnay-sous-Bois",
        latitude=48.940826,
        longitude=2.479869,
        postalCode="93600",
    ),
    Location(address="Rue Pasteur DATA", city="Brive", latitude=45.1593976, longitude=1.5336677, postalCode="19100"),
    Location(address="Rue de Cali DATA", city="Brive", latitude=45.1593976, longitude=1.5336677, postalCode="19100"),
    Location(address="Rue de Paris DATA", city="Brive", latitude=45.1593976, longitude=1.5336677, postalCode="19100"),
    Location(address="Rue Panacoco DATA", city="Lille", latitude=50.631108, longitude=3.0715963, postalCode="59000"),
    Location(address="Rue Aristote DATA", city="Lille", latitude=50.631108, longitude=3.0715963, postalCode="59000"),
    Location(address="Cayenne DATA", city="Lille", latitude=50.631108, longitude=3.0715963, postalCode="59000"),
    Location(address="RT3 DATA", city="Lille", latitude=50.631108, longitude=3.0715963, postalCode="59000"),
]


def create_data_offerers_with_pro_users() -> tuple[dict[str, Offerer], dict[str, User]]:
    logger.info("create_data_offerers_with_pro_users_data")

    offerers_by_name = {}
    users_by_name = {}
    user_offerers_by_name = {}

    user_index = 0

    # loop on locations to create offerers and associated users
    incremented_siren = 555555555
    starting_index = 0

    for location_index, location in enumerate(OFFERER_LOCATIONS):
        mock_index = location_index % len(MOCK_NAMES) + starting_index

        departement_code = location.postalCode[:2]

        offerer_name = f"{incremented_siren} lat:{location.latitude} lon:{location.longitude}"

        offerer = offerers_factories.OffererFactory(
            street=location.address.upper(),
            city=location.city,
            name=MOCK_NAMES[mock_index],
            postalCode=location.postalCode,
            siren=str(incremented_siren),
        )

        offerers_by_name[offerer_name] = offerer

        incremented_siren += 1

        # special user that signed up with this offerer
        domain = MOCK_DOMAINS[user_index % len(MOCK_DOMAINS)]
        first_name = MOCK_FIRST_NAMES[user_index % len(MOCK_FIRST_NAMES)]
        last_name = MOCK_LAST_NAMES[user_index % len(MOCK_LAST_NAMES)]
        email = get_email(f"{first_name}_Data", last_name, domain)
        user_name = f"{first_name} {last_name}"
        offerer.validationStatus = ValidationStatus.VALIDATED
        pro = users_factories.ProFactory(
            departementCode=departement_code,
            email=email,
            firstName=first_name,
            lastName=last_name,
            postalCode=f"{departement_code}100",
            phoneNumber="+33100000001",
        )
        users_factories.UserProNewNavStateFactory(user=pro)
        users_by_name[user_name] = pro
        user_index += 1

        # user_offerer with None as validation token
        # because this user has created the offerer
        user_offerers_by_name[f"{user_name} / {offerer_name}"] = offerers_factories.UserOffererFactory(
            offerer=offerer,
            user=pro,
        )

        # create also users that are attached to this offerer
        for _i in range(ATTACHED_PRO_USERS_COUNT):
            # special user that signed up with this offerer
            domain = MOCK_DOMAINS[user_index % len(MOCK_DOMAINS)]
            first_name = MOCK_FIRST_NAMES[user_index % len(MOCK_FIRST_NAMES)]
            last_name = MOCK_LAST_NAMES[user_index % len(MOCK_LAST_NAMES)]
            email = get_email(f"{first_name}_data", last_name, domain)
            user_name = f"{first_name} {last_name} DATA"
            pro = users_factories.ProFactory(
                departementCode=departement_code,
                email=email,
                firstName=first_name,
                lastName=last_name,
                postalCode=f"{departement_code}100",
                phoneNumber="+33100000002",
            )
            users_factories.UserProNewNavStateFactory(user=pro)
            users_by_name[user_name] = pro
            user_index += 1

            user_offerers_by_name[f"{user_name} / {offerer_name}"] = offerers_factories.UserOffererFactory(
                offerer=offerer,
                user=pro,
                validationStatus=ValidationStatus.VALIDATED,
            )

    objects_to_save = list(offerers_by_name.values()) + list(users_by_name.values())

    repository.save(*objects_to_save)

    logger.info("created %d offerers with pro users DATA", len(offerers_by_name))

    return offerers_by_name, users_by_name
