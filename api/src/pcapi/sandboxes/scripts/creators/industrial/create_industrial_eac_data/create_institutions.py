import datetime

import pytz

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import utils
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils
from pcapi.utils.db import make_timerange


# store here UAIs with a ministry that is not EDUCATION_NATIONALE
MINISTRY_BY_UAI = {
    "0771436T": educational_models.Ministry.AGRICULTURE,
    "0221624W": educational_models.Ministry.MER,
    "0290063L": educational_models.Ministry.ARMEES,
    "0780004F": educational_models.Ministry.AGRICULTURE,
    "0762735K": educational_models.Ministry.MER,
    "0780015T": educational_models.Ministry.ARMEES,
    "0762634A": educational_models.Ministry.AGRICULTURE,
}


@log_func_duration
def create_institutions() -> list[educational_models.EducationalInstitution]:
    program = educational_factories.EducationalInstitutionProgramFactory.create(
        name="marseille_en_grand", label="Marseille en grand"
    )
    institutions = [
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0560071Y",
            name="JEAN LE COUTALLER",
            institutionType="COLLEGE",
            city="LORIENT",
            postalCode="56100",
        ),
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0470009E",
            name="LYC LES BONS UAI LOCAL",
            institutionType="LYCEE",
            city="BOURG-EN-BRESSE",
            postalCode="01000",
        ),
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0010013J",
            name="",
            institutionType="LYCEE",
            city="BOURG-EN-BRESSE",
            postalCode="01000",
        ),
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0910620E",
            institutionType="LYCEE POLYVALENT",
            name="METIER ROBERT DOISNEAU",
            city="CORBEIL-ESSONNES",
            postalCode="91100",
            latitude=48.61,
            longitude=2.46,
        ),
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0130569Y",
            institutionType="ECOLE ELEMENTAIRE PUBLIQUE",
            name="FRANCOIS MOISSON",
            city="MARSEILLE",
            postalCode="13002",
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory.create(
                    program=program,
                )
            ],
        ),
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0130541T",
            institutionType="ECOLE ELEMENTAIRE PUBLIQUE",
            name="CANET AMBROSINI",
            city="MARSEILLE",
            postalCode="13014",
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory.create(
                    program=program,
                )
            ],
        ),
        # keep one school without the expected program to allow some
        # tests
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0131251P",
            institutionType="ECOLE MATERNELLE PUBLIQUE",
            name="PARC DES CHARTREUX",
            city="MARSEILLE",
            postalCode="13013",
        ),
        # ministry = AGRICULTURE
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0771436T",
            institutionType="LYCEE ENS GENERAL TECHNO PROF AGRICOLE",
            name="CAMPUS BOUGAINVILLE DE BRIE-COMTE-ROBERT",
            city="BRIE-COMTE-ROBERT",
            postalCode="77170",
        ),
        # ministry = MER
        educational_factories.EducationalInstitutionFactory.create(
            institutionId="0221624W",
            institutionType="LYCEE PROFESSIONNEL",
            name="LYCEE PROFESSIONNEL MARITIME PIERRE LOTI",
            city="PAIMPOL",
            postalCode="22501",
        ),
        # ministry = ARMEES
        educational_factories.EducationalInstitutionFactory.create(
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
            educational_factories.EducationalInstitutionFactory.create(
                name="LYC METIER FREDERIC ET IRENE JOLIOT CURIE", institutionId="0760100W"
            ),
            educational_factories.EducationalInstitutionFactory.create(
                institutionId="0780032L",
                institutionType="COLLEGE",
                name="FLORA TRISTAN",
                city="CARRIÈRES-SOUS-POISSY",
                postalCode="78955",
            ),
            educational_factories.EducationalInstitutionFactory.create(
                institutionId="0780004F",
                institutionType="LYCÉE AGRICOLE ET HORTICOLE",
                name="LEGTPA DE ST GERMAIN EN LAYE",
                city="SAINT-GERMAIN-EN-LAYE",
                postalCode="78100",
            ),
            educational_factories.EducationalInstitutionFactory.create(
                institutionId="0130553F",
                institutionType="ECOLE ÉLÉMENTAIRE",
                name="CLAIR SOLEIL",
                city="MARSEILLE",
                programAssociations=[
                    educational_factories.EducationalInstitutionProgramAssociationFactory.create(
                        program=program,
                    )
                ],
                postalCode="13014",
            ),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0921935D"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0752525M"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0752902X"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0781537X"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0922256C"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0761337R"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0781845G"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0920150N"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0750652B"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0760142S"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0762735K"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0780015T"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0783283V"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0920889S"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0753820V"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0761341V"),
            educational_factories.EducationalInstitutionFactory.create(institutionId="0762634A"),
        ]

    create_deposits(institutions)
    return institutions


@log_func_duration
def create_institutions_with_deposits_by_period() -> list[educational_models.EducationalDeposit]:
    test_datetime = datetime.datetime(2025, 12, 1)
    current_year = educational_factories.create_educational_year(test_datetime)
    next_year = educational_factories.create_educational_year(test_datetime.replace(year=test_datetime.year + 1))

    institution_data = (
        ("CLG", "ANDRE MALRAUX", "ASNIERES-SUR-SEINE", "0921545E"),
        ("CLG", "LUCIE AUBRAC", "ARGENTEUIL", "0951356H"),
        ("LGT", "JULIE-VICTOIRE DAUBIE", "ARGENTEUIL", "0950640E"),
        ("LP", "SIMONE WEIL", "CONFLANS-SAINTE-HONORINE", "0783447Y"),
        ("LGT", "ROSA PARKS", "MONTGERON", "0910625K"),
        ("LPO", "LYC METIER GUSTAVE MONOD", "ENGHIEN-LES-BAINS", "0952196W"),
        ("LPO", "JEAN-JACQUES ROUSSEAU", "SARCELLES", "0950650R"),
        ("LGT", "JEAN-BAPTISTE COROT", "SAVIGNY-SUR-ORGE", "0910627M"),
        ("CLG", "JEAN RACINE", "VIROFLAY", "0780184B"),
        ("CLG", "PAUL ELUARD", "SAINTE-GENEVIEVE-DES-BOIS", "0911042N"),
    )

    institutions = [
        educational_factories.EducationalInstitutionFactory.create(
            institutionId=uai, institutionType=institution_type, name=name, city=city
        )
        for institution_type, name, city, uai in institution_data
    ]
    institutions_iter = iter(institutions)
    deposits = []

    # case 1: no deposit for current year
    # deposit with amount 0 for next year, first period
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=next_year,
                period=utils.get_educational_year_first_period(next_year),
                amount=0,
            ),
        ]
    )

    # case 2: deposit for current year, 2 periods
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=utils.get_educational_year_first_period(current_year),
                amount=3000,
            ),
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=utils.get_educational_year_second_period(current_year),
                amount=7000,
            ),
        ]
    )

    # case 3: deposit for current year, first period only
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=utils.get_educational_year_first_period(current_year),
                amount=3000,
            )
        ]
    )

    # case 4: deposit for current year, period = educational year
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=utils.get_educational_year_full_period(current_year),
                amount=10_000,
            )
        ]
    )

    # case 5: deposit for current year, 2 periods, first period is passed
    institution = next(institutions_iter)
    PARIS_TZ = pytz.timezone(date_utils.METROPOLE_TIMEZONE)
    passed_period_end = PARIS_TZ.localize(datetime.datetime(2025, 10, 31, 23, 59, 59))
    passed_period_next_start = PARIS_TZ.localize(datetime.datetime(2025, 11, 1))
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=make_timerange(start=current_year.beginningDate, end=passed_period_end),
                amount=3000,
            ),
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=make_timerange(start=passed_period_next_start, end=current_year.expirationDate),
                amount=7000,
            ),
        ]
    )

    # case 6: deposit for current year, first period only, passed
    # deposit with amount 0 for second period
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=make_timerange(start=current_year.beginningDate, end=passed_period_end),
                amount=3000,
            ),
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=make_timerange(start=passed_period_next_start, end=current_year.expirationDate),
                amount=0,
            ),
        ]
    )

    # case 7: deposit with amount 0 for current year, first period
    # no deposit for next year
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=current_year,
                period=utils.get_educational_year_first_period(current_year),
                amount=0,
            ),
        ]
    )

    # case 8: deposit for next year, 2 periods
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=next_year,
                period=utils.get_educational_year_first_period(next_year),
                amount=3000,
            ),
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=next_year,
                period=utils.get_educational_year_second_period(next_year),
                amount=7000,
            ),
        ]
    )

    # case 9: deposit for next year, first period only
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=next_year,
                period=utils.get_educational_year_first_period(next_year),
                amount=3000,
            )
        ]
    )

    # case 10: deposit for next year, period = educational year
    institution = next(institutions_iter)
    deposits.extend(
        [
            educational_factories.EducationalDepositFactory.create(
                educationalInstitution=institution,
                educationalYear=next_year,
                period=utils.get_educational_year_full_period(next_year),
                amount=10_000,
            )
        ]
    )

    return deposits


def create_deposits(institutions: list[educational_models.EducationalInstitution]) -> None:
    years = create_years()

    for year, amount in zip(years, (20000, 30000, 40000, 50000)):
        for institution in institutions:
            ministry = MINISTRY_BY_UAI.get(institution.institutionId, educational_models.Ministry.EDUCATION_NATIONALE)
            educational_factories.EducationalDepositFactory.create(
                ministry=ministry,
                educationalInstitution=institution,
                educationalYear=year,
                amount=amount,
                isFinal=(year.beginningDate <= date_utils.get_naive_utc_now()),
            )


def create_years() -> tuple[educational_models.EducationalYear, ...]:
    two_years_ago = educational_factories.create_educational_year(
        date_utils.get_naive_utc_now() - datetime.timedelta(days=731)
    )
    last_year = educational_factories.create_educational_year(
        date_utils.get_naive_utc_now() - datetime.timedelta(days=365)
    )
    current_year = educational_factories.create_educational_year(date_utils.get_naive_utc_now())
    next_year = educational_factories.create_educational_year(
        date_utils.get_naive_utc_now() + datetime.timedelta(days=365)
    )
    return two_years_ago, last_year, current_year, next_year
