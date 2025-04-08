import datetime
import typing

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models


def create_institutions() -> list[educational_models.EducationalInstitution]:
    program = educational_factories.EducationalInstitutionProgramFactory(
        name="marseille_en_grand", label="Marseille en grand"
    )
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
            institutionId="0010013J",
            name="",
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
            institutionId="0130569Y",
            institutionType="ECOLE ELEMENTAIRE PUBLIQUE",
            name="FRANCOIS MOISSON",
            city="MARSEILLE",
            postalCode="13002",
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(
                    program=program,
                )
            ],
        ),
        educational_factories.EducationalInstitutionFactory(
            institutionId="0130541T",
            institutionType="ECOLE ELEMENTAIRE PUBLIQUE",
            name="CANET AMBROSINI",
            city="MARSEILLE",
            postalCode="13014",
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(
                    program=program,
                )
            ],
        ),
        # keep one school without the expected program to allow some
        # tests
        educational_factories.EducationalInstitutionFactory(
            institutionId="0131251P",
            institutionType="ECOLE MATERNELLE PUBLIQUE",
            name="PARC DES CHARTREUX",
            city="MARSEILLE",
            postalCode="13013",
        ),
        # ministry = AGRICULTURE
        educational_factories.EducationalInstitutionFactory(
            institutionId="0771436T",
            institutionType="LYCEE ENS GENERAL TECHNO PROF AGRICOLE",
            name="CAMPUS BOUGAINVILLE DE BRIE-COMTE-ROBERT",
            city="BRIE-COMTE-ROBERT",
            postalCode="77170",
        ),
        # ministry = MER
        educational_factories.EducationalInstitutionFactory(
            institutionId="0221624W",
            institutionType="LYCEE PROFESSIONNEL",
            name="LYCEE PROFESSIONNEL MARITIME PIERRE LOTI",
            city="PAIMPOL",
            postalCode="22501",
        ),
        # ministry = ARMEES
        educational_factories.EducationalInstitutionFactory(
            institutionId="0290063L",
            institutionType="LYCEE D ENSEIGNEMENT GENERAL",
            name="LYCEE NAVAL DE BREST",
            city="BREST",
            postalCode="29240",
        ),
    ]
    if settings.CREATE_ADAGE_TESTING_DATA:
        # Those are used by Adage for testing purposes
        institutions += [
            educational_factories.EducationalInstitutionFactory(
                name="LYC METIER FREDERIC ET IRENE JOLIOT CURIE", institutionId="0760100W"
            ),
            educational_factories.EducationalInstitutionFactory(
                institutionId="0780032L",
                institutionType="COLLEGE",
                name="FLORA TRISTAN",
                city="CARRIÈRES-SOUS-POISSY",
                postalCode="78955",
            ),
            educational_factories.EducationalInstitutionFactory(
                institutionId="0780004F",
                institutionType="LYCÉE AGRICOLE ET HORTICOLE",
                name="LEGTPA DE ST GERMAIN EN LAYE",
                city="SAINT-GERMAIN-EN-LAYE",
                postalCode="78100",
            ),
            educational_factories.EducationalInstitutionFactory(
                institutionId="0130553F",
                institutionType="ECOLE ÉLÉMENTAIRE",
                name="CLAIR SOLEIL",
                city="MARSEILLE",
                programAssociations=[
                    educational_factories.EducationalInstitutionProgramAssociationFactory(
                        program=program,
                    )
                ],
                postalCode="13014",
            ),
            educational_factories.EducationalInstitutionFactory(institutionId="0921935D"),
            educational_factories.EducationalInstitutionFactory(institutionId="0752525M"),
            educational_factories.EducationalInstitutionFactory(institutionId="0752902X"),
            educational_factories.EducationalInstitutionFactory(institutionId="0781537X"),
            educational_factories.EducationalInstitutionFactory(institutionId="0922256C"),
            educational_factories.EducationalInstitutionFactory(institutionId="0761337R"),
            educational_factories.EducationalInstitutionFactory(institutionId="0781845G"),
            educational_factories.EducationalInstitutionFactory(institutionId="0920150N"),
            educational_factories.EducationalInstitutionFactory(institutionId="0750652B"),
            educational_factories.EducationalInstitutionFactory(institutionId="0760142S"),
            educational_factories.EducationalInstitutionFactory(institutionId="0762735K"),
            educational_factories.EducationalInstitutionFactory(institutionId="0780015T"),
            educational_factories.EducationalInstitutionFactory(institutionId="0783283V"),
            educational_factories.EducationalInstitutionFactory(institutionId="0920889S"),
            educational_factories.EducationalInstitutionFactory(institutionId="0753820V"),
            educational_factories.EducationalInstitutionFactory(institutionId="0761341V"),
            educational_factories.EducationalInstitutionFactory(institutionId="0762634A"),
        ]

    create_deposits(institutions)
    return institutions


def create_deposits(institutions: list[educational_models.EducationalInstitution]) -> None:
    years = create_years()

    for year, amount in zip(years, range(20000, 50001, 10000)):
        educational_factories.EducationalDepositFactory(
            ministry=educational_models.Ministry.AGRICULTURE,
            educationalInstitution=institutions[0],
            educationalYear=year,
            amount=amount,
            isFinal=(year.beginningDate <= datetime.datetime.utcnow()),
        )

        for educational_institution in institutions[1:]:
            educational_factories.EducationalDepositFactory(
                educationalInstitution=educational_institution,
                educationalYear=year,
                amount=amount,
                isFinal=(year.beginningDate <= datetime.datetime.utcnow()),
            )


def create_years() -> typing.Iterable[educational_models.EducationalYear]:
    before = educational_factories.create_educational_year(datetime.datetime.utcnow() - datetime.timedelta(days=731))
    last_year = educational_factories.create_educational_year(datetime.datetime.utcnow() - datetime.timedelta(days=365))
    current_year = educational_factories.create_educational_year(datetime.datetime.utcnow())
    next_year = educational_factories.create_educational_year(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    return before, last_year, current_year, next_year
