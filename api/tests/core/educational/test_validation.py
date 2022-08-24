from decimal import Decimal

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational.factories import CancelledCollectiveBookingFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.validation import check_institution_fund


class EducationalValidationTest:
    def test_institution_fund_is_ok(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
        )
        PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(2000.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        CancelledCollectiveBookingFactory(
            collectiveStock__price=Decimal(2000.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory.create_batch(
            20,
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        check_institution_fund(
            educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
        )

    def test_institution_fund_is_temporary_insufficient(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=False,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(
                educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
            )

    def test_institution_fund_is_insufficient(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(
                educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
            )
