from datetime import datetime
import logging

from dateutil.relativedelta import SA
from dateutil.relativedelta import relativedelta

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.users.factories as users_factories


logger = logging.getLogger(__name__)


def create_future_beneficiaries() -> None:
    coming_saturday = datetime.now() + relativedelta(weekday=SA)
    eighteen_on_saturday = coming_saturday + relativedelta(years=-18)
    users_factories.UserFactory(
        email="pctest.non-beneficiary.17-going-on-18.v1@example.com",
        dateOfBirth=eighteen_on_saturday,
        isBeneficiary=False,
        needsToFillCulturalSurvey=False,
        hasSeenTutorials=True,
    )
    users_factories.UserFactory(
        email="pctest.non-beneficiary.17-going-on-18.v2@example.com",
        dateOfBirth=eighteen_on_saturday,
        isBeneficiary=False,
        needsToFillCulturalSurvey=False,
        hasSeenTutorials=True,
    )

    logger.info("created 2 future beneficiaries")


def create_expiring_beneficiary() -> None:
    coming_saturday = datetime.now() + relativedelta(weekday=SA)
    users_factories.BeneficiaryFactory(
        email="pctest.beneficiary.deposit-expires-soon@example.com",
        deposit__expirationDate=coming_saturday,
        deposit__source="sandbox",
        needsToFillCulturalSurvey=False,
        hasSeenTutorials=True,
    )

    logger.info("created 1 expiring beneficiary")


def create_beneficiary_with_empty_deposit() -> None:
    beneficiary_user = users_factories.BeneficiaryFactory(
        email="pctest.beneficiary.no-more-deposit@example.com",
        deposit__source="sandbox",
        needsToFillCulturalSurvey=False,
        hasSeenTutorials=True,
    )
    bookings_factories.BookingFactory(user=beneficiary_user, amount=beneficiary_user.deposit.amount)

    logger.info("created 1 beneficiary with empty deposit")


def create_beneficiary_with_specific_address() -> None:
    users_factories.BeneficiaryFactory(
        email="pctest.beneficiary.adress-specified@example.com",
        address="182 rue Saint-Honoré",
        city="Paris",
        departementCode="75",
        postalCode="75001",
        deposit__source="sandbox",
        needsToFillCulturalSurvey=False,
        hasSeenTutorials=True,
    )

    logger.info("created 1 beneficiary with specific address")


def save_beneficiaries_sandbox() -> None:
    create_future_beneficiaries()
    create_expiring_beneficiary()
    create_beneficiary_with_empty_deposit()
    create_beneficiary_with_specific_address()
