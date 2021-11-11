import pytest

from pcapi.core.finance import models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class MagicEnumInBusinessUnitTest:
    def test_set_and_get(self):
        bu = models.BusinessUnit(name="unit", siret="1234")
        db.session.add(bu)
        db.session.commit()
        assert bu.cashflowFrequency == models.Frequency.EVERY_TWO_WEEKS
