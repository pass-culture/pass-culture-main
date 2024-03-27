import datetime
import logging
from random import choice

import pcapi.core.finance.models as finance_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User


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

    app_users = dict(beneficiaries, **underage_beneficiaries)
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
            deposit__source="sandbox",
            deposit__version=deposit_version,
        )
        users_factories.DepositGrantFactory(
            user=user,
            expirationDate=datetime.datetime.now(datetime.timezone.utc),
            source="sandbox",
            type=finance_models.DepositType.GRANT_15_17,
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
            deposit__source="sandbox",
        )

        user_key = f"mineur data {departement_code}_{index} {tag}"
        users_by_name[user_key] = user

    logger.info("created %d underage beneficiaries data", len(users_by_name))

    return users_by_name
