from typing import Any

import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.testing import assert_num_queries

from tests.routes.adage.v1.conftest import expected_serialized_prebooking


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_educational_institution(self, client: Any) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=True,
        )
        EducationalInstitutionFactory()
        booking = CollectiveBookingFactory(
            educationalRedactor=redactor,
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=other_educational_year,
            amount=2000,
            isFinal=False,
        )
        EducationalDepositFactory(
            educationalInstitution=other_educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=False,
        )

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 2000,
            "isFinal": True,
            "prebookings": [expected_serialized_prebooking(booking)],
        }

    def test_get_educational_institution_num_queries(self, client: Any) -> None:
        redactor = EducationalRedactorFactory()
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=200000,
            isFinal=True,
        )
        EducationalInstitutionFactory()
        CollectiveBookingFactory.create_batch(
            10,
            educationalRedactor=redactor,
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=other_educational_year,
            amount=2000,
            isFinal=False,
        )
        EducationalDepositFactory(
            educationalInstitution=other_educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=False,
        )

        adage_id = educational_year.adageId
        institution_id = educational_institution.institutionId

        dst = f"/adage/v1/years/{adage_id}/educational_institution/{institution_id}"

        # fetch the institution (1 query)
        # fetch the prebookings (1 query)
        # fetch the deposit (1 query)
        with assert_num_queries(3):
            client.with_eac_token().get(dst)

    def test_get_educational_institution_without_deposit(self, client: Any) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200
        assert response.json == {
            "credit": 0,
            "isFinal": False,
            "prebookings": [],
        }


class Returns404Test:
    def test_get_educational_institution_not_found(self, client: Any, db_session: Any) -> None:
        educational_year = EducationalYearFactory()
        EducationalInstitutionFactory()

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/UNKNOWN"
        )

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}
