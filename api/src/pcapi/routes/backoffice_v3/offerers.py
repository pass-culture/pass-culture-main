from flask import render_template
from werkzeug.exceptions import NotFound

from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
import pcapi.utils.regions as regions_utils

from . import utils
from .serialization import offerers as offerers_serialization


offerer_blueprint = utils.child_backoffice_blueprint(
    "offerer",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@offerer_blueprint.route("", methods=["GET"])
def get(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    basic_info = offerers_api.get_offerer_basic_info(offerer_id)

    if not basic_info:
        raise NotFound()

    bank_informations = basic_info.bank_informations or {}
    bank_informations_ok = bank_informations.get("ok", 0)
    bank_informations_ko = bank_informations.get("ko", 0)

    bank_information_status = offerers_serialization.OffererBankInformationStatus(
        ok=bank_informations_ok, ko=bank_informations_ko
    )

    return render_template(
        "offerer/get.html",
        offerer=offerer,
        region=regions_utils.get_region_name_from_postal_code(offerer.postalCode),
        bank_information_status=bank_information_status,
        is_collective_eligible=basic_info.is_collective_eligible,
    )


@offerer_blueprint.route("/stats", methods=["GET"])
def get_offerer_stats(offerer_id: int) -> utils.BackofficeResponse:
    total_revenue = offerers_api.get_offerer_total_revenue(offerer_id)
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id)

    stats = offerers_serialization.OffersStats(
        active=offerers_serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("active", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("active", 0) if offers_stats.collective_offers else 0,
        ),
        inactive=offerers_serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("inactive", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("inactive", 0) if offers_stats.collective_offers else 0,
        ),
    )

    return render_template(
        "offerer/get/stats.html",
        total_revenue=total_revenue,
        stats=stats,
    )


@offerer_blueprint.route("/history", methods=["GET"])
def get_offerer_history(offerer_id: int) -> utils.BackofficeResponse:
    actions = history_repository.find_all_actions_by_offerer(offerer_id)

    return render_template("offerer/get/history.html", history={"actions": actions})
