from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import url_for
from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2023-12-15 16:00:00")
class GetEducationalInstitutionTest:
    endpoint = "adage_iframe.get_educational_institution_with_budget"

    def test_get_institution(self, client):
        year = _build_educational_year()
        deposit = educational_factories.EducationalDepositFactory(educationalYear=year)
        institution = deposit.educationalInstitution

        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json["id"] == institution.id
        assert response.json["name"] == institution.name
        assert response.json["institutionType"] == "COLLEGE"
        assert response.json["postalCode"] == "75000"
        assert response.json["city"] == "PARIS"
        assert response.json["phoneNumber"] == "0600000000"
        assert response.json["budget"] == deposit.get_amount()

    def test_current_deposit_is_used(self, client):
        year1 = _build_educational_year(relativedelta(years=2))
        year2 = _build_educational_year(relativedelta(years=1))
        year3 = _build_educational_year()

        deposit1 = educational_factories.EducationalDepositFactory(educationalYear=year1, amount=1000)
        deposit2 = educational_factories.EducationalDepositFactory(educationalYear=year2, amount=2000)
        deposit3 = educational_factories.EducationalDepositFactory(educationalYear=year3, amount=3000)

        institution = educational_factories.EducationalInstitutionFactory(deposits=[deposit1, deposit2, deposit3])

        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json["budget"] == 3000

    def test_remaining_budget(self, client):
        year = _build_educational_year()
        deposit = educational_factories.EducationalDepositFactory(educationalYear=year, amount=1000)
        institution = educational_factories.EducationalInstitutionFactory(deposits=[deposit])

        used_booking = educational_factories.UsedCollectiveBookingFactory(
            educationalInstitution=institution, educationalYear=year
        )

        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=institution.institutionId)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json["budget"] == deposit.get_amount() - used_booking.collectiveStock.price


def _build_educational_year(delta: relativedelta | None = None):
    delta = delta if delta else relativedelta(years=0)
    now = datetime.utcnow() - delta

    return educational_factories.EducationalYearFactory(
        beginningDate=datetime(now.year, 9, 1),
        expirationDate=datetime(now.year + 1, 8, 31),
    )
