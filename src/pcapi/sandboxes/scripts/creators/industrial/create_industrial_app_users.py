from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import itertools
import logging
import uuid

from dateutil.relativedelta import relativedelta
from faker import Faker

from pcapi.core.bookings.conf import GRANT_18_VALIDITY_IN_YEARS
from pcapi.core.payments import factories as payments_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import TokenType
from pcapi.models.deposit import DepositType


logger = logging.getLogger(__name__)


DEPARTEMENT_CODES = ["93", "97"]
BENEFICIARIES_TAGS = [
    "has-filled-cultural-survey",
    "has-confirmed-activation",
    "has-booked-some",
    "has-booked-some-but-deposit-expired",
    "has-no-more-money",
]
UNDERAGE_BENEFICIARIES_TAGS = [
    "15-years-old-underage-beneficiary",
    "16-years-old-underage-beneficiary",
    "17-years-old-underage-beneficiary",
]
OTHER_USERS_TAGS = ["has-signed-up", "has-booked-activation"]
AGE_TAGS = ["age-more-than-18yo", "age-less-than-18yo", "age-18yo"]
GRANT_18_DEPOSIT_VERSIONS = [1, 2]


def create_industrial_app_users():
    beneficiaries = create_industrial_app_beneficiaries()
    underage_beneficiaries = create_industrial_app_underage_beneficiaries()
    other_users = create_industrial_app_other_users()
    general_public_users = create_industrial_app_general_public_users()
    short_email_users = create_short_email_beneficiaries()

    app_users = dict(
        beneficiaries, **underage_beneficiaries, **other_users, **general_public_users, **short_email_users
    )
    return app_users


def create_industrial_app_beneficiaries():
    logger.info("create_industrial_app_beneficiaries")

    users_by_name = {}

    variants = itertools.product(DEPARTEMENT_CODES, BENEFICIARIES_TAGS, GRANT_18_DEPOSIT_VERSIONS)

    for index, (departement_code, tag, deposit_version) in enumerate(variants, start=0):
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        if tag == "has-filled-cultural-survey":
            has_seen_tutorials = False
        else:
            has_seen_tutorials = True

        email = f"pctest.jeune{departement_code}.{tag}.v{deposit_version}@example.com"
        user = users_factories.BeneficiaryGrant18Factory(
            culturalSurveyId=None,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Jeune",
            hasSeenTutorials=has_seen_tutorials,
            lastName=f"{departement_code} {short_tag} {deposit_version}",
            needsToFillCulturalSurvey=False,
            postalCode="{}100".format(departement_code),
            publicName=f"PC Test Jeune {departement_code} {short_tag} {deposit_version}",
            deposit__source="sandbox",
            deposit__version=deposit_version,
        )
        payments_factories.DepositGrantFactory(
            user=user, expirationDate=datetime.now(), source="sandbox", type=DepositType.GRANT_17
        )

        user_key = f"jeune{departement_code} {tag} v{deposit_version}"
        users_by_name[user_key] = user

    logger.info("created %d beneficiaries", len(users_by_name))

    return users_by_name


def create_industrial_app_underage_beneficiaries():
    logger.info("create_industrial_app_underage_beneficiaries")

    users_by_name = {}

    variants = itertools.product(DEPARTEMENT_CODES, UNDERAGE_BENEFICIARIES_TAGS)

    for index, (departement_code, tag) in enumerate(variants, start=0):
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        email = f"pctest.mineur{departement_code}.{tag}@example.com"

        if tag == "15-years-old-underage-beneficiary":
            age = 15
        elif tag == "16-years-old-underage-beneficiary":
            age = 16
        else:
            age = 17

        user = users_factories.UnderageBeneficiaryFactory(
            subscription_age=age,
            culturalSurveyId=None,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Mineur",
            hasSeenTutorials=True,
            lastName=f"{departement_code} {short_tag}",
            needsToFillCulturalSurvey=False,
            postalCode="{}100".format(departement_code),
            publicName=f"PC Test Mineur {departement_code} {short_tag}",
            deposit__source="sandbox",
        )

        user_key = f"jeune{departement_code} {tag}"
        users_by_name[user_key] = user

    logger.info("created %d underage beneficiaries", len(users_by_name))

    return users_by_name


def create_industrial_app_other_users():
    logger.info("create_industrial_app_other_users")

    users_by_name = {}

    validation_prefix, validation_suffix = "AZERTY", 123
    validation_suffix += 1

    variants = itertools.product(DEPARTEMENT_CODES, OTHER_USERS_TAGS)

    for index, (departement_code, tag) in enumerate(variants, start=0):
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        if tag == "has-signed-up":
            reset_password_token = "{}{}".format(validation_prefix, validation_suffix)
            validation_suffix += 1
            cultural_survey_id = uuid.uuid4()
            needs_to_fill_cultural_survey = True
            has_seen_tutorials = False
        else:
            cultural_survey_id = None
            needs_to_fill_cultural_survey = False
            has_seen_tutorials = True
            reset_password_token = None

        email = f"pctest.autre{departement_code}.{tag}@example.com"

        user = users_factories.UserFactory(
            culturalSurveyId=cultural_survey_id,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Utilisateur",
            hasSeenTutorials=has_seen_tutorials,
            lastName=f"{departement_code} {short_tag}",
            needsToFillCulturalSurvey=needs_to_fill_cultural_survey,
            postalCode="{}100".format(departement_code),
            publicName=f"PC Test Utilisateur {departement_code} {short_tag}",
        )

        if reset_password_token:
            users_factories.TokenFactory(
                user=user,
                value=reset_password_token,
                expirationDate=datetime.utcnow() + timedelta(hours=24),
                type=TokenType.RESET_PASSWORD,
            )
        user_key = f"jeune{departement_code} {tag}"
        users_by_name[user_key] = user

    logger.info("created %d other users", len(users_by_name))

    return users_by_name


def create_industrial_app_general_public_users():
    logger.info("create_industrial_app_general_public_users")

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


def create_short_email_beneficiaries() -> dict:
    fake = Faker("fr_FR")
    users = []

    for age in [15, 16, 17]:
        users.append(
            users_factories.UnderageBeneficiaryFactory(
                email=f"bene_{age}@example.com",
                subscription_age=age,
                firstName=fake.first_name(),
                lastName=fake.last_name(),
                needsToFillCulturalSurvey=False,
            )
        )
    for age in [15, 16, 17, 18]:
        users.append(
            users_factories.UserFactory(
                email=f"eli_{age}@example.com",
                address=None,
                city=None,
                dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=age, months=5),
                departementCode=None,
                firstName=None,
                lastName=None,
                postalCode=None,
                needsToFillCulturalSurvey=False,
            )
        )

    users.append(
        users_factories.BeneficiaryGrant18Factory(
            email="bene_18@example.com",
            firstName=fake.first_name(),
            lastName=fake.last_name(),
            needsToFillCulturalSurvey=False,
        )
    )

    users.append(
        users_factories.UnderageBeneficiaryFactory(
            email="exunderage_18@example.com",
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=18, months=5),
            dateCreated=datetime.utcnow() - relativedelta(years=3, months=3),
            subscription_age=15,
            firstName=fake.first_name(),
            lastName=fake.last_name(),
            needsToFillCulturalSurvey=False,
        )
    )

    users.append(
        users_factories.BeneficiaryGrant18Factory(
            email="exbene_20@example.com",
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=20, months=5),
            dateCreated=datetime.utcnow() - relativedelta(years=GRANT_18_VALIDITY_IN_YEARS, months=5),
            deposit__expirationDate=datetime.utcnow() - relativedelta(months=5),
            firstName=fake.first_name(),
            lastName=fake.last_name(),
            needsToFillCulturalSurvey=False,
        )
    )

    user_by_email = {}
    for user in users:
        user_by_email[user.email] = user

    return user_by_email
