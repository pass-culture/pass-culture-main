from datetime import date
from datetime import datetime
from datetime import time
import logging
from random import choice

from dateutil.relativedelta import relativedelta
from faker import Faker
from freezegun import freeze_time

from pcapi.core.bookings import factories as bookings_factory
import pcapi.core.finance.conf as finance_conf
import pcapi.core.finance.models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


DEPARTEMENT_CODES = ["93", "97"]
UNDERAGE_BENEFICIARIES_TAGS = [
    "15-years-old-underage-beneficiary",
    "16-years-old-underage-beneficiary",
    "17-years-old-underage-beneficiary",
]
DATA_USERS = 15
DATA_UNDERAGE_USERS = 5


def create_data_app_users() -> dict[str, User]:
    beneficiaries = create_data_app_beneficiaries()
    underage_beneficiaries = create_data_app_underage_beneficiaries()
    short_email_users = create_short_email_beneficiaries()

    app_users = dict(beneficiaries, **underage_beneficiaries, **short_email_users)
    return app_users


def create_data_app_beneficiaries() -> dict[str, User]:
    logger.info("create_data_app_beneficiaries_data")

    users_by_name = {}

    for index in range(0, DATA_USERS):
        departement_code = "99"
        tag = "has-booked-some"
        deposit_version = 1
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        email = f"pctest.jeune.data{departement_code}_{index}.{tag}.v{deposit_version}@example.com"
        user = users_factories.BeneficiaryGrant18Factory(
            culturalSurveyId=None,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="DATA Test Jeune",
            lastName=f"DATA {departement_code} {short_tag} {deposit_version} {index}",
            needsToFillCulturalSurvey=False,
            postalCode="{}310".format(departement_code),
            publicName=f"DATA Test Jeune {departement_code} {short_tag} {deposit_version} {index}",
            deposit__source="sandbox",
            deposit__version=deposit_version,
        )
        users_factories.DepositGrantFactory(
            user=user, expirationDate=datetime.utcnow(), source="sandbox", type=finance_models.DepositType.GRANT_15_17
        )

        user_key = f"jeune data {departement_code}_{index} {tag} v{deposit_version}"
        users_by_name[user_key] = user

    logger.info("created %d beneficiaries data", len(users_by_name))

    return users_by_name


def create_data_app_underage_beneficiaries() -> dict[str, User]:
    logger.info("create_data_app_underage_beneficiaries_data")

    users_by_name = {}

    for index in range(0, DATA_UNDERAGE_USERS):
        departement_code = "99"
        # tag="has-booked-some"
        tag = choice(UNDERAGE_BENEFICIARIES_TAGS)
        email = f"pctest.mineur.data{departement_code}_{index}.{tag}@example.com"
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])
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
            firstName="DATA Test Mineur",
            lastName=f"DATA {departement_code} {short_tag} {index}",
            needsToFillCulturalSurvey=False,
            postalCode="{}100".format(departement_code),
            publicName=f"DATA Test Mineur {departement_code} {short_tag} {index}",
            deposit__source="sandbox",
        )

        user_key = f"mineur data {departement_code}_{index} {tag}"
        users_by_name[user_key] = user

    logger.info("created %d underage beneficiaries data", len(users_by_name))

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
    with freeze_time(datetime.utcnow() - relativedelta(years=3)):
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
        db.session.execute("ALTER TABLE booking DISABLE TRIGGER booking_update;")
        bookings_factory.IndividualBookingFactory(individualBooking__user=beneficiary_and_exunderage)
        db.session.execute("ALTER TABLE booking ENABLE TRIGGER booking_update;")

        fraud_factories.BeneficiaryFraudCheckFactory(user=beneficiary_and_exunderage)
    users_factories.DepositGrantFactory(user=beneficiary_and_exunderage)
    beneficiary_and_exunderage.add_beneficiary_role()
    beneficiary_and_exunderage.remove_underage_beneficiary_role()
    users.append(beneficiary_and_exunderage)

    with freeze_time(datetime.utcnow() - relativedelta(years=finance_conf.GRANT_18_VALIDITY_IN_YEARS, months=5)):
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
