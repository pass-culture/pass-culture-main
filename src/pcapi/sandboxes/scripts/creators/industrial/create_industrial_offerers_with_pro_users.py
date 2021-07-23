from datetime import datetime
from datetime import timedelta
import logging

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository
from pcapi.repository.offerer_queries import check_if_siren_already_exists
from pcapi.sandboxes.scripts.mocks.offerer_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_DOMAINS
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES
from pcapi.sandboxes.scripts.utils.helpers import get_email
from pcapi.sandboxes.scripts.utils.locations import OFFERER_PLACES
from pcapi.sandboxes.scripts.utils.locations import create_locations_from_places
from pcapi.sandboxes.scripts.utils.select import pick_every


logger = logging.getLogger(__name__)


ATTACHED_PRO_USERS_COUNT = 2
VALIDATED_OFFERERS_REMOVE_MODULO = 5
VALIDATED_USER_OFFERER_REMOVE_MODULO = 2
VALIDATED_USER_REMOVE_MODULO = 4
OFFERERS_WITH_IBAN_REMOVE_MODULO = 2
USERS_WITH_SEVERAL_OFFERERS_PICK_MODULO = 2
OFFERERS_WITH_THREE_ATTACHED_USERS_PICK_MODULO = 2


def create_industrial_offerers_with_pro_users():
    logger.info("create_industrial_offerers_with_pro_users")

    locations = create_locations_from_places(OFFERER_PLACES, max_location_per_place=3)

    offerers_by_name = {}
    users_by_name = {}
    user_offerers_by_name = {}

    user_index = 0
    user_validation_prefix, user_validation_suffix = "AZERTY", 123

    # add a real offerer just for the inscription/validation API
    real_siren = "784340093"
    if not check_if_siren_already_exists(real_siren):
        offerer_name = "784340093 lat:48.8 lon:1.48"
        offerer = create_offerer(
            address="LIEU DIT CARTOUCHERIE",
            city="Paris 12",
            name="THEATRE DU SOLEIL",
            postal_code="75012",
            siren=real_siren,
        )
        offerers_by_name[offerer_name] = offerer

        departement_code = 75

        domain = MOCK_DOMAINS[user_index]
        first_name = MOCK_FIRST_NAMES[user_index]
        last_name = MOCK_LAST_NAMES[user_index]
        email = get_email(first_name, last_name, domain)
        user_name = "{} {}".format(first_name, last_name)
        user = users_factories.UserFactory(
            resetPasswordTokenValidityLimit=datetime.utcnow() + timedelta(hours=24),
            departementCode=str(departement_code),
            email=email,
            firstName=first_name,
            lastName=last_name,
            postalCode="{}100".format(departement_code),
            phoneNumber="01 00 00 00 00",
            publicName="{} {}".format(first_name, last_name),
            validationToken="{}{}".format(user_validation_prefix, user_validation_suffix),
        )
        users_by_name[user_name] = user
        user_index += 1
        user_validation_suffix += 1

        user_offerers_by_name["{} / {}".format(user_name, offerer_name)] = create_user_offerer(
            offerer=offerer,
            user=user,
        )

    # loop on locations to create offerers and associated users
    incremented_siren = 222222222
    starting_index = 0
    iban_prefix = "FR7630001007941234567890185"
    bic_prefix, bic_suffix = "QSDFGH8Z", 555
    user_offerer_validation_prefix, user_offerer_validation_suffix = "AZERTY", 123
    application_id_prefix = "23"

    for (location_index, location) in enumerate(locations):

        mock_index = location_index % len(MOCK_NAMES) + starting_index

        departement_code = location["postalCode"][:2]

        offerer_name = "{} lat:{} lon:{}".format(incremented_siren, location["latitude"], location["longitude"])

        offerer = create_offerer(
            address=location["address"].upper(),
            city=location["city"],
            name=MOCK_NAMES[mock_index],
            postal_code=location["postalCode"],
            siren=str(incremented_siren),
        )

        # create every OFFERERS_WITH_IBAN_REMOVE_MODULO an offerer with no iban
        if location_index % OFFERERS_WITH_IBAN_REMOVE_MODULO:
            create_bank_information(
                bic=bic_prefix + str(bic_suffix),
                iban=iban_prefix,
                offerer=offerer,
                application_id=application_id_prefix + str(location_index),
            )

        offerers_by_name[offerer_name] = offerer

        incremented_siren += 1
        bic_suffix += 1

        # special user that signed up with this offerer
        domain = MOCK_DOMAINS[user_index % len(MOCK_DOMAINS)]
        first_name = MOCK_FIRST_NAMES[user_index % len(MOCK_FIRST_NAMES)]
        last_name = MOCK_LAST_NAMES[user_index % len(MOCK_LAST_NAMES)]
        email = get_email(first_name, last_name, domain)
        user_name = "{} {}".format(first_name, last_name)

        if location_index % VALIDATED_USER_REMOVE_MODULO:
            user_validation_token = None
        else:
            user_validation_token = "{}{}".format(user_validation_prefix, user_validation_suffix)

        if location_index % VALIDATED_OFFERERS_REMOVE_MODULO == 0:
            offerer.generate_validation_token()

        user = users_factories.UserFactory(
            resetPasswordTokenValidityLimit=datetime.utcnow() + timedelta(hours=24),
            departementCode=str(departement_code),
            email=email,
            firstName=first_name,
            lastName=last_name,
            postalCode="{}100".format(departement_code),
            phoneNumber="01 00 00 00 00",
            publicName="{} {}".format(first_name, last_name),
            validationToken=user_validation_token,
        )
        users_by_name[user_name] = user
        user_validation_suffix += 1
        user_index += 1

        # user_offerer with None as validation token
        # because this user has created the offerer
        user_offerers_by_name["{} / {}".format(user_name, offerer_name)] = create_user_offerer(
            offerer=offerer, user=user
        )

        # create also users that are attached to this offerer
        for _i in range(ATTACHED_PRO_USERS_COUNT):
            # special user that signed up with this offerer
            domain = MOCK_DOMAINS[user_index % len(MOCK_DOMAINS)]
            first_name = MOCK_FIRST_NAMES[user_index % len(MOCK_FIRST_NAMES)]
            last_name = MOCK_LAST_NAMES[user_index % len(MOCK_LAST_NAMES)]
            email = get_email(first_name, last_name, domain)
            user_name = "{} {}".format(first_name, last_name)
            if location_index % VALIDATED_USER_REMOVE_MODULO:
                user_validation_token = None
            else:
                user_validation_token = "{}{}".format(user_validation_prefix, user_validation_suffix)
            user_name = "{} {}".format(first_name, last_name)
            user = users_factories.UserFactory(
                resetPasswordTokenValidityLimit=datetime.utcnow() + timedelta(hours=24),
                departementCode=str(departement_code),
                email=email,
                firstName=first_name,
                lastName=last_name,
                postalCode="{}100".format(departement_code),
                phoneNumber="01 00 00 00 00",
                publicName="{} {}".format(first_name, last_name),
                validationToken=user_validation_token,
            )
            users_by_name[user_name] = user
            user_index += 1
            user_validation_suffix += 1

            if location_index % VALIDATED_USER_OFFERER_REMOVE_MODULO:
                user_offerer_validation_token = None
            else:
                user_offerer_validation_token = "{}{}".format(
                    user_offerer_validation_prefix, user_offerer_validation_suffix
                )
            user_offerers_by_name["{} / {}".format(user_name, offerer_name)] = create_user_offerer(
                offerer=offerer, user=user, validation_token=user_offerer_validation_token
            )
            user_offerer_validation_suffix += 1

    # loop on users to make some of them with several attached offerers
    user_items_with_several_offerers = pick_every(users_by_name.items(), USERS_WITH_SEVERAL_OFFERERS_PICK_MODULO)
    user_offerer_index = 0

    for (user_name, user) in user_items_with_several_offerers:
        offerer_items_with_three_attached_users = pick_every(
            offerers_by_name.items(), OFFERERS_WITH_THREE_ATTACHED_USERS_PICK_MODULO
        )
        for (offerer_name, offerer) in offerer_items_with_three_attached_users:
            user_offerer_name = "{} / {}".format(user_name, offerer_name)

            if user_offerer_name in user_offerers_by_name:
                continue

            if offerer.isValidated and user_offerer_index % VALIDATED_USER_OFFERER_REMOVE_MODULO == 0:
                user_offerer_validation_token = None
            else:
                user_offerer_validation_token = "{}{}".format(
                    user_offerer_validation_prefix, user_offerer_validation_suffix
                )
            user_offerers_by_name["{} / {}".format(user_name, offerer_name)] = create_user_offerer(
                offerer=offerer, user=user, validation_token=user_offerer_validation_token
            )
            user_offerer_index += 1
            user_offerer_validation_suffix += 1

    objects_to_save = (
        list(offerers_by_name.values()) + list(users_by_name.values()) + list(user_offerers_by_name.values())
    )

    repository.save(*objects_to_save)

    logger.info("created %d offerers with pro users", len(offerers_by_name))

    return (offerers_by_name, users_by_name)
