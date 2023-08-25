from datetime import datetime
from functools import partial
from functools import reduce
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import gql.transport.exceptions as gql_exceptions
from markupsafe import Markup
import requests.exceptions
import sqlalchemy as sa
import urllib3.exceptions
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.connectors.dms.api import DMSGraphQLClient
from pcapi.core import search
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
import pcapi.core.history.models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.permissions.models as perm_models
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.routes.backoffice_v3 import autocomplete
from pcapi.routes.backoffice_v3 import utils
from pcapi.routes.backoffice_v3.forms import empty as empty_forms
from pcapi.routes.backoffice_v3.forms import search as search_forms
from pcapi.routes.backoffice_v3.serialization.search import TypeOptions
import pcapi.routes.serialization.base as serialize_base
import pcapi.utils.regions as regions_utils
from pcapi.utils.regions import get_department_codes_for_region
from pcapi.utils.string import to_camelcase

from . import form as forms
from . import serialization


venue_blueprint = utils.child_backoffice_blueprint(
    "venue",
    __name__,
    url_prefix="/pro/venue",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def _can_edit_siret() -> bool:
    return utils.has_current_user_permission(perm_models.Permissions.MOVE_SIRET)


def _get_venues(form: forms.GetVenuesListForm) -> list[offerers_models.Venue]:
    base_query = offerers_models.Venue.query.options(
        sa.orm.load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
            offerers_models.Venue.publicName,
            offerers_models.Venue.dateCreated,
            offerers_models.Venue.postalCode,
            offerers_models.Venue.departementCode,
            offerers_models.Venue.isPermanent,
        ),
        sa.orm.joinedload(offerers_models.Venue.managingOfferer).load_only(offerers_models.Offerer.name),
        sa.orm.joinedload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
        sa.orm.joinedload(offerers_models.Venue.venueLabel).load_only(offerers_models.VenueLabel.label),
    )

    if form.venue_label.data:
        base_query = base_query.filter(offerers_models.Venue.venueLabelId.in_(form.venue_label.raw_data))

    if form.department.data:
        base_query = base_query.filter(offerers_models.Venue.departementCode.in_(form.department.data))

    if form.regions.data:
        department_codes: list[str] = []
        for region in form.regions.data:
            department_codes += get_department_codes_for_region(region)
        base_query = base_query.filter(offerers_models.Venue.departementCode.in_(department_codes))

    if form.type.data:
        base_query = base_query.filter(offerers_models.Venue.venueTypeCode.in_(form.type.data))

    if form.criteria.data:
        base_query = base_query.outerjoin(offerers_models.Venue.criteria).filter(
            criteria_models.Criterion.id.in_(form.criteria.data)
        )

    if form.order.data:
        base_query = base_query.order_by(getattr(getattr(offerers_models.Venue, "id"), form.order.data)())
    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1).all()


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
    except (
        gql_exceptions.TransportError,
        gql_exceptions.TransportQueryError,
        urllib3.exceptions.HTTPError,
        requests.exceptions.RequestException,
    ):
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
                venue_type_code=venue.venueTypeCode.name,
            )
            edit_venue_form.siret.flags.disabled = not _can_edit_siret()
        edit_venue_form.tags.choices = [(criterion.id, criterion.name) for criterion in venue.criteria]

    delete_venue_form = empty_forms.EmptyForm()

    return render_template(
        "venue/get.html",
        search_form=search_forms.ProSearchForm(terms=request.args.get("terms"), pro_type=TypeOptions.VENUE),
        search_dst=url_for("backoffice_v3_web.search_pro"),
        venue=venue,
        edit_venue_form=edit_venue_form,
        region=region,
        has_reimbursement_point=has_reimbursement_point(venue),
        dms_stats=dms_stats,
        delete_venue_form=delete_venue_form,
        active_tab=request.args.get("active_tab", "history"),
    )


@venue_blueprint.route("", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def list_venues() -> utils.BackofficeResponse:
    form = forms.GetVenuesListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("venue/list.html", rows=[], form=form), 400

    if form.is_empty():
        return render_template("venue/list.html", rows=[], form=form)

    venues = _get_venues(form)

    if len(venues) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        venues = venues[: form.limit.data]

    autocomplete.prefill_criteria_choices(form.criteria)

    form_url = partial(url_for, ".list_venues", **form.raw_data)
    date_created_sort_url = form_url(order="desc" if form.order.data == "asc" else "asc")

    return render_template("venue/list.html", rows=venues, form=form, date_created_sort_url=date_created_sort_url)


@venue_blueprint.route("/<int:venue_id>", methods=["GET"])
def get(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue(venue_id)
    return render_venue_details(venue)


# mypy doesn't like nested dict
@typing.no_type_check
def get_stats_data(venue_id: int) -> dict:
    PLACEHOLDER = -1
    offers_stats = offerers_api.get_venue_offers_stats(venue_id, max_offer_count=1000)

    is_collective_too_big = offers_stats["collective_offer"]["active"] == -1
    is_collective_too_big = is_collective_too_big or offers_stats["collective_offer_template"]["active"] == -1
    is_individual_too_big = offers_stats["offer"]["active"] == -1

    stats = {
        "active": {},
        "inactive": {},
        "total_revenue": PLACEHOLDER,
        "placeholder": PLACEHOLDER,
    }

    if is_collective_too_big:
        stats["active"]["collective"] = PLACEHOLDER
        stats["inactive"]["collective"] = PLACEHOLDER
        stats["active"]["total"] = PLACEHOLDER
        stats["inactive"]["total"] = PLACEHOLDER
    else:
        stats["active"]["collective"] = (
            offers_stats["collective_offer"]["active"] + offers_stats["collective_offer_template"]["active"]
        )
        stats["inactive"]["collective"] = (
            offers_stats["collective_offer"]["inactive"] + offers_stats["collective_offer_template"]["inactive"]
        )
    if is_individual_too_big:
        stats["active"]["individual"] = PLACEHOLDER
        stats["inactive"]["individual"] = PLACEHOLDER
        stats["active"]["total"] = PLACEHOLDER
        stats["inactive"]["total"] = PLACEHOLDER
    else:
        stats["active"]["individual"] = offers_stats["offer"]["active"]
        stats["inactive"]["individual"] = offers_stats["offer"]["inactive"]

    if not (is_collective_too_big or is_individual_too_big):
        stats["active"]["total"] = stats["active"]["collective"] + stats["active"]["individual"]
        stats["inactive"]["total"] = stats["inactive"]["collective"] + stats["inactive"]["individual"]
        stats["total_revenue"] = offerers_api.get_venue_total_revenue(venue_id)

    return stats


def get_venue_bank_information(venue: offerers_models.Venue) -> serialization.VenueBankInformation:
    now = datetime.utcnow()
    reimbursement_point_name = None
    pricing_point_name = None
    bic = None
    iban = None
    reimbursement_point_url = None
    pricing_point_url = None
    current_pricing_point = next(
        (
            pricing_point_link.pricingPoint
            for pricing_point_link in venue.pricing_point_links
            if now in pricing_point_link.timespan
        ),
        None,
    )
    current_reimbursement_point = next(
        (
            reimbursement_point_link.reimbursementPoint
            for reimbursement_point_link in venue.reimbursement_point_links
            if now in reimbursement_point_link.timespan
        ),
        None,
    )

    if current_reimbursement_point:
        bic = current_reimbursement_point.bic
        iban = current_reimbursement_point.iban
        reimbursement_point_name = current_reimbursement_point.name

        if current_reimbursement_point.id != venue.id:
            reimbursement_point_url = url_for("backoffice_v3_web.venue.get", venue_id=current_reimbursement_point.id)

    if venue.siret:
        pricing_point_name = venue.name
    elif current_pricing_point is not None:
        pricing_point_name = current_pricing_point.name
        pricing_point_url = url_for("backoffice_v3_web.venue.get", venue_id=current_pricing_point.id)

    return serialization.VenueBankInformation(
        reimbursement_point_name=reimbursement_point_name,
        reimbursement_point_url=reimbursement_point_url,
        pricing_point_name=pricing_point_name,
        pricing_point_url=pricing_point_url,
        bic=bic,
        iban=iban,
    )


@venue_blueprint.route("/<int:venue_id>/stats", methods=["GET"])
def get_stats(venue_id: int) -> utils.BackofficeResponse:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .options(
            sa.orm.joinedload(offerers_models.Venue.pricing_point_links).joinedload(
                offerers_models.VenuePricingPointLink.pricingPoint
            ),
            sa.orm.joinedload(offerers_models.Venue.reimbursement_point_links)
            .joinedload(offerers_models.VenueReimbursementPointLink.reimbursementPoint)
            .load_only(offerers_models.Venue.name)
            .joinedload(offerers_models.Venue.bankInformation)
            .load_only(finance_models.BankInformation.bic, finance_models.BankInformation.iban),
            sa.orm.joinedload(offerers_models.Venue.bankInformation).load_only(
                finance_models.BankInformation.bic, finance_models.BankInformation.iban
            ),
        )
        .one_or_none()
    )

    data = get_stats_data(venue.id)
    bank_information = get_venue_bank_information(venue)
    return render_template(
        "venue/get/stats.html",
        venue=venue,
        stats=data,
        bank_information=bank_information,
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


@venue_blueprint.route("/<int:venue_id>/history", methods=["GET"])
def get_history(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue_with_history(venue_id)
    actions = sorted(venue.action_history, key=lambda action: action.actionDate, reverse=True)

    form = forms.CommentForm()
    dst = url_for("backoffice_v3_web.venue.comment_venue", venue_id=venue.id)

    return render_template(
        "venue/get/history.html",
        venue=venue,
        actions=actions,
        dst=dst,
        form=form,
    )


@venue_blueprint.route("/<int:venue_id>/invoices", methods=["GET"])
def get_invoices(venue_id: int) -> utils.BackofficeResponse:
    # Find current reimbursement point for the current venue, if different from itself
    current_link = (
        offerers_models.VenueReimbursementPointLink.query.filter(
            offerers_models.VenueReimbursementPointLink.venueId == venue_id,
            offerers_models.VenueReimbursementPointLink.reimbursementPointId != venue_id,
            offerers_models.VenueReimbursementPointLink.timespan.contains(datetime.utcnow()),
        )
        .options(
            sa.orm.joinedload(offerers_models.VenueReimbursementPointLink.reimbursementPoint).load_only(
                offerers_models.Venue.id, offerers_models.Venue.name
            )
        )
        .one_or_none()
    )

    # Get invoices for the current venue as a reimbursement point
    # We may have results even if the venue is no longer a reimbursement point
    invoices = (
        finance_models.Invoice.query.filter(finance_models.Invoice.reimbursementPointId == venue_id)
        .options(
            sa.orm.joinedload(finance_models.Invoice.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
        )
        .order_by(finance_models.Invoice.date.desc())
    ).all()

    return render_template(
        "venue/get/invoices.html",
        reimbursement_point=current_link.reimbursementPoint if current_link else None,
        invoices=invoices,
    )


@venue_blueprint.route("/<int:venue_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.DELETE_PRO_ENTITY)
def delete_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)
    venue_name = venue.name

    emails = offerers_repository.get_emails_by_venue(venue)

    try:
        offerers_api.delete_venue(venue.id)
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


@venue_blueprint.route("/<int:venue_id>/update", methods=["POST"])
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

    attrs = {
        to_camelcase(field.name): field.data
        for field in form
        if field.name and hasattr(venue, to_camelcase(field.name))
    }

    update_siret = False
    if not venue.isVirtual and venue.siret != form.siret.data:
        if not _can_edit_siret():
            flash(
                f"Vous ne pouvez pas {'modifier' if venue.siret else 'ajouter'} le SIRET d'un lieu. Contactez le support pro N2.",
                "warning",
            )
            return render_venue_details(venue, form), 400

        if venue.siret:
            if not form.siret.data:
                flash("Vous ne pouvez pas retirer le SIRET d'un lieu.", "warning")
                return render_venue_details(venue, form), 400
        elif form.siret.data:
            # Remove comment because of constraint check_has_siret_xor_comment_xor_isVirtual
            attrs["comment"] = None

        existing_pricing_point_id = venue.current_pricing_point_id
        if existing_pricing_point_id and venue.id != existing_pricing_point_id:
            flash(
                f"Ce lieu a déjà un point de valorisation (Venue.id={existing_pricing_point_id}). "
                f"Définir un SIRET impliquerait qu'il devienne son propre point de valorisation, "
                f"mais le changement de point de valorisation n'est pas autorisé",
                "warning",
            )
            return render_venue_details(venue, form), 400

        try:
            if not sirene.siret_is_active(form.siret.data):
                flash("Ce SIRET n'est plus actif, on ne peut pas l'attribuer à ce lieu", "error")
                return render_venue_details(venue, form), 400
        except sirene.SireneException:
            unavailable_sirene = True
        else:
            unavailable_sirene = False

        update_siret = True

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

    if update_siret:
        if unavailable_sirene:
            flash("Ce SIRET n'a pas pu être vérifié, mais la modification a néanmoins été effectuée", "warning")
        if not existing_pricing_point_id:
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

    flash("Les informations ont bien été mises à jour", "success")
    return redirect(url_for("backoffice_v3_web.venue.get", venue_id=venue.id), code=303)


@venue_blueprint.route("/<int:venue_id>/comment", methods=["POST"])
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


@venue_blueprint.route("/batch-edit-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def get_batch_edit_venues_form() -> utils.BackofficeResponse:
    form = forms.BatchEditVenuesForm()
    if form.object_ids.data:
        if not form.validate():
            flash(utils.build_form_error_msg(form), "warning")
            return redirect(request.referrer or url_for(".list_venues"), code=303)

        venues = (
            offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(form.object_ids_list))
            .options(
                sa.orm.load_only(offerers_models.Venue.id),
                sa.orm.joinedload(offerers_models.Venue.criteria).load_only(
                    criteria_models.Criterion.id, criteria_models.Criterion.name
                ),
            )
            .all()
        )
        criteria = list(reduce(set.intersection, [set(venue.criteria) for venue in venues]))  # type: ignore

        if len(criteria) > 0:
            form.criteria.choices = [(criterion.id, criterion.name) for criterion in criteria]

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".batch_edit_venues"),
        div_id="batch-edit-venues-modal",
        title="Édition des lieux",
        button_text="Enregistrer les modifications",
    )


@venue_blueprint.route("/batch-edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def batch_edit_venues() -> utils.BackofficeResponse:
    form = forms.BatchEditVenuesForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer or url_for(".list_venues"), code=303)

    venues = offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(form.object_ids_list)).all()

    updated_criteria_venues = _update_venues_criteria(venues=venues, criteria_ids=form.criteria.data)
    updated_permanent_venues = []
    if form.all_permanent.data:
        updated_permanent_venues = _update_permanent_venues(venues=venues, is_permanent=True)
    elif form.all_not_permanent.data:
        updated_permanent_venues = _update_permanent_venues(venues=venues, is_permanent=False)

    updated_venues = list(set(updated_criteria_venues + updated_permanent_venues))

    repository.save(*updated_venues)
    search.async_index_venue_ids([v.id for v in updated_venues])

    flash("Les lieux ont été modifiés avec succès", "success")
    return redirect(request.referrer or url_for(".list_venues"), code=303)


def _update_venues_criteria(
    venues: list[offerers_models.Venue], criteria_ids: list[int]
) -> list[offerers_models.Venue]:
    new_criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(criteria_ids)).all()

    previous_criteria = set.intersection(*(set(venue.criteria) for venue in venues))
    deleted_criteria = list(previous_criteria.difference(new_criteria))

    changed_venues = []

    for venue in venues:
        if venue.criteria == new_criteria:
            continue
        if venue.criteria:
            venue.criteria.extend(criterion for criterion in new_criteria if criterion not in venue.criteria)
            for criterion in deleted_criteria:
                venue.criteria.remove(criterion)
        else:
            venue.criteria = new_criteria
        changed_venues.append(venue)

    return changed_venues


def _update_permanent_venues(venues: list[offerers_models.Venue], is_permanent: bool) -> list[offerers_models.Venue]:
    venues_to_update = [venue for venue in venues if venue.isPermanent != is_permanent]
    for venue in venues_to_update:
        venue.isPermanent = is_permanent

    return venues_to_update
