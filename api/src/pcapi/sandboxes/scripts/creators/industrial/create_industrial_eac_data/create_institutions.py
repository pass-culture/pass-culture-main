from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models


def create_institutions() -> list[educational_models.EducationalInstitution]:
    institutions = [
        educational_factories.EducationalInstitutionFactory(
            institutionId="0560071Y",
            name="JEAN LE COUTALLER",
            institutionType="COLLEGE",
            city="LORIENT",
            postalCode="56100",
        ),
        educational_factories.EducationalInstitutionFactory(
            # institutionId="0470009E",
            name="LYC LES BONS UAI LOCAL",
            institutionType="LYCEE",
            city="BOURG-EN-BRESSE",
            postalCode="01000",
        ),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0910620E",
            institutionType="LYCEE POLYVALENT",
            name="METIER ROBERT DOISNEAU",
            city="CORBEIL-ESSONNES",
            postalCode="91100",
        ),
        educational_factories.EducationalInstitutionFactory(),
        educational_factories.EducationalInstitutionFactory(),
        educational_factories.EducationalInstitutionFactory(),
        educational_factories.EducationalInstitutionFactory(
            name="LYC METIER FREDERIC ET IRENE JOLIOT CURIE",
        ),
    ]
    create_deposits(institutions)
    return institutions


def create_deposits(institutions: list[educational_models.EducationalInstitution]) -> None:
    current_year, next_year = create_years()
    educational_factories.EducationalDepositFactory(
        ministry=educational_models.Ministry.AGRICULTURE,
        educationalInstitution=institutions[0],
        educationalYear=current_year,
        amount=40000,
    )
    educational_factories.EducationalDepositFactory(
        ministry=educational_models.Ministry.AGRICULTURE,
        educationalInstitution=institutions[0],
        educationalYear=next_year,
        amount=50000,
        isFinal=False,
    )

    for educational_institution in institutions[1:]:
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=current_year,
            amount=40000,
        )
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=next_year,
            amount=50000,
            isFinal=False,
        )


def create_years() -> tuple[educational_models.EducationalYear, educational_models.EducationalYear]:
    current_year = educational_factories.EducationalYearFactory()
    next_year = educational_factories.EducationalYearFactory()
    return current_year, next_year
