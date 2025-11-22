from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db


def test_import_sandbox(run_command):
    run_command("import_sandbox", "--name", "beneficiaries", "--name", "accessibility_offers", raise_on_error=True)
    assert db.session.query(offers_models.Offer).filter(offers_models.Offer.name.endswith("Access42")).count() == 4
    assert (
        db.session.query(offerers_models.Venue).filter(offerers_models.Venue.name == "Lieu - Audit Access42").count()
        == 1
    )
    assert (
        db.session.query(users_models.User)
        .filter(users_models.User.email == "pctest.non-beneficiary.17-going-on-18.v1@example.com")
        .count()
        == 1
    )
