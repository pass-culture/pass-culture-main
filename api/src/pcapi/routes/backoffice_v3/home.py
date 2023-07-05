import typing

from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models import offer_mixin

from . import blueprint
from . import utils


REDIRECT_AFTER_LOGIN_COOKIE_NAME = "redirect_after_login"


def _get_pending_offers_stats() -> dict[str, typing.Any]:
    pending_individual_offers_query = (
        sa.select(sa.func.count(offers_models.Offer.id))
        .select_from(offers_models.Offer)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(
            offers_models.Offer.validation == offer_mixin.OfferValidationStatus.PENDING,
            offerers_models.Offerer.isValidated,
        )
    )
    pending_collective_offers_query = (
        sa.select(sa.func.count(educational_models.CollectiveOffer.id))
        .select_from(educational_models.CollectiveOffer)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(
            educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
            offerers_models.Offerer.isValidated,
        )
    )
    pending_collective_templates_query = (
        sa.select(sa.func.count(educational_models.CollectiveOfferTemplate.id))
        .select_from(educational_models.CollectiveOfferTemplate)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(
            educational_models.CollectiveOfferTemplate.validation == offer_mixin.OfferValidationStatus.PENDING,
            offerers_models.Offerer.isValidated,
        )
    )

    stats = db.session.execute(
        sa.select(
            pending_individual_offers_query.scalar_subquery().label("pending_individual_offers_count"),
            pending_collective_offers_query.scalar_subquery().label("pending_collective_offers_count"),
            pending_collective_templates_query.scalar_subquery().label("pending_collective_templates_count"),
        )
    ).one()

    return dict(stats)


@blueprint.backoffice_v3_web.route("/", methods=["GET"])
def home() -> utils.BackofficeResponse:
    if not current_user or current_user.is_anonymous:
        return render_template("home/login.html")

    redirect_url = request.cookies.get(REDIRECT_AFTER_LOGIN_COOKIE_NAME, "")
    if redirect_url:
        if redirect_url.startswith("/"):
            response = redirect(redirect_url)
            response.delete_cookie(REDIRECT_AFTER_LOGIN_COOKIE_NAME)
            return response

    data = {}
    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        data = {
            "pending_individual": {
                "search-0-search_field": "VALIDATION",
                "search-0-operator": "IN",
                "search-0-validation": "PENDING",
                "only_validated_offerers": "on",
                "sort": "dateCreated",
                "order": "desc",
                "limit": "1000",
            }
        }
        data.update(_get_pending_offers_stats())

    return render_template("home/home.html", **data)
