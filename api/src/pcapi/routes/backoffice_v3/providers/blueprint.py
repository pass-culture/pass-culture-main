from flask import flash
from flask import redirect
from flask import render_template
import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models

from .. import utils


providers_blueprint = utils.child_backoffice_blueprint(
    "providers",
    __name__,
    url_prefix="/pro/providers",
    permission=perm_models.Permissions.MANAGE_PROVIDERS,
)


@providers_blueprint.route("", methods=["GET"])
def get_providers() -> utils.BackofficeResponse:
    providers = (
        providers_models.Provider.query.options(
            sa.orm.joinedload(providers_models.Provider.offererProvider)
            .joinedload(offerers_models.OffererProvider.offerer)
            .load_only(offerers_models.Offerer.city, offerers_models.Offerer.postalCode, offerers_models.Offerer.siren)
        )
        .options(sa.orm.joinedload(providers_models.Provider.apiKeys).load_only(offerers_models.ApiKey.id))
        .all()
    )
    return render_template("providers/get.html", providers=providers)
