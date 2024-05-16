from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import itertools
import logging
import re

from dateutil.relativedelta import relativedelta
from faker import Faker
import sqlalchemy as sa
import time_machine

from pcapi.core.bookings import factories as bookings_factory
import pcapi.core.finance.conf as finance_conf
import pcapi.core.finance.models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


DEPARTEMENT_CODES = ["93", "97"]
BENEFICIARIES_TAGS = [
    "has-filled-cultural-survey",
    "has-booked-some",
    "has-booked-some-but-deposit-expired",
    "has-no-more-money",
]
UNDERAGE_BENEFICIARIES_TAGS = [
    "15-years-old-underage-beneficiary",
    "16-years-old-underage-beneficiary",
    "17-years-old-underage-beneficiary",
    "18-years-old-ex-underage-beneficiary",
    "18-years-old-ex-underage-beneficiary-ubble",
    "19-years-old-ex-underage-beneficiary",
    "19-years-old-ex-underage-beneficiary-ubble",
]
OTHER_USERS_TAGS = ["has-signed-up"]
AGE_TAGS = ["age-more-than-18yo", "age-less-than-18yo", "age-18yo"]
GRANT_18_DEPOSIT_VERSIONS = [1, 2]


def create_industrial_app_users() -> dict[str, User]:
    beneficiaries = create_industrial_app_beneficiaries()
    underage_beneficiaries = create_industrial_app_underage_beneficiaries()
    other_users = create_industrial_app_other_users()
    general_public_users = create_industrial_app_general_public_users()
    short_email_users = create_short_email_beneficiaries()

    app_users = dict(
        beneficiaries, **underage_beneficiaries, **other_users, **general_public_users, **short_email_users
    )
    return app_users


def create_industrial_app_beneficiaries() -> dict[str, User]:
    logger.info("create_industrial_app_beneficiaries")

    users_by_name = {}

    variants = itertools.product(DEPARTEMENT_CODES, BENEFICIARIES_TAGS, GRANT_18_DEPOSIT_VERSIONS)

    for index, (departement_code, tag, deposit_version) in enumerate(variants, start=0):
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        email = f"pctest.jeune{departement_code}.{tag}.v{deposit_version}@example.com"
        user = users_factories.BeneficiaryGrant18Factory(
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Jeune",
            lastName=f"{departement_code} {short_tag} {deposit_version}",
            needsToFillCulturalSurvey=False,
            postalCode="{}100".format(departement_code),
            deposit__source="sandbox",
            deposit__version=deposit_version,
        )
        users_factories.DepositGrantFactory(
            user=user, expirationDate=datetime.utcnow(), source="sandbox", type=finance_models.DepositType.GRANT_15_17
        )

        user_key = f"jeune{departement_code} {tag} v{deposit_version}"
        users_by_name[user_key] = user

    logger.info("created %d beneficiaries", len(users_by_name))

    return users_by_name


def create_industrial_app_underage_beneficiaries() -> dict[str, User]:
    logger.info("create_industrial_app_underage_beneficiaries")

    users_by_name = {}

    variants = itertools.product(DEPARTEMENT_CODES, UNDERAGE_BENEFICIARIES_TAGS)

    for index, (departement_code, tag) in enumerate(variants, start=0):
        split_tag = tag.split("-")
        short_tag = split_tag[0] + "".join([chunk[0].upper() for chunk in split_tag[1:]])

        email = f"pctest.mineur{departement_code}.{tag}@example.com"

        match = re.match(r"^(\d+)-years-old", tag)
        assert match
        age = int(match.group(1))

        if age >= ELIGIBILITY_AGE_18:
            if "ubble" in tag:
                factory = users_factories.ExUnderageBeneficiaryWithUbbleFactory
            else:
                factory = users_factories.ExUnderageBeneficiaryFactory
        else:
            factory = users_factories.UnderageBeneficiaryFactory

        user = factory(
            subscription_age=age,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Mineur",
            lastName=f"{departement_code} {short_tag}",
            needsToFillCulturalSurvey=False,
            postalCode="{}100".format(departement_code),
            deposit__source="sandbox",
        )

        # EDUCONNECT or UBBLE already created in factory, make subscription steps consistent with granted deposit
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=user.dateCreated,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=user.dateCreated,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        user_key = f"jeune{departement_code} {tag}"
        users_by_name[user_key] = user

    logger.info("created %d underage beneficiaries", len(users_by_name))

    return users_by_name


def create_industrial_app_other_users() -> dict[str, User]:
    logger.info("create_industrial_app_other_users")

    users_by_name = {}

    variants = itertools.product(DEPARTEMENT_CODES, OTHER_USERS_TAGS)

    for index, (departement_code, tag) in enumerate(variants, start=0):
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        needs_to_fill_cultural_survey = bool(tag == "has-signed-up")

        email = f"pctest.autre{departement_code}.{tag}@example.com"

        user = users_factories.UserFactory(
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Utilisateur",
            lastName=f"{departement_code} {short_tag}",
            needsToFillCulturalSurvey=needs_to_fill_cultural_survey,
            postalCode="{}100".format(departement_code),
        )

        user_key = f"jeune{departement_code} {tag}"
        users_by_name[user_key] = user

    logger.info("created %d other users", len(users_by_name))

    return users_by_name


def create_industrial_app_general_public_users() -> dict[str, User]:
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
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="PC Test Grand Public",
            dateOfBirth=date_of_birth,
            roles=[],
            lastName=f"{short_age}",
            needsToFillCulturalSurvey=True,
            postalCode="{}100".format(departement_code),
        )
        user_key = f"grandpublic{age}"
        users_by_name[user_key] = user

    logger.info("created %d general public users", len(users_by_name))

    return users_by_name


def create_short_email_beneficiaries() -> dict[str, User]:
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
    with time_machine.travel(datetime.utcnow() - relativedelta(years=3)):
        users.append(
            users_factories.UnderageBeneficiaryFactory(
                email="exunderage_18@example.com",
                dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=15, months=5),
                subscription_age=15,
                firstName=fake.first_name(),
                lastName=fake.last_name(),
                needsToFillCulturalSurvey=False,
            )
        )

        beneficiary_and_exunderage = users_factories.UnderageBeneficiaryFactory(
            email="bene_18_exunderage@example.com",
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=15, months=5),
            subscription_age=15,
            firstName=fake.first_name(),
            lastName=fake.last_name(),
            needsToFillCulturalSurvey=False,
        )
        db.session.execute(sa.text("ALTER TABLE booking DISABLE TRIGGER booking_update;"))
        bookings_factory.BookingFactory(user=beneficiary_and_exunderage)
        db.session.execute(sa.text("ALTER TABLE booking ENABLE TRIGGER booking_update;"))

        fraud_factories.BeneficiaryFraudCheckFactory(user=beneficiary_and_exunderage)
    users_factories.DepositGrantFactory(user=beneficiary_and_exunderage)
    beneficiary_and_exunderage.add_beneficiary_role()
    users.append(beneficiary_and_exunderage)

    with time_machine.travel(
        datetime.utcnow() - relativedelta(years=finance_conf.GRANT_18_VALIDITY_IN_YEARS, months=5)
    ):
        users.append(
            users_factories.BeneficiaryGrant18Factory(
                email="exbene_20@example.com",
                dateOfBirth=datetime.combine(date.today(), time(0, 0))
                - relativedelta(years=ELIGIBILITY_AGE_18, months=5),
                firstName=fake.first_name(),
                lastName=fake.last_name(),
                needsToFillCulturalSurvey=False,
            )
        )

    user_by_email = {}
    for user in users:
        user_by_email[user.email] = user

    return user_by_email
