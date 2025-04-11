import datetime

import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.scripts.add_program_timespan import main as script_main
from pcapi.utils import db as db_utils


pytestmark = pytest.mark.usefixtures("db_session")


def format_datetime(dt: datetime.datetime) -> str:
    """Format datetime to match the database format."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def test_update_institutions_timespan_for_new_institutions():
    program = educational_factories.EducationalInstitutionProgramFactory(
        name=educational_models.PROGRAM_MARSEILLE_EN_GRAND
    )
    institution = educational_factories.EducationalInstitutionFactory(institutionId="0131208T")
    association = educational_factories.EducationalInstitutionProgramAssociationFactory(
        institution=institution,
        program=program,
    )
    start_date = datetime.datetime(2025, 9, 1)

    script_main.update_institutions_timespan(
        ["0131208T"],
        program,
        start_date,
        None,
    )

    assert association.timespan == db_utils.make_timerange(start_date, None)


def test_update_institutions_timespan_for_leaving_institutions():
    program = educational_factories.EducationalInstitutionProgramFactory(
        name=educational_models.PROGRAM_MARSEILLE_EN_GRAND
    )
    institution = educational_factories.EducationalInstitutionFactory(institutionId="0130868Y")
    association = educational_factories.EducationalInstitutionProgramAssociationFactory(
        institution=institution,
        program=program,
    )
    start_date = datetime.datetime(2025, 9, 1)  # Using a fixed date instead of MEG_BEGINNING_DATE
    end_date = datetime.datetime(2026, 8, 31)

    script_main.update_institutions_timespan(
        ["0130868Y"],
        program,
        start_date,
        end_date,
    )

    assert association.timespan == db_utils.make_timerange(start_date, end_date)
