from flask import render_template
from werkzeug.exceptions import NotFound

from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.permissions import models as perm_models
import pcapi.utils.regions as regions_utils

from . import utils


get_offerer_blueprint = utils.child_backoffice_blueprint(
    "get_offerer",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>",
    permission=perm_models.Permissions.READ_PUBLIC_ACCOUNT,
)


@get_offerer_blueprint.route("", methods=["GET"])
def get_offerer(offerer_id: int) -> utils.Response:
    offerer_basic_info = offerers_api.get_offerer_basic_info(offerer_id)

    if not offerer_basic_info:
        raise NotFound()

    region = ""
    if offerer_basic_info.postalCode:
        region = regions_utils.get_region_name_from_postal_code(offerer_basic_info.postalCode)

    return render_template("offerer/get.html", offerer=offerer_basic_info, region=region)


@get_offerer_blueprint.route("/stats", methods=["GET"])
def get_offerer_stats(offerer_id: int) -> utils.Response:
    total_revenue = offerers_api.get_offerer_total_revenue(offerer_id)
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id)

    return render_template(
        "offerer/get/stats.html",
        stats={
            "total_revenue": total_revenue,
            "active_individual_offers": offers_stats.individual_offers.get("active", 0)
            if offers_stats.individual_offers
            else 0,
            "active_collective_offers": offers_stats.collective_offers.get("active", 0)
            if offers_stats.collective_offers
            else 0,
            "inactive_individual_offers": offers_stats.individual_offers.get("inactive", 0)
            if offers_stats.individual_offers
            else 0,
            "inactive_collective_offers": offers_stats.collective_offers.get("inactive", 0)
            if offers_stats.collective_offers
            else 0,
        },
    )


@get_offerer_blueprint.route("/history", methods=["GET"])
def get_offerer_history(offerer_id: int) -> utils.Response:
    actions = history_repository.find_all_actions_by_offerer(offerer_id)

    return render_template("offerer/get/history.html", history={"actions": actions})
