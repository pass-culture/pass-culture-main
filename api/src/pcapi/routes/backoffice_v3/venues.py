from flask import render_template

import pcapi.core.offerers.models as offerers_models
import pcapi.core.permissions.models as perm_models

from . import utils


venue_blueprint = utils.child_backoffice_blueprint(
    "venue",
    __name__,
    url_prefix="/pro/venue/<int:venue_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@venue_blueprint.route("", methods=["GET"])
def get(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)
    return render_template("venue/get.html", row=venue)
