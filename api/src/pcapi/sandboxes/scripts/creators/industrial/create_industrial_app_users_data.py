from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
import itertools
import logging
import uuid

from dateutil.relativedelta import relativedelta
from faker import Faker
from freezegun import freeze_time

from pcapi.core.bookings import factories as bookings_factory
import pcapi.core.finance.conf as finance_conf
import pcapi.core.finance.models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


DEPARTEMENT_CODES = ["93","97","99"]
BENEFICIARIES_TAGS = [
    "has-filled-cultural-survey",
    "has-booked-some",
]
UNDERAGE_BENEFICIARIES_TAGS = [
    "15-years-old-underage-beneficiary",
    "16-years-old-underage-beneficiary",
    "17-years-old-underage-beneficiary",
]
OTHER_USERS_TAGS = ["has-signed-up", "has-booked-activation"]
AGE_TAGS = ["age-more-than-18yo", "age-less-than-18yo", "age-18yo"]
GRANT_18_DEPOSIT_VERSIONS = [1, 2]

DATA_USERS=10

def create_industrial_app_users_data() -> dict[str, User]:
    beneficiaries = create_industrial_app_beneficiaries()
    app_users = dict(
        beneficiaries
    )
    return app_users


def create_industrial_app_beneficiaries() -> dict[str, User]:
    logger.info("create_industrial_app_beneficiaries")

    users_by_name = {}

    variants = itertools.product(DEPARTEMENT_CODES, BENEFICIARIES_TAGS, GRANT_18_DEPOSIT_VERSIONS)

    for index in range(0,DATA_USERS):
        departement_code="93"
        tag="has-booked-some"
        deposit_version=2
        short_tag = "".join([chunk[0].upper() for chunk in tag.split("-")])

        email = f"pctest.jeune.data{departement_code}.{tag}.v{deposit_version}_{index}@example.com"
        user = users_factories.BeneficiaryGrant18Factory(
            culturalSurveyId=None,
            departementCode=str(departement_code),
            email=email,
            phoneNumber=f"+336{index:0>8}",
            firstName="DATA Test Jeune ",
            lastName=f"DATA {departement_code} {short_tag} {deposit_version}",
            needsToFillCulturalSurvey=False,
            postalCode="{}100".format(departement_code),
            publicName=f"DATA Test Jeune {departement_code} {short_tag} {deposit_version} {index}",
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

