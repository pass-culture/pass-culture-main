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

from pcapi import settings
from pcapi.connectors.dms.api import DMSGraphQLClient
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.history.models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.permissions.models as perm_models
from pcapi.models.api_errors import ApiErrors
import pcapi.routes.serialization.base as serialize_base
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id
import pcapi.utils.regions as regions_utils
from pcapi.utils.string import to_camelcase

from . import utils
from .forms import empty as empty_forms
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
            sa.orm.joinedload(offerers_models.Venue.venueLabel),
            sa.orm.joinedload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
            sa.orm.joinedload(offerers_models.Venue.collectiveDmsApplications).load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.depositDate,
                educational_models.CollectiveDmsApplication.lastChangeDate,
            ),
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
        # validation date of the dossier
        lastChangeDate=datetime.fromisoformat(
            dms_stats["dossier"]["dateDerniereModification"]  # pylint: disable=unsubscriptable-object
        ),
        url=f"https://www.demarches-simplifiees.fr/procedures/{settings.DMS_VENUE_PROCEDURE_ID_V4}/dossiers/{dms_application_id}",
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
    venue: offerers_models.Venue, edit_venue_form: forms.EditVirtualVenueForm | None = None
) -> str:
    dms_application_id = venue.bankInformation.applicationId if venue.bankInformation else None
    dms_stats = get_dms_stats(dms_application_id)
    region = regions_utils.get_region_name_from_postal_code(venue.postalCode) if venue.postalCode else ""

    if not edit_venue_form:
        if venue.isVirtual:
            edit_venue_form = forms.EditVirtualVenueForm(
                booking_email=venue.bookingEmail,
                phone_number=venue.contact.phone_number if venue.contact else None,
            )
        else:
            edit_venue_form = forms.EditVenueForm(
                venue=venue,
                name=venue.name,
                public_name=venue.publicName,
                siret=venue.siret,
                city=venue.city,
                postal_address_autocomplete=f"{venue.address}, {venue.postalCode} {venue.city}"
                if venue.address is not None and venue.city is not None and venue.postalCode is not None
                else None,
                postal_code=venue.postalCode,
                address=venue.address,
                booking_email=venue.bookingEmail,
                phone_number=venue.contact.phone_number if venue.contact else None,
                is_permanent=venue.isPermanent,
                latitude=venue.latitude,
                longitude=venue.longitude,
            )
        edit_venue_form.tags.choices = [(criterion.id, criterion.name) for criterion in venue.criteria]

    delete_venue_form = empty_forms.EmptyForm()

    return render_template(
        "venue/get.html",
        venue=venue,
        edit_venue_form=edit_venue_form,
        region=region,
        has_reimbursement_point=has_reimbursement_point(venue),
        dms_stats=dms_stats,
        delete_venue_form=delete_venue_form,
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
    dst = url_for("backoffice_v3_web.venue.comment_venue", venue_id=venue.id)

    return render_template(
        "venue/get/details.html",
        venue=venue,
        actions=actions,
        dst=dst,
        form=form,
    )


@venue_blueprint.route("/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_PRO_ENTITY)
def delete_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)
    venue_name = venue.name

    emails = offerers_repository.get_emails_by_venue(venue)

    try:
        delete_cascade_venue_by_id(venue.id)
    except offerers_exceptions.CannotDeleteVenueWithBookingsException:
        flash("Impossible d'effacer un lieu pour lequel il existe des réservations", "warning")
        return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue.id), code=303)
    except offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException:
        flash("Impossible d'effacer un lieu utilisé comme point de valorisation d'un autre lieu", "warning")
        return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue.id), code=303)
    except offerers_exceptions.CannotDeleteVenueUsedAsReimbursementPointException:
        flash("Impossible d'effacer un lieu utilisé comme point de remboursement d'un autre lieu", "warning")
        return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue.id), code=303)

    for email in emails:
        external_attributes_api.update_external_pro(email)

    flash(f"Le lieu {venue_name} ({venue_id}) a été supprimé", "success")
    return redirect(url_for("backoffice_v3_web.search_pro"), code=303)


@venue_blueprint.route("/update", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_venue(venue_id: int) -> utils.BackofficeResponse:
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
        return render_venue_details(venue, form), 400

    if not venue.isVirtual and bool(venue.siret) != bool(form.siret.data):
        flash(
            f"Vous ne pouvez pas {'créer' if form.siret.data else 'retirer'} le SIRET d'un lieu. Contactez le support pro.",
            "warning",
        )
        return render_venue_details(venue, form), 400

    attrs = {
        to_camelcase(field.name): field.data
        for field in form
        if field.name and hasattr(venue, to_camelcase(field.name))
    }

    if form.phone_number.data or venue.contact:
        contact_data = serialize_base.VenueContactModel(
            phone_number=form.phone_number.data,
            # Use existing values, if any, to ensure that no data (website
            # for example) will be erased by mistake
            email=venue.contact.email if venue.contact else None,
            website=venue.contact.website if venue.contact else None,
            social_medias=venue.contact.social_medias if venue.contact else None,
        )
    else:
        contact_data = None

    criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(form.tags.data)).all()

    try:
        offerers_api.update_venue(
            venue, author=current_user, contact_data=contact_data, criteria=criteria, admin_update=True, **attrs
        )
    except ApiErrors as api_errors:
        for error_key, error_details in api_errors.errors.items():
            for error_detail in error_details:
                flash(f"[{error_key}] {error_detail}", "warning")
        return render_venue_details(venue, form), 400

    flash("Les informations ont bien été mises à jour", "success")
    return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue.id), code=303)


@venue_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)

    form = forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
    else:
        offerers_api.add_comment_to_venue(venue, current_user, comment=form.comment.data)
        flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue_id), code=303)
