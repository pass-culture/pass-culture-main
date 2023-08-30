from typing import Any

import pytest

from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory



class Returns200Test:
    def test_get_educational_deposit(self, client) -> None:
        educational_year1 = EducationalYearFactory()
        educational_institution1 = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution1,
            educationalYear=educational_year1,
            amount=2000,
            isFinal=True,
        )

        educational_year2 = EducationalYearFactory()
        educational_institution2 = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year2,
            amount=3000,
            isFinal=False,
        )

        response = client.with_eac_token().get(f"/adage/v1/years/{educational_year1.adageId}/deposits")

        assert response.status_code == 200
        assert response.json == {
            "deposits": [
                {
                    "uai": educational_institution1.institutionId,
                    "deposit": 2000.0,
                    "isFinal": True,
                }
            ]
        }

        response = client.with_eac_token().get(f"/adage/v1/years/{educational_year2.adageId}/deposits")

        assert response.status_code == 200
        assert response.json == {
            "deposits": [
                {
                    "uai": educational_institution2.institutionId,
                    "deposit": 3000.0,
                    "isFinal": False,
                }
            ]
        }


class Returns404Test:
    def test_get_educational_deposit_not_found(self, client):
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            amount=2000,
            isFinal=True,
        )
        response = client.with_eac_token().get("/adage/v1/years/UNKNOWN/deposits")

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DEPOSIT_NOT_FOUND"}
