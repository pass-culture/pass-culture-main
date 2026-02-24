from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from flask import Flask

from pcapi.core.educational import models
from pcapi.core.educational.adage.backends.logger import BASE_ADAGE_PARTNER
from pcapi.core.educational.api.institution import ImportDepositPeriodOption
from pcapi.core.educational.schemas import AdageCulturalPartners

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.core.educational.api.institution.import_deposit_institution_csv")
def test_import_deposit_csv(mock_import: MagicMock, app: Flask):
    import pcapi

    args = (
        "--year",
        "2020",
        "--ministry",
        "EDUCATION_NATIONALE",
        "--period-option",
        "EDUCATIONAL_YEAR_FIRST_PERIOD",
        "--filename",
        "test.csv",
    )
    run_command(app, "import_deposit_csv", *args, raise_on_error=True)

    mock_import.assert_called_once_with(
        path=str(Path(pcapi.__file__).parent / "scripts" / "flask" / "test.csv"),
        year=2020,
        ministry=models.Ministry.EDUCATION_NATIONALE,
        period_option=ImportDepositPeriodOption.EDUCATIONAL_YEAR_FIRST_PERIOD,
        credit_update="replace",
        ministry_conflict="keep",
        program_name=None,
        final=False,
    )


@patch("pcapi.core.educational.api.adage.synchronize_adage_partners")
@patch("pcapi.core.educational.api.adage.get_cultural_partners")
def test_synchronize_adage_cultural_partners(mock_partners: MagicMock, mock_sync: MagicMock, app: Flask):
    adage_partners = AdageCulturalPartners(partners=[BASE_ADAGE_PARTNER])
    mock_partners.return_value = adage_partners

    run_command(app, "synchronize_adage_cultural_partners", raise_on_error=True)

    mock_partners.assert_called_once()
    mock_sync.assert_called_once_with(adage_partners=adage_partners.partners, apply=False)

    assert app.redis_client.get("synchronize_adage_cultural_partners:active_offerer_sirens") is not None


@patch("pcapi.core.educational.api.adage.synchronize_adage_ids_on_offerers")
@patch("pcapi.core.educational.api.adage.get_cultural_partners")
def test_synchronize_offerers_from_adage_cultural_partners(mock_partners: MagicMock, mock_sync: MagicMock, app: Flask):
    adage_partners = AdageCulturalPartners(partners=[BASE_ADAGE_PARTNER])
    mock_partners.return_value = adage_partners

    run_command(app, "synchronize_offerers_from_adage_cultural_partners", raise_on_error=True)

    mock_partners.assert_called_once()
    mock_sync.assert_called_once_with(adage_partners.partners)
