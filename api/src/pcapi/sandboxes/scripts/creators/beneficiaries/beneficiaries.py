from datetime import datetime
import logging

from dateutil.relativedelta import SA
from dateutil.relativedelta import relativedelta

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.users.factories as users_factories


logger = logging.getLogger(__name__)


def create_future_beneficiaries() -> None:
    coming_saturday = datetime.utcnow() + relativedelta(weekday=SA)
    eighteen_on_saturday = coming_saturday + relativedelta(years=-18)
    users_factories.UserFactory(
        email="pctest.non-beneficiary.17-going-on-18.v1@example.com",
        dateOfBirth=eighteen_on_saturday,
        needsToFillCulturalSurvey=False,
    )
    users_factories.UserFactory(
        email="pctest.non-beneficiary.17-going-on-18.v2@example.com",
        dateOfBirth=eighteen_on_saturday,
        needsToFillCulturalSurvey=False,
    )

    logger.info("created 2 future beneficiaries")


def create_expiring_beneficiary() -> None:
    coming_saturday = datetime.utcnow() + relativedelta(weekday=SA)
    users_factories.BeneficiaryGrant18Factory(
        email="pctest.beneficiary.deposit-expires-soon@example.com",
        deposit__expirationDate=coming_saturday,
        deposit__source="sandbox",
        needsToFillCulturalSurvey=False,
    )

    logger.info("created 1 expiring beneficiary")


def create_beneficiary_with_empty_deposit() -> None:
    beneficiary_user = users_factories.BeneficiaryGrant18Factory(
        email="pctest.beneficiary.no-more-deposit@example.com",
        deposit__source="sandbox",
        needsToFillCulturalSurvey=False,
    )
    bookings_factories.BookingFactory(
        amount=beneficiary_user.deposit.amount,
        user=beneficiary_user,
        # OffererFactory and VenueFactory would set the siren and
        # siret to '000000000[00000]', which we sometimes use in our
        # prod database for (probably dubious) reasons. That would make
        # the prod->staging dump crash because of a unicity constraint
        # violation.
        stock__offer__venue__siret="55555555500000",
        stock__offer__venue__managingOfferer__siren="555555555",
    )

    logger.info("created 1 beneficiary with empty deposit")


def create_beneficiary_with_specific_address() -> None:
    users_factories.BeneficiaryGrant18Factory(
        email="pctest.beneficiary.adress-specified@example.com",
        address="182 rue Saint-Honoré",
        city="Paris",
        departementCode="75",
        postalCode="75001",
        deposit__source="sandbox",
        needsToFillCulturalSurvey=False,
    )

    logger.info("created 1 beneficiary with specific address")


def create_underage_beneficiary() -> None:
    users_factories.UnderageBeneficiaryFactory(
        email="pctest.underage-beneficiary@example.com",
        deposit__source="sandbox",
    )
    logger.info("created 1 underage beneficiary")


def save_beneficiaries_sandbox() -> None:
    create_future_beneficiaries()
    create_expiring_beneficiary()
    create_beneficiary_with_empty_deposit()
    create_beneficiary_with_specific_address()
    create_underage_beneficiary()
