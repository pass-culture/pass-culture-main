import pytest

from pcapi.core.educational import factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_educational_deposit(self, client) -> None:
        educational_year1 = factories.EducationalYearFactory()
        educational_institution1 = factories.EducationalInstitutionFactory()
        factories.EducationalDepositFactory(
            educationalInstitution=educational_institution1,
            educationalYear=educational_year1,
            amount=2000,
            isFinal=True,
        )

        educational_year2 = factories.EducationalYearFactory()
        educational_institution2 = factories.EducationalInstitutionFactory()
        factories.EducationalDepositFactory(
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
                    "period": {
                        "start": educational_year1.beginningDate.isoformat() + "Z",
                        "end": educational_year1.expirationDate.isoformat() + "Z",
                    },
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
                    "period": {
                        "start": educational_year2.beginningDate.isoformat() + "Z",
                        "end": educational_year2.expirationDate.isoformat() + "Z",
                    },
                }
            ]
        }

    def test_get_educational_deposit_two_periods(self, client) -> None:
        educational_year = factories.EducationalYearFactory()
        educational_institution = factories.EducationalInstitutionFactory()
        deposit_first_period = factories.EducationalDepositFirstPeriodFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=2000,
        )
        deposit_second_period = factories.EducationalDepositSecondPeriodFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=2500,
        )

        response = client.with_eac_token().get(f"/adage/v1/years/{educational_year.adageId}/deposits")

        assert response.status_code == 200
        assert response.json == {
            "deposits": [
                {
                    "uai": educational_institution.institutionId,
                    "deposit": 2000,
                    "isFinal": True,
                    "period": {
                        "start": deposit_first_period.period.lower.isoformat() + "Z",
                        "end": deposit_first_period.period.upper.isoformat() + "Z",
                    },
                },
                {
                    "uai": educational_institution.institutionId,
                    "deposit": 2500,
                    "isFinal": True,
                    "period": {
                        "start": deposit_second_period.period.lower.isoformat() + "Z",
                        "end": deposit_second_period.period.upper.isoformat() + "Z",
                    },
                },
            ]
        }


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_get_educational_deposit_not_found(self, client) -> None:
        educational_institution = factories.EducationalInstitutionFactory()
        factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            amount=2000,
            isFinal=True,
        )
        response = client.with_eac_token().get("/adage/v1/years/UNKNOWN/deposits")

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DEPOSIT_NOT_FOUND"}
