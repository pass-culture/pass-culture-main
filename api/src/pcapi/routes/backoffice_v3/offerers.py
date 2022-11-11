import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from werkzeug.exceptions import NotFound

from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.utils.date import format_into_utc_date
import pcapi.utils.regions as regions_utils

from . import utils
from .forms import offerer as offerer_forms
from .serialization import offerers as serialization


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

    bank_information_status = serialization.OffererBankInformationStatus(
        ok=bank_informations_ok, ko=bank_informations_ko
    )

    return render_template(
        "offerer/get.html",
        offerer=offerer,
        region=regions_utils.get_region_name_from_postal_code(offerer.postalCode),
        bank_information_status=bank_information_status,
        is_collective_eligible=basic_info.is_collective_eligible,
    )


def get_stats_data(offerer_id: int) -> serialization.OfferersStats:
    offers_stats = offerers_api.get_offerer_offers_stats(offerer_id)
    stats = serialization.OffersStats(
        active=serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("active", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("active", 0) if offers_stats.collective_offers else 0,
        ),
        inactive=serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("inactive", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("inactive", 0) if offers_stats.collective_offers else 0,
        ),
    )

    total_revenue = offerers_api.get_offerer_total_revenue(offerer_id)

    return serialization.OfferersStats(stats=stats, total_revenue=total_revenue)


@offerer_blueprint.route("/stats", methods=["GET"])
def get_stats(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    data = get_stats_data(offerer.id)
    return render_template(
        "offerer/get/stats.html",
        stats=data.stats,
        total_revenue=data.total_revenue,
    )


def get_offerer_history_data(offerer_id: int) -> typing.Sequence[serialization.HistoryItem]:
    actions = history_repository.find_all_actions_by_offerer(offerer_id)
    return [
        serialization.HistoryItem(
            type=action.actionType.value,
            date=format_into_utc_date(action.actionDate) if action.actionDate else None,
            authorId=action.authorUserId,
            authorName=action.authorUser.publicName if action.authorUser else None,
            comment=action.comment,
            accountId=action.userId,
            accountName=action.user.publicName if action.user else None,
        )
        for action in actions
    ]


@offerer_blueprint.route("/history", methods=["GET"])
def get_offerer_history(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    history = get_offerer_history_data(offerer_id)
    can_add_comment = utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
    return render_template(
        "offerer/get/details.html", offerer=offerer, history=history, can_add_comment=can_add_comment
    )


offerer_comment_blueprint = utils.child_backoffice_blueprint(
    "offerer_comment",
    __name__,
    url_prefix="/pro/offerer/<int:offerer_id>/comment",
    permission=perm_models.Permissions.MANAGE_PRO_ENTITY,
)


@offerer_comment_blueprint.route("", methods=["GET"])
def new_comment(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)
    form = offerer_forms.CommentForm()
    return render_template("offerer/comment.html", form=form, offerer=offerer)


@offerer_comment_blueprint.route("", methods=["POST"])
def comment_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = offerers_models.Offerer.query.get_or_404(offerer_id)

    form = offerer_forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return render_template("offerer/comment.html", form=form, offerer=offerer), 400

    offerers_api.add_comment_to_offerer(offerer_id, current_user, comment=form.comment.data)
    flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_v3_web.offerer.get", offerer_id=offerer_id), code=303)
