from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
import sqlalchemy as sa

from pcapi.connectors.dms import models as dms_models
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import offer_mixin

from . import blueprint
from . import utils


REDIRECT_AFTER_LOGIN_COOKIE_NAME = "redirect_after_login"

# Tags are created from the backoffice, so there is nothing in the code which forces this tag to exist.
# Let's hardcode the name given in production (also created in sandbox for testing purpose).
CONFORMITE_TAG_NAME = "conformité"


def _get_fraud_stats() -> list[sa.sql.elements.Label]:
    pending_individual_offers_subquery = (
        sa.select(sa.func.count(offers_models.Offer.id))
        .select_from(offers_models.Offer)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(
            offers_models.Offer.validation == offer_mixin.OfferValidationStatus.PENDING,
            offerers_models.Offerer.isValidated,
        )
        .scalar_subquery()
        .label("pending_individual_offers_count")
    )
    pending_collective_offers_subquery = (
        sa.select(sa.func.count(educational_models.CollectiveOffer.id))
        .select_from(educational_models.CollectiveOffer)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(
            educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
            offerers_models.Offerer.isValidated,
        )
        .scalar_subquery()
        .label("pending_collective_offers_count")
    )
    pending_collective_templates_subquery = (
        sa.select(sa.func.count(educational_models.CollectiveOfferTemplate.id))
        .select_from(educational_models.CollectiveOfferTemplate)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(
            educational_models.CollectiveOfferTemplate.validation == offer_mixin.OfferValidationStatus.PENDING,
            offerers_models.Offerer.isValidated,
        )
        .scalar_subquery()
        .label("pending_collective_templates_count")
    )

    pending_conformite_offerers_count_subquery = (
        sa.select(sa.func.count(offerers_models.Offerer.id))
        .select_from(offerers_models.Offerer)
        .join(offerers_models.Offerer.tags)
        .filter(offerers_models.Offerer.isPending, offerers_models.OffererTag.name == CONFORMITE_TAG_NAME)
        .scalar_subquery()
        .label("pending_conformite_offerers_count")
    )
    conformite_tag_id_subquery = (
        sa.select(offerers_models.OffererTag.id)
        .select_from(offerers_models.OffererTag)
        .filter(offerers_models.OffererTag.name == CONFORMITE_TAG_NAME)
        .scalar_subquery()
        .label("conformite_tag_id")
    )

    return [
        pending_individual_offers_subquery,
        pending_collective_offers_subquery,
        pending_collective_templates_subquery,
        pending_conformite_offerers_count_subquery,
        conformite_tag_id_subquery,
    ]


def _get_user_account_update_requests_stats() -> list[sa.sql.elements.Label]:
    pending_unassigned_update_requests_count_subquery = (
        sa.select(sa.func.count(users_models.UserAccountUpdateRequest.id))
        .select_from(users_models.UserAccountUpdateRequest)
        .filter(
            users_models.UserAccountUpdateRequest.status.in_(
                (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going)
            ),
            users_models.UserAccountUpdateRequest.lastInstructorId.is_(None),
        )
        .label("pending_unassigned_update_requests_count")
    )

    pending_self_update_requests_count_subquery = (
        sa.select(sa.func.count(users_models.UserAccountUpdateRequest.id))
        .select_from(users_models.UserAccountUpdateRequest)
        .filter(
            users_models.UserAccountUpdateRequest.status.in_(
                (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going)
            ),
            users_models.UserAccountUpdateRequest.lastInstructorId == current_user.id,
        )
        .scalar_subquery()
        .label("pending_self_update_requests_count")
    )

    return [pending_unassigned_update_requests_count_subquery, pending_self_update_requests_count_subquery]


@blueprint.backoffice_web.route("/", methods=["GET"])
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
    subqueries = []

    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        subqueries += _get_fraud_stats()

    if (
        utils.has_current_user_permission(perm_models.Permissions.MANAGE_ACCOUNT_UPDATE_REQUEST)
        and current_user.backoffice_profile.dsInstructorId
    ):
        subqueries += _get_user_account_update_requests_stats()

    if subqueries:
        stats = db.session.execute(sa.select(*subqueries)).one()
        data.update(stats._mapping)

    return render_template("home/home.html", **data)
