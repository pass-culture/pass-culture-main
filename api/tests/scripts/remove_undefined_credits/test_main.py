import pytest

from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.models import Mediation
from pcapi.models import db
from pcapi.scripts.remove_undefined_credits.main import delete_undefined_credits


@pytest.mark.usefixtures("clean_database")
def test_remove_undefined_credits_script():
    MediationFactory(credit="undefined")
    MediationFactory(credit="valid credit")

    delete_undefined_credits()
    db.session.commit()

    assert Mediation.query.filter(Mediation.credit == "undefined").count() == 0
    assert Mediation.query.filter(Mediation.credit.is_(None)).count() == 1
