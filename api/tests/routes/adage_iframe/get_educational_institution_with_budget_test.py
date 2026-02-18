from datetime import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta
from flask import url_for

from pcapi.core.educational import factories
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class EducationalInstitutionTest:
    endpoint = "adage_iframe.get_educational_institution_with_budget"

    @time_machine.travel("2023-12-15 16:00:00")
    def test_get_institution(self, client):
        year = _build_educational_year()
        deposit = factories.EducationalDepositFactory(educationalYear=year)
        institution = deposit.educationalInstitution

        educational_redactor = factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"budget": deposit.amount}

    @time_machine.travel("2023-12-15 16:00:00")
    def test_current_deposit_is_used(self, client):
        year1 = _build_educational_year(relativedelta(years=2))
        year2 = _build_educational_year(relativedelta(years=1))
        year3 = _build_educational_year()

        deposit1 = factories.EducationalDepositFactory(educationalYear=year1, amount=1000)
        deposit2 = factories.EducationalDepositFactory(educationalYear=year2, amount=2000)
        deposit3 = factories.EducationalDepositFactory(educationalYear=year3, amount=3000)

        institution = factories.EducationalInstitutionFactory(deposits=[deposit1, deposit2, deposit3])

        educational_redactor = factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"budget": 3000}

    @time_machine.travel("2023-12-15 16:00:00")
    def test_remaining_budget(self, client):
        year = _build_educational_year()
        deposit = factories.EducationalDepositFactory(educationalYear=year, amount=1000)
        institution = factories.EducationalInstitutionFactory(deposits=[deposit])

        used_booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit
        )

        educational_redactor = factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"budget": deposit.amount - used_booking.collectiveStock.price}

    @time_machine.travel("2023-12-15 16:00:00")
    def test_remaining_budget_first_period(self, client):
        year = factories.EducationalCurrentYearFactory()
        institution = factories.EducationalInstitutionFactory()
        deposit_1 = factories.EducationalDepositFirstPeriodFactory(
            educationalYear=year,
            educationalInstitution=institution,
            amount=1000,
        )
        factories.EducationalDepositSecondPeriodFactory(
            educationalYear=year,
            educationalInstitution=institution,
            amount=2000,
        )

        used_booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit_1
        )

        educational_redactor = factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"budget": 1000 - used_booking.collectiveStock.price}

    @time_machine.travel("2024-05-15 16:00:00")
    def test_remaining_budget_second_period(self, client):
        year = factories.EducationalCurrentYearFactory()
        institution = factories.EducationalInstitutionFactory()
        deposit_1 = factories.EducationalDepositFirstPeriodFactory(
            educationalYear=year,
            educationalInstitution=institution,
            amount=1000,
        )
        deposit_2 = factories.EducationalDepositSecondPeriodFactory(
            educationalYear=year,
            educationalInstitution=institution,
            amount=2000,
        )

        used_booking = factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit_2
        )
        # this booking is linked to the first deposit, it should be ignored in the remaining budget computation
        factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year, educationalDeposit=deposit_1
        )

        educational_redactor = factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json == {"budget": 2000 - used_booking.collectiveStock.price}


def _build_educational_year(delta: relativedelta | None = None):
    delta = delta if delta else relativedelta(years=0)
    now = date_utils.get_naive_utc_now() - delta

    return factories.EducationalYearFactory(
        beginningDate=datetime(now.year, 9, 1),
        expirationDate=datetime(now.year + 1, 8, 31, 23, 59, 59),
    )
