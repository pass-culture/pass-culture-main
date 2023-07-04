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
            institutionId="0470009E",
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
        educational_factories.EducationalInstitutionFactory(
            institutionId="0130872C",
            institutionType="ECOLE MATERNELLE PUBLIQUE",
            name="EVECHE",
            city="MARSEILLE",
            postalCode="13002",
        ),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0130569Y",
            institutionType="ECOLE MATERNELLE PUBLIQUE",
            name="FRANCOIS MOISSON",
            city="MARSEILLE",
            postalCode="13002",
        ),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0130855J",
            institutionType="ECOLE MATERNELLE PUBLIQUE",
            name="CANET LAROUSSE",
            city="MARSEILLE",
            postalCode="13014",
        ),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0130629N",
            institutionType="ECOLE MATERNELLE PUBLIQUE",
            name="SAINT BARTHELEMY SNCF",
            city="MARSEILLE",
            postalCode="13014",
        ),
        educational_factories.EducationalInstitutionFactory(institutionId="0780032L"),
        educational_factories.EducationalInstitutionFactory(institutionId="0921545E"),
        educational_factories.EducationalInstitutionFactory(institutionId="0752525M"),
        educational_factories.EducationalInstitutionFactory(institutionId="0752902X"),
        educational_factories.EducationalInstitutionFactory(institutionId="0781537X"),
        educational_factories.EducationalInstitutionFactory(institutionId="0922256C"),
        educational_factories.EducationalInstitutionFactory(institutionId="0761337R"),
        educational_factories.EducationalInstitutionFactory(institutionId="0781845G"),
        educational_factories.EducationalInstitutionFactory(institutionId="0920150N"),
        educational_factories.EducationalInstitutionFactory(institutionId="0750652B"),
        educational_factories.EducationalInstitutionFactory(institutionId="0760142S"),
        educational_factories.EducationalInstitutionFactory(institutionId="0780004F"),
        educational_factories.EducationalInstitutionFactory(institutionId="0762735K"),
        educational_factories.EducationalInstitutionFactory(institutionId="0780015T"),
        educational_factories.EducationalInstitutionFactory(institutionId="0783283V"),
        educational_factories.EducationalInstitutionFactory(institutionId="0920889S"),
        educational_factories.EducationalInstitutionFactory(institutionId="0753820V"),
        educational_factories.EducationalInstitutionFactory(institutionId="0761341V"),
        educational_factories.EducationalInstitutionFactory(institutionId="0762634A"),
        educational_factories.EducationalInstitutionFactory(
            name="LYC METIER FREDERIC ET IRENE JOLIOT CURIE", institutionId="0760100W"
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
