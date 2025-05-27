from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.flask_app import app
from pcapi.repository import db


def create_missing_offerer_provider() -> None:
    offerer = db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == 59703).one()
    provider = db.session.query(providers_models.Provider).filter(providers_models.Provider.id == 2120).one()
    offerer_provider = offerers_models.OffererProvider(offerer=offerer, provider=provider)
    db.session.add(offerer_provider)
    db.session.commit()


if __name__ == "__main__":
    app.app_context().push()
    create_missing_offerer_provider()
