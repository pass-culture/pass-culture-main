from datetime import datetime

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
import gql.transport.exceptions as gql_exceptions
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.connectors.dms.api import DMSGraphQLClient
import pcapi.core.history.models as history_models
from pcapi.core.offerers import api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.permissions.models as perm_models
from pcapi.models.api_errors import ApiErrors
import pcapi.routes.serialization.base as serialize_base
import pcapi.utils.regions as regions_utils

from . import utils
from .forms import venue as forms
from .serialization import offerers as offerers_serialization
from .serialization import venues as serialization


venue_blueprint = utils.child_backoffice_blueprint(
    "venue",
    __name__,
    url_prefix="/pro/venue/<int:venue_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def get_venue(venue_id: int) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .options(
            sa.orm.joinedload(offerers_models.Venue.managingOfferer),
            sa.orm.joinedload(offerers_models.Venue.contact),
            sa.orm.joinedload(offerers_models.Venue.bankInformation),
            sa.orm.joinedload(offerers_models.Venue.reimbursement_point_links),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def get_dms_stats(dms_application_id: int | None) -> serialization.VenueDmsStats | None:
    if not dms_application_id:
        return None

    try:
        dms_stats = DMSGraphQLClient().get_bank_info_status(dms_application_id)
    except (gql_exceptions.TransportError, gql_exceptions.TransportQueryError):
        return None

    return serialization.VenueDmsStats(
        status=dms_stats["dossier"]["state"],  # pylint: disable=unsubscriptable-object
        subscriptionDate=datetime.fromisoformat(
            dms_stats["dossier"]["dateDepot"]  # pylint: disable=unsubscriptable-object
        ),
        url=f"https://www.demarches-simplifiees.fr/dossiers/{dms_application_id}",
    )


def has_reimbursement_point(
    venue: offerers_models.Venue,
) -> bool:
    now = datetime.utcnow()

    for link in venue.reimbursement_point_links:
        lower = link.timespan.lower
        upper = link.timespan.upper

        if lower <= now and (not upper or now <= upper):
            return True

    return False


def render_venue_details(
    venue: offerers_models.Venue, form: forms.EditVirtualVenueForm | None = None
) -> utils.BackofficeResponse:
    dms_application_id = venue.bankInformation.applicationId if venue.bankInformation else None
    dms_stats = get_dms_stats(dms_application_id)
    region = regions_utils.get_region_name_from_postal_code(venue.postalCode) if venue.postalCode else ""

    if not form:
        if venue.isVirtual:
            form = forms.EditVirtualVenueForm(
                email=venue.contact.email if venue.contact else None,
                phone_number=venue.contact.phone_number if venue.contact else None,
            )
        else:
            form = forms.EditVenueForm(
                venue=venue,
                siret=venue.siret,
                city=venue.city,
                postalCode=venue.postalCode,
                address=venue.address,
                email=venue.contact.email if venue.contact else None,
                phone_number=venue.contact.phone_number if venue.contact else None,
                isPermanent=venue.isPermanent,
            )

    return render_template(
        "venue/get.html",
        venue=venue,
        form=form,
        region=region,
        has_reimbursement_point=has_reimbursement_point(venue),
        dms_stats=dms_stats,
    )


@venue_blueprint.route("", methods=["GET"])
def get(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue(venue_id)
    return render_venue_details(venue)


def get_stats_data(venue_id: int) -> serialization.VenueStats:
    offers_stats = offerers_api.get_venue_offers_stats(venue_id)

    if not offers_stats:
        raise NotFound()

    stats = serialization.VenueOffersStats(
        active=offerers_serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("active", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("active", 0) if offers_stats.collective_offers else 0,
        ),
        inactive=offerers_serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("inactive", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("inactive", 0) if offers_stats.collective_offers else 0,
        ),
        lastSync=serialization.LastOfferSyncStats(
            date=offers_stats.lastSyncDate,
            provider=offers_stats.name,
        ),
    )

    total_revenue = offerers_api.get_venue_total_revenue(venue_id)

    return serialization.VenueStats(stats=stats, total_revenue=total_revenue)


@venue_blueprint.route("/stats", methods=["GET"])
def get_stats(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)
    data = get_stats_data(venue.id)

    return render_template(
        "venue/get/stats.html",
        venue=venue,
        stats=data.stats,
        total_revenue=data.total_revenue,
    )


def get_venue_with_history(venue_id: int) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .options(
            sa.orm.joinedload(offerers_models.Venue.action_history).joinedload(history_models.ActionHistory.user),
            sa.orm.joinedload(offerers_models.Venue.action_history).joinedload(history_models.ActionHistory.authorUser),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


@venue_blueprint.route("/details", methods=["GET"])
def get_details(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue_with_history(venue_id)
    actions = sorted(venue.action_history, key=lambda action: action.actionDate, reverse=True)

    form = forms.CommentForm()
    dst = url_for("backoffice_v3_web.manage_venue.comment", venue_id=venue.id)

    return render_template(
        "venue/get/details.html",
        venue=venue,
        actions=actions,
        dst=dst,
        form=form,
    )


manage_venue_blueprint = utils.child_backoffice_blueprint(
    "manage_venue",
    __name__,
    url_prefix="/pro/venue/<int:venue_id>/",
    permission=perm_models.Permissions.MANAGE_PRO_ENTITY,
)


@manage_venue_blueprint.route("/update", methods=["POST"])
def update(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue(venue_id)

    if venue.isVirtual:
        form = forms.EditVirtualVenueForm()
    else:
        form = forms.EditVenueForm(venue)

    if not form.validate():
        msg = Markup(
            """
            <button type="button"
                    class="btn"
                    data-bs-toggle="modal"
                    data-bs-target="#venue-edit-details">
                Les données envoyées comportent des erreurs. Afficher
            </button>
            """
        ).format()
        flash(msg, "warning")
        return render_venue_details(venue, form)

    attrs = {field.name: field.data for field in form if field.name and hasattr(venue, field.name)}
    contact_attrs = {"email": form.email.data, "phone_number": form.phone_number.data}

    contact_data = serialize_base.VenueContactModel(**contact_attrs)

    try:
        offerers_api.update_venue(venue, contact_data, admin_update=True, **attrs)
    except ApiErrors as api_errors:
        for error_key, error_details in api_errors.errors.items():
            for error_detail in error_details:
                flash(f"[{error_key}] {error_detail}", "warning")
        return render_venue_details(venue, form)

    flash("Les informations ont bien été mises à jour", "success")
    return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue.id), code=303)


@manage_venue_blueprint.route("", methods=["POST"])
def comment(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)

    form = forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return render_template("venue/comment.html", form=form, venue=venue), 400

    offerers_api.add_comment_to_venue(venue, current_user, comment=form.comment.data)
    flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue_id), code=303)
