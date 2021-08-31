from datetime import datetime
from datetime import timedelta
import itertools
import logging
import uuid

from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import TokenType


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
GRANT_18_DEPOSIT_VERSIONS = [1, 2]


def create_industrial_webapp_users():
    young_users = create_industrial_webapp_young_users()
    general_public_users = create_industrial_webapp_general_public_users()

    webapp_users = dict(young_users, **general_public_users)
    return webapp_users


def create_industrial_webapp_young_users():
    logger.info("create_industrial_webapp_young_users")

    users_by_name = {}

    validation_prefix, validation_suffix = "AZERTY", 123
    validation_suffix += 1

    variants = itertools.product(DEPARTEMENT_CODES, WEBAPP_TAGS, GRANT_18_DEPOSIT_VERSIONS)

    for index, (departement_code, tag, deposit_version) in enumerate(variants, start=0):
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

        if tag in ("has-signed-up", "has-booked-activation"):
            user = users_factories.UserFactory(
                culturalSurveyId=cultural_survey_id,
                departementCode=str(departement_code),
                email=email,
                phoneNumber=f"+336{index:0>8}",
                firstName="PC Test Jeune",
                dateOfBirth=datetime(2003, 1, 1),
                hasSeenTutorials=has_seen_tutorials,
                lastName=f"{departement_code} {short_tag} {deposit_version}",
                needsToFillCulturalSurvey=needs_to_fill_cultural_survey,
                postalCode="{}100".format(departement_code),
                publicName=f"PC Test Jeune {departement_code} {short_tag} {deposit_version}",
            )
        else:
            user = users_factories.BeneficiaryFactory(
                culturalSurveyId=cultural_survey_id,
                departementCode=str(departement_code),
                email=email,
                phoneNumber=f"+336{index:0>8}",
                firstName="PC Test Jeune",
                dateOfBirth=datetime(2003, 1, 1),
                hasSeenTutorials=has_seen_tutorials,
                lastName=f"{departement_code} {short_tag} {deposit_version}",
                needsToFillCulturalSurvey=needs_to_fill_cultural_survey,
                postalCode="{}100".format(departement_code),
                publicName=f"PC Test Jeune {departement_code} {short_tag} {deposit_version}",
                deposit__source="sandbox",
                deposit__version=deposit_version,
            )
        if reset_password_token:
            users_factories.TokenFactory(
                user=user,
                value=reset_password_token,
                expirationDate=datetime.utcnow() + timedelta(hours=24),
                type=TokenType.RESET_PASSWORD,
            )
        user_key = f"jeune{departement_code} {tag} v{deposit_version}"
        users_by_name[user_key] = user

    logger.info("created %d young users", len(users_by_name))

    return users_by_name


AGE_TAGS = ["age-more-than-18yo", "age-less-than-18yo", "age-18yo"]


def create_industrial_webapp_general_public_users():
    logger.info("create_industrial_webapp_general_public_users")

    users_by_name = {}

    variants = itertools.product(AGE_TAGS)

    for index, (age,) in enumerate(variants, start=100):
        short_age = "".join([chunk[0].upper() for chunk in age.split("-")])
        email = f"pctest.grandpublic.{age}@example.com"
        departement_code = 39
        today = datetime.today()
        date_of_birth = today - timedelta(18 * 366)

        if age == "age-more-than-18yo":
            date_of_birth = today - timedelta(20 * 366)

        if age == "age-less-than-18yo":
            date_of_birth = today - timedelta(16 * 366)

        user = users_factories.UserFactory(
            culturalSurveyId=None,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Grand Public",
            dateOfBirth=date_of_birth,
            hasSeenTutorials=False,
            isBeneficiary=False,
            roles=[],
            lastName=f"{short_age}",
            needsToFillCulturalSurvey=True,
            postalCode="{}100".format(departement_code),
            publicName=f"PC Test Grand Public {short_age}",
        )
        user_key = f"grandpublic{age}"
        users_by_name[user_key] = user

    logger.info("created %d general public users", len(users_by_name))

    return users_by_name
