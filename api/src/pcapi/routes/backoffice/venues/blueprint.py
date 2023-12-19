from datetime import datetime
from functools import partial
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.connectors import sirene
from pcapi.connectors.dms import api as dms_api
from pcapi.core import search
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import siret_api
from pcapi.core.history import models as history_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import api as providers_api
from pcapi.core.providers import models as providers_models
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import search as search_forms
from pcapi.routes.backoffice.forms.search import TypeOptions
from pcapi.routes.serialization import base as serialize_base
from pcapi.utils import regions as regions_utils
from pcapi.utils.string import to_camelcase

from . import forms
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
            department_codes += regions_utils.get_department_codes_for_region(region)
        base_query = base_query.filter(offerers_models.Venue.departementCode.in_(department_codes))

    if form.type.data:
        base_query = base_query.filter(offerers_models.Venue.venueTypeCode.in_(form.type.data))

    if form.criteria.data:
        base_query = base_query.outerjoin(offerers_models.Venue.criteria).filter(
            criteria_models.Criterion.id.in_(form.criteria.data)
        )

    if form.offerer.data:
        base_query = base_query.filter(offerers_models.Venue.managingOffererId.in_(form.offerer.data))

    if form.only_validated_offerers.data:
        base_query = base_query.join(offerers_models.Venue.managingOfferer).filter(offerers_models.Offerer.isValidated)

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
            sa.orm.joinedload(offerers_models.Venue.reimbursement_point_links)
            .joinedload(offerers_models.VenueReimbursementPointLink.reimbursementPoint)
            .load_only(offerers_models.Venue.id),
            sa.orm.joinedload(offerers_models.Venue.venueLabel),
            sa.orm.joinedload(offerers_models.Venue.criteria).load_only(criteria_models.Criterion.name),
            sa.orm.joinedload(offerers_models.Venue.collectiveDmsApplications).load_only(
                educational_models.CollectiveDmsApplication.state,
                educational_models.CollectiveDmsApplication.depositDate,
                educational_models.CollectiveDmsApplication.lastChangeDate,
            ),
            sa.orm.joinedload(offerers_models.Venue.venueProviders)
            .load_only(
                providers_models.VenueProvider.id,
                providers_models.VenueProvider.lastSyncDate,
            )
            .joinedload(providers_models.VenueProvider.provider)
            .load_only(
                providers_models.Provider.id,
                providers_models.Provider.name,
                providers_models.Provider.localClass,
            ),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def render_venue_details(
    venue: offerers_models.Venue, edit_venue_form: forms.EditVirtualVenueForm | None = None
) -> str:
    dms_application_id = venue.bankInformation.applicationId if venue.bankInformation else None
    dms_stats = dms_api.get_dms_stats(dms_application_id, api_v4=True)
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
                ban_id=venue.banId,
                booking_email=venue.bookingEmail,
                phone_number=venue.contact.phone_number if venue.contact else None,
                is_permanent=venue.isPermanent,
                latitude=venue.latitude,
                longitude=venue.longitude,
                venue_type_code=venue.venueTypeCode.name,
            )
            edit_venue_form.siret.flags.disabled = not _can_edit_siret()
        edit_venue_form.tags.choices = [(criterion.id, criterion.name) for criterion in venue.criteria]

    delete_form = empty_forms.EmptyForm()

    search_form = search_forms.CompactProSearchForm(
        q=request.args.get("q"),
        pro_type=TypeOptions.VENUE.name,
        departments=request.args.getlist("departments")
        if request.args.get("q") or request.args.getlist("departments")
        else current_user.backoffice_profile.preferences.get("departments", []),
    )

    return render_template(
        "venue/get.html",
        search_form=search_form,
        search_dst=url_for("backoffice_web.search_pro"),
        venue=venue,
        edit_venue_form=edit_venue_form,
        region=region,
        has_reimbursement_point=bool(venue.current_reimbursement_point),
        dms_stats=dms_stats,
        delete_form=delete_form,
        active_tab=request.args.get("active_tab", "history"),
        zendesk_sell_synchronisation_form=empty_forms.EmptyForm()
        if venue.isPermanent
        and not venue.isVirtual
        and utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
        else None,
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
    venues = utils.limit_rows(venues, form.limit.data)

    autocomplete.prefill_criteria_choices(form.criteria)
    autocomplete.prefill_offerers_choices(form.offerer)

    form_url = partial(url_for, ".list_venues", **form.raw_data)
    date_created_sort_url = form_url(order="desc" if form.order.data == "asc" else "asc")

    return render_template("venue/list.html", rows=venues, form=form, date_created_sort_url=date_created_sort_url)


@venue_blueprint.route("/<int:venue_id>", methods=["GET"])
def get(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue(venue_id)

    if request.args.get("q") and request.args.get("search_rank"):
        utils.log_backoffice_tracking_data(
            event_name="ConsultCard",
            extra_data={
                "searchType": "ProSearch",
                "searchProType": TypeOptions.VENUE.name,
                "searchQuery": request.args.get("q"),
                "searchDepartments": ",".join(request.args.get("departments", [])),
                "searchRank": request.args.get("search_rank"),
                "searchNbResults": request.args.get("total_items"),
            },
        )

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
    reimbursement_point_name = None
    pricing_point_name = None
    bic = None
    iban = None
    reimbursement_point_url = None
    pricing_point_url = None
    current_pricing_point = venue.current_pricing_point
    current_reimbursement_point = venue.current_reimbursement_point

    if current_reimbursement_point:
        bic = current_reimbursement_point.bic
        iban = current_reimbursement_point.iban
        reimbursement_point_name = current_reimbursement_point.common_name

        if current_reimbursement_point.id != venue.id:
            reimbursement_point_url = url_for("backoffice_web.venue.get", venue_id=current_reimbursement_point.id)

    if current_pricing_point is not None:
        pricing_point_name = current_pricing_point.common_name
        if current_pricing_point.id != venue.id:
            pricing_point_url = url_for("backoffice_web.venue.get", venue_id=current_pricing_point.id)

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
    venue_query = offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id).options(
        sa.orm.joinedload(offerers_models.Venue.pricing_point_links).joinedload(
            offerers_models.VenuePricingPointLink.pricingPoint
        ),
        sa.orm.joinedload(offerers_models.Venue.reimbursement_point_links)
        .joinedload(offerers_models.VenueReimbursementPointLink.reimbursementPoint)
        .load_only(offerers_models.Venue.name, offerers_models.Venue.publicName)
        .joinedload(offerers_models.Venue.bankInformation)
        .load_only(finance_models.BankInformation.bic, finance_models.BankInformation.iban),
        sa.orm.joinedload(offerers_models.Venue.bankInformation).load_only(
            finance_models.BankInformation.bic, finance_models.BankInformation.iban
        ),
    )

    if FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY.is_active():
        venue_query = (
            venue_query.outerjoin(
                offerers_models.VenueBankAccountLink,
                sa.and_(
                    offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId,
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
                ),
            )
            .outerjoin(offerers_models.VenueBankAccountLink.bankAccount)
            .options(
                sa.orm.contains_eager(offerers_models.Venue.bankAccountLinks)
                .load_only(offerers_models.VenueBankAccountLink.timespan)
                .contains_eager(offerers_models.VenueBankAccountLink.bankAccount)
                .load_only(finance_models.BankAccount.id, finance_models.BankAccount.label)
            )
        )

    venue = venue_query.one_or_none()
    if not venue:
        raise NotFound()

    data = get_stats_data(venue.id)
    bank_information = get_venue_bank_information(venue)
    return render_template(
        "venue/get/stats.html",
        venue=venue,
        stats=data,
        bank_information=bank_information,
    )


@venue_blueprint.route("/<int:venue_id>/provider/<int:provider_id>/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def delete_venue_provider(venue_id: int, provider_id: int) -> utils.BackofficeResponse:
    venue_provider = (
        providers_models.VenueProvider.query.filter(
            providers_models.VenueProvider.providerId == provider_id,
            providers_models.VenueProvider.venueId == venue_id,
        )
        .options(
            sa.orm.joinedload(providers_models.VenueProvider.venue).load_only(offerers_models.Venue.id),
            sa.orm.joinedload(providers_models.VenueProvider.provider).load_only(providers_models.Provider.localClass),
        )
        .one_or_none()
    )

    if not venue_provider:
        raise NotFound()

    if venue_provider.isFromAllocineProvider:
        flash("Impossible d'effacer le lien entre le lieu et Allociné.", "warning")
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)

    providers_api.delete_venue_provider(venue_provider, author=current_user, send_email=False)
    flash("Le lien entre le lieu et le provider a bien été effacé.", "info")

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


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
    dst = url_for("backoffice_web.venue.comment_venue", venue_id=venue.id)

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
                offerers_models.Venue.id, offerers_models.Venue.name, offerers_models.Venue.publicName
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
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)
    except offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException:
        flash("Impossible d'effacer un lieu utilisé comme point de valorisation d'un autre lieu", "warning")
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)
    except offerers_exceptions.CannotDeleteVenueUsedAsReimbursementPointException:
        flash("Impossible d'effacer un lieu utilisé comme point de remboursement d'un autre lieu", "warning")
        return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)

    for email in emails:
        external_attributes_api.update_external_pro(email)

    flash(
        Markup("Le lieu {venue_name} ({venue_id}) a été supprimé").format(venue_name=venue_name, venue_id=venue_id),
        "success",
    )
    return redirect(url_for("backoffice_web.search_pro"), code=303)


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
                    data-bs-target="#edit-venue-modal">
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

    venue_was_permanent = venue.isPermanent
    new_permanent = attrs.get("isPermanent")

    update_siret = False
    if not venue.isVirtual and venue.siret != form.siret.data:
        new_siret = form.siret.data

        if not _can_edit_siret():
            flash(
                f"Vous ne pouvez pas {'modifier' if venue.siret else 'ajouter'} le SIRET d'un lieu. Contactez le support pro N2.",
                "warning",
            )
            return render_venue_details(venue, form), 400

        if venue.siret:
            if not new_siret:
                flash("Vous ne pouvez pas retirer le SIRET d'un lieu.", "warning")
                return render_venue_details(venue, form), 400
        elif new_siret:
            # Remove comment because of constraint check_has_siret_xor_comment_xor_isVirtual
            attrs["comment"] = None

        if new_siret and offerers_repository.find_venue_by_siret(new_siret):
            flash(Markup("Un autre lieu existe déjà avec le SIRET {siret}").format(siret=new_siret), "warning")
            return render_venue_details(venue, form), 400

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
            if not sirene.siret_is_active(new_siret):
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
                flash(
                    Markup("[{error_key}] {error_detail}").format(error_key=error_key, error_detail=error_detail),
                    "warning",
                )
        return render_venue_details(venue, form), 400

    if not venue_was_permanent and new_permanent and venue.thumbCount == 0:
        transactional_mails.send_permanent_venue_needs_picture(venue)

    if update_siret:
        if unavailable_sirene:
            flash("Ce SIRET n'a pas pu être vérifié, mais la modification a néanmoins été effectuée", "warning")
        if not existing_pricing_point_id:
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

    flash("Les informations ont bien été mises à jour", "success")
    return redirect(url_for("backoffice_web.venue.get", venue_id=venue.id), code=303)


@venue_blueprint.route("/<int:venue_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)

    form = forms.CommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    else:
        offerers_api.add_comment_to_venue(venue, current_user, comment=form.comment.data)
        flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


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
        criteria = set.intersection(*[set(venue.criteria) for venue in venues])

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
    search.async_index_venue_ids(
        [v.id for v in updated_venues],
        reason=search.IndexationReason.VENUE_BATCH_UPDATE,
    )

    flash("Les lieux ont été modifiés avec succès", "success")
    return redirect(request.referrer or url_for(".list_venues"), code=303)


def _update_venues_criteria(
    venues: list[offerers_models.Venue], criteria_ids: list[int]
) -> list[offerers_models.Venue]:
    new_criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(criteria_ids)).all()

    previous_criteria = set.intersection(*(set(venue.criteria) for venue in venues))
    deleted_criteria = previous_criteria.difference(new_criteria)

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
        if is_permanent and venue.thumbCount == 0:
            transactional_mails.send_permanent_venue_needs_picture(venue)

    return venues_to_update


REMOVE_PRICING_POINT_TITLE = "Détacher les points de valorisation et remboursement"


def _load_venue_for_removing_pricing_point(venue_id: int) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .options(
            sa.orm.load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
            sa.orm.joinedload(offerers_models.Venue.pricing_point_links)
            .joinedload(offerers_models.VenuePricingPointLink.pricingPoint)
            .load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
            sa.orm.joinedload(offerers_models.Venue.reimbursement_point_links)
            .joinedload(offerers_models.VenueReimbursementPointLink.reimbursementPoint)
            .load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def _render_remove_pricing_point_content(
    venue: offerers_models.Venue, form: forms.RemovePricingPointForm | None = None, error: str | None = None
) -> utils.BackofficeResponse:
    current_pricing_point = venue.current_pricing_point
    current_reimbursement_point = venue.current_reimbursement_point

    kwargs = {}
    if form:
        kwargs.update(
            {
                "form": form,
                "dst": url_for("backoffice_web.venue.remove_pricing_point", venue_id=venue.id),
                "button_text": "Confirmer",
            }
        )
    return (
        render_template(
            "components/turbo/modal_form.html",
            div_id="remove-venue-pricing-point",  # must be consistent with parameter passed to build_lazy_modal
            title=REMOVE_PRICING_POINT_TITLE,
            additional_data={
                "Lieu": venue.name,
                "Venue ID": venue.id,
                "SIRET": venue.siret or "Pas de SIRET",
                "CA de l'année": filters.format_amount(siret_api.get_yearly_revenue(venue.id)),
                "Point de valorisation": current_pricing_point.name if current_pricing_point else "Aucun",
                "SIRET de valorisation": current_pricing_point.siret if current_pricing_point else "Aucun",
                "Point de remboursement": current_reimbursement_point.name if current_reimbursement_point else "Aucun",
                "SIRET de remboursement": current_reimbursement_point.siret if current_reimbursement_point else "Aucun",
            },
            alert=error,
            **kwargs,
        ),
        400 if error or (form and form.errors) else 200,
    )


@venue_blueprint.route("/<int:venue_id>/remove-pricing-point", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_remove_pricing_point_form(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_pricing_point(venue_id)

    try:
        siret_api.check_can_remove_pricing_point(venue)
    except siret_api.CheckError as exc:
        return _render_remove_pricing_point_content(venue, error=str(exc))

    form = forms.RemovePricingPointForm()
    return _render_remove_pricing_point_content(venue, form=form)


@venue_blueprint.route("/<int:venue_id>/remove-pricing-point", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def remove_pricing_point(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_pricing_point(venue_id)

    form = forms.RemovePricingPointForm()
    if not form.validate():
        return _render_remove_pricing_point_content(venue, form=form)

    try:
        siret_api.remove_pricing_point_link(
            venue,
            form.comment.data,
            apply_changes=True,
            override_revenue_check=bool(form.override_revenue_check.data),
            author_user_id=current_user.id,
        )
    except siret_api.CheckError as exc:
        return _render_remove_pricing_point_content(venue, form=form, error=str(exc))

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)


REMOVE_SIRET_TITLE = "Supprimer le SIRET d'un lieu"


def _load_venue_for_removing_siret(venue_id: int) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .options(
            sa.orm.load_only(offerers_models.Venue.name, offerers_models.Venue.publicName, offerers_models.Venue.siret),
            sa.orm.joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.id, offerers_models.Offerer.name)
            .joinedload(offerers_models.Offerer.managedVenues)
            .load_only()
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            ),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def _render_remove_siret_content(
    venue: offerers_models.Venue, form: forms.RemoveSiretForm | None = None, error: str | None = None
) -> utils.BackofficeResponse:
    kwargs = {}
    if form:
        kwargs.update(
            {
                "form": form,
                "dst": url_for("backoffice_web.venue.remove_siret", venue_id=venue.id),
                "button_text": "Confirmer",
            }
        )
    return (
        render_template(
            "components/turbo/modal_form.html",
            div_id="remove-venue-siret",  # must be consistent with parameter passed to build_lazy_modal
            title=REMOVE_SIRET_TITLE,
            additional_data={
                "Structure": venue.managingOfferer.name,
                "Offerer ID": venue.managingOfferer.id,
                "Lieu": venue.name,
                "Venue ID": venue.id,
                "SIRET": venue.siret or "Pas de SIRET",
                "CA de l'année": filters.format_amount(siret_api.get_yearly_revenue(venue.id)),
            },
            alert=error,
            **kwargs,
        ),
        400 if error or (form and form.errors) else 200,
    )


@venue_blueprint.route("/<int:venue_id>/remove-siret", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MOVE_SIRET)
def get_remove_siret_form(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_siret(venue_id)

    try:
        siret_api.check_can_remove_siret(
            venue, "comment", override_revenue_check=True, check_offerer_has_other_siret=True
        )
    except siret_api.CheckError as exc:
        return _render_remove_siret_content(venue, error=str(exc))

    form = forms.RemoveSiretForm(venue)
    return _render_remove_siret_content(venue, form=form)


@venue_blueprint.route("/<int:venue_id>/remove-siret", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MOVE_SIRET)
def remove_siret(venue_id: int) -> utils.BackofficeResponse:
    venue = _load_venue_for_removing_siret(venue_id)

    form = forms.RemoveSiretForm(venue)
    if not form.validate():
        return _render_remove_siret_content(venue, form=form)

    try:
        siret_api.remove_siret(
            venue,
            form.comment.data,
            apply_changes=True,
            override_revenue_check=bool(form.override_revenue_check.data),
            new_pricing_point_id=form.new_pricing_point.data,
            author_user_id=current_user.id,
            new_db_session=False,
        )
    except siret_api.CheckError as exc:
        return _render_remove_siret_content(venue, form=form, error=str(exc))

    return redirect(url_for("backoffice_web.venue.get", venue_id=venue_id), code=303)
