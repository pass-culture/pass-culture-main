from datetime import datetime
from datetime import timedelta
import itertools
import logging
import uuid

import pcapi.core.bookings.conf as bookings_conf
from pcapi.core.payments.api import create_deposit
from pcapi.model_creators.generic_creators import create_user
from pcapi.repository import repository


logger = logging.getLogger(__name__)


DEPARTEMENT_CODES = ["93", "97"]
WEBAPP_TAGS = [
    "has-signed-up",
    "has-filled-cultural-survey",
    "has-booked-activation",
    "has-confirmed-activation",
    "has-booked-some",
    "has-booked-some-but-deposit-expired",
    "has-no-more-money",
]
DEPOSIT_VERSIONS = bookings_conf.LIMIT_CONFIGURATIONS.keys()


def create_industrial_webapp_users():
    young_users = create_industrial_webapp_young_users()
    general_public_users = create_industrial_webapp_general_public_users()

    webapp_users = dict(young_users, **general_public_users)
    return webapp_users


def create_industrial_webapp_young_users():
    logger.info("create_industrial_webapp_young_users")

    users_by_name = {}
    deposit_versions = {}

    validation_prefix, validation_suffix = "AZERTY", 123
    validation_suffix += 1

    variants = itertools.product(DEPARTEMENT_CODES, WEBAPP_TAGS, DEPOSIT_VERSIONS)

    for departement_code, tag, deposit_version in variants:
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        if tag == "has-signed-up":
            reset_password_token = "{}{}".format(validation_prefix, validation_suffix)
            validation_suffix += 1
        else:
            reset_password_token = None

        cultural_survey_id = None
        needs_to_fill_cultural_survey = False
        has_seen_tutorials = True

        if tag == "has-filled-cultural-survey":
            has_seen_tutorials = False

        if tag == "has-signed-up":
            cultural_survey_id = uuid.uuid4()
            needs_to_fill_cultural_survey = True
            has_seen_tutorials = False

        email = f"pctest.jeune{departement_code}.{tag}.v{deposit_version}@example.com"

        user = create_user(
            cultural_survey_id=cultural_survey_id,
            departement_code=str(departement_code),
            email=email,
            first_name="PC Test Jeune",
            date_of_birth=datetime(2003, 1, 1),
            has_seen_tutorials=has_seen_tutorials,
            last_name=f"{departement_code} {short_tag} {deposit_version}",
            needs_to_fill_cultural_survey=needs_to_fill_cultural_survey,
            postal_code="{}100".format(departement_code),
            public_name=f"PC Test Jeune {departement_code} {short_tag} {deposit_version}",
            reset_password_token=reset_password_token,
            reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24),
        )
        user_key = f"jeune{departement_code} {tag} v{deposit_version}"
        users_by_name[user_key] = user
        deposit_versions[user_key] = deposit_version

    repository.save(*users_by_name.values())
    for user_key, user in users_by_name.items():
        # FIXME (asaunier, 2021-01-27): There are only 2 accounts in production where beneficiaries have no deposit
        #  including one passculture account.
        if not ("has-signed-up" in user_key or "has-booked-activation" in user_key):
            deposit = create_deposit(
                user,
                deposit_source="sandbox",
                version=deposit_versions[user_key],
            )
            repository.save(deposit)

    logger.info("created %d young users", len(users_by_name))

    return users_by_name


AGE_TAGS = ["age-more-than-18yo", "age-less-than-18yo", "age-18yo"]


def create_industrial_webapp_general_public_users():
    logger.info("create_industrial_webapp_general_public_users")

    users_by_name = {}
    deposit_versions = {}

    variants = itertools.product(AGE_TAGS, DEPOSIT_VERSIONS)

    for age, deposit_version in variants:
        short_age = "".join([chunk[0].upper() for chunk in age.split("-")])
        email = f"pctest.grandpublic.{age}.v{deposit_version}@example.com"
        departement_code = 39
        today = datetime.today()
        date_of_birth = today - timedelta(18 * 366)

        if age == "age-more-than-18yo":
            date_of_birth = today - timedelta(20 * 366)

        if age == "age-less-than-18yo":
            date_of_birth = today - timedelta(16 * 366)

        user = create_user(
            cultural_survey_id=None,
            departement_code=str(departement_code),
            email=email,
            first_name="PC Test Grand Public",
            date_of_birth=date_of_birth,
            has_seen_tutorials=False,
            is_beneficiary=False,
            last_name=f"{short_age} {deposit_version}",
            needs_to_fill_cultural_survey=True,
            postal_code="{}100".format(departement_code),
            public_name=f"PC Test Grand Public {short_age} {deposit_version}",
            reset_password_token=None,
            reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24),
        )
        user_key = f"grandpublic{age}v{deposit_version}"
        users_by_name[user_key] = user
        deposit_versions[user_key] = deposit_version

    repository.save(*users_by_name.values())
    logger.info("created %d general public users", len(users_by_name))

    return users_by_name
