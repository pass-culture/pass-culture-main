import datetime
import typing
from functools import partial

import sqlalchemy.orm as sa_orm
from flask import flash
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.utils import get_or_404
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import blueprint as backoffice_blueprint
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.utils import access_control
from pcapi.routes.backoffice.utils import request as request_utils
from pcapi.routes.backoffice.utils import response as response_utils
from pcapi.routes.backoffice.utils import search as search_utils
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms as venue_forms
from . import validation_repository


venue_validation_blueprint = backoffice_blueprint.child_backoffice_blueprint(
    "venue_validation",
    __name__,
    url_prefix="/pro/venue/validation",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def _filter_homologation_tags(tags: list[offerers_models.OffererTag]) -> list[offerers_models.OffererTag]:
    return [tag for tag in tags if "homologation" in [cat.name for cat in tag.categories]]


def _redirect_after_venue_validation_action() -> response_utils.BackofficeResponse:
    return request_utils.safe_redirect_back(request, url_for("backoffice.venue_validation.list_venues_to_validate"))


def _render_venues_to_validate(venues_id: list[int]) -> response_utils.BackofficeResponse:
    items = validation_repository.list_venues_to_validate(venues_id=venues_id)
    return render_template(
        "venue/validation_rows.html",
        items=items,
    )


@venue_validation_blueprint.route("", methods=["GET"])
def list_venues_to_validate() -> response_utils.BackofficeResponse:
    stats = offerers_api.count_offerers_by_validation_status()

    form = venue_forms.VenueValidationListForm(formdata=request_utils.get_query_params())
    if not form.validate():
        mark_transaction_as_invalid()
        return render_template("venue/validation.html", rows=[], form=form, stats=stats), 400

    if not form.status.data:
        form.status.data = [offerers_models.VenueValidationStatus.PENDING.value]

    venues = validation_repository.list_venues_to_validate(
        q=form.q.data,
        regions=form.regions.data,
        tags=form.tags.data,
        status=form.status.data,
        ae_documents_received=form.ae_documents_received.data,
        last_instructor_ids=form.instructors.data,
        dms_adage_status=form.dms_adage_status.data,
        from_datetime=date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time()),
        to_datetime=date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time()),
    )

    sorted_venues: sa_orm.Query = venues.order_by(
        getattr(getattr(offerers_models.Venue, form.sort.data), form.order.data)()
    )

    paginated_venues = search_utils.paginate(
        query=sorted_venues,
        page=int(form.data["page"]),
        per_page=int(form.data["limit"]),
    )

    form_url = partial(url_for, ".list_venues_to_validate", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.data["page"]), paginated_venues.pages)

    date_created_sort_url = form_url(
        sort="dateCreated", order="desc" if form.sort.data == "dateCreated" and form.order.data == "asc" else "asc"
    )

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    autocomplete.prefill_bo_users_choices(form.instructors)
    return render_template(
        "venue/validation.html",
        rows=paginated_venues,
        form=form,
        next_pages_urls=next_pages_urls,
        date_created_sort_url=date_created_sort_url,
        stats=stats,
    )


def _get_validation_action_information(venue_ids: typing.Collection[int]) -> str | None:
    information = ""

    bank_accounts = (
        db.session.query(finance_models.BankAccount)
        .filter(
            finance_models.BankAccount.offererId.in_(
                db.session.query(offerers_models.Venue.managingOffererId).filter(
                    offerers_models.Venue.id.in_(venue_ids)
                )
            ),
            finance_models.BankAccount.status.in_(
                [
                    finance_models.BankAccountApplicationStatus.DRAFT,
                    finance_models.BankAccountApplicationStatus.ON_GOING,
                    finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS,
                ]
            ),
        )
        .order_by(finance_models.BankAccount.offererId)
        .all()
    )

    if bank_accounts:
        offerers_text = filters.pluralize(
            len(venue_ids), "l'entité juridique parente", "les entités juridiques parentes"
        )
        if len(bank_accounts) == 1:
            information = Markup(
                "Un dossier de <strong>coordonnées bancaires</strong> est en cours sur Démarche Numérique pour {offerers_text}, "
                "son traitement n'est pas automatique, ne l'oublions pas : <ul>"
            ).format(offerers_text=offerers_text)
        else:
            information = Markup(
                "{count} dossiers de <strong>coordonnées bancaires</strong> sont en cours sur Démarche Numérique pour {offerers_text}, "
                "leur traitement n'est pas automatique, ne les oublions pas : <ul>"
            ).format(count=len(bank_accounts), offerers_text=offerers_text)

        for pending_bank_account in bank_accounts:
            information += Markup(
                '<li class="my-1"><a href="https://demarche.numerique.gouv.fr/procedures/{procedure_number}/dossiers/{application_number}" target="_blank" class="link-primary">Dossier n°{application_number}</a> : {status}</li>'
            ).format(
                procedure_number=settings.DS_BANK_ACCOUNT_PROCEDURE_ID,
                application_number=pending_bank_account.dsApplicationId,
                status=filters.format_dms_application_status_badge(pending_bank_account.status),
            )
        information += Markup("</ul>")

    collective_applications = (
        db.session.query(educational_models.CollectiveDmsApplication)
        .join(offerers_models.Venue, offerers_models.Venue.siret == educational_models.CollectiveDmsApplication.siret)
        .filter(
            offerers_models.Venue.id.in_(venue_ids),
            educational_models.CollectiveDmsApplication.state.in_(
                [GraphQLApplicationStates.draft.value, GraphQLApplicationStates.on_going.value]
            ),
        )
        .order_by(educational_models.CollectiveDmsApplication.lastChangeDate)
        .all()
    )

    if collective_applications:
        offerers_text = filters.pluralize(len(venue_ids), "ce partenaire culturel", "ces partenaires culturels")
        if len(collective_applications) == 1:
            information += Markup(
                "Un dossier <strong>ADAGE</strong> est en cours sur Démarche Numérique pour {offerers_text}, "
                "son traitement n'est pas automatique, ne l'oublions pas : <ul>"
            ).format(offerers_text=offerers_text)
        else:
            information += Markup(
                "{count} dossiers <strong>ADAGE</strong> sont en cours sur Démarche Numérique pour {offerers_text}, "
                "leur traitement n'est pas automatique, ne les oublions pas : <ul>"
            ).format(count=len(collective_applications), offerers_text=offerers_text)

        for collective_application in collective_applications:
            information += Markup(
                '<li class="my-1"><a href="https://demarche.numerique.gouv.fr/procedures/{procedure_number}/dossiers/{application_number}" target="_blank" class="link-primary">Dossier n°{application_number}</a> : {status}</li>'
            ).format(
                procedure_number=collective_application.procedure,
                application_number=collective_application.application,
                status=filters.format_dms_status(collective_application.state),
            )
        information += Markup("</ul>")

    return information or None


@venue_validation_blueprint.route("/offerer/<int:venue_id>/validate", methods=["GET"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_validate_venue_form(venue_id: int) -> response_utils.BackofficeResponse:
    venue = get_or_404(offerers_models.Venue, venue_id)
    information = _get_validation_action_information([venue_id])

    kwargs = {
        "information": information,
        "form": venue_forms.VenueValidationForm(),
        "dst": url_for("backoffice.venue_validation.validate_venue", venue_id=venue.id),
        "div_id": f"validate-modal-{venue.id}",  # must be consistent with parameter passed to build_lazy_modal
        "title": f"Valider le partenaire culturel {venue.name.upper()}",
        "button_text": "Valider le partenaire culturel",
        "ajax_submit": request_utils.is_request_from_htmx(),
    }

    if kwargs["ajax_submit"]:
        kwargs["target_id"] = f"#offerer-row-{venue.id}"

    return render_template("components/dynamic/modal_form.html", **kwargs)


@venue_validation_blueprint.route("/<int:venue_id>/validate", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def validate_offerer(venue_id: int) -> response_utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    form = venue_forms.VenueValidationForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(response_utils.build_form_error_msg(form), "warning")
        if request_utils.is_request_from_htmx():
            return _render_venues_to_validate([venue_id])
        return _redirect_after_venue_validation_action()

    try:
        offerers_api.validate_venue(
            venue, current_user, review_all_offers=bool(form.review_all_offers.data), comment=form.comment.data
        )
    except offerers_exceptions.VenueAlreadyValidatedException:
        mark_transaction_as_invalid()
        flash(Markup("Le partenaire culturel <b>{name}</b> est déjà validé").format(name=venue.name), "warning")
        if request_utils.is_request_from_htmx():
            return _render_venues_to_validate([venue_id])
        return _redirect_after_venue_validation_action()

    flash(Markup("Le partenaire culturel <b>{name}</b> a été validé").format(name=venue.name), "success")
    if request_utils.is_request_from_htmx():
        return _render_venues_to_validate([venue_id])
    return _redirect_after_venue_validation_action()


@venue_validation_blueprint.route("/<int:venue_id>/reject", methods=["GET"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_reject_venue_form(venue_id: int) -> response_utils.BackofficeResponse:
    venue = get_or_404(offerers_models.Venue, venue_id)
    information = _get_validation_action_information([venue_id])

    kwargs = {
        "information": information,
        "form": venue_forms.VenueRejectionForm(),
        "dst": url_for("backoffice.venue_validation.reject_venue", venue_id=venue.id),
        "div_id": f"reject-modal-{venue.id}",  # must be consistent with parameter passed to build_lazy_modal
        "title": f"Rejeter le partenaire culturel {venue.name.upper()}",
        "button_text": "Rejeter le partenaire culturel",
        "ajax_submit": request_utils.is_request_from_htmx(),
    }

    if kwargs["ajax_submit"]:
        kwargs["target_id"] = f"#venue-row-{venue.id}"

    return render_template("components/dynamic/modal_form.html", **kwargs)


@venue_validation_blueprint.route("/<int:venue_id>/reject", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def reject_venue(venue_id: int) -> response_utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    form = venue_forms.VenueRejectionForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(response_utils.build_form_error_msg(form), "warning")
        if request_utils.is_request_from_htmx():
            return _render_venues_to_validate([venue_id])
        return _redirect_after_venue_validation_action()

    try:
        offerers_api.reject_venue(
            venue,
            current_user,
            comment=form.comment.data,
            rejection_reason=offerers_models.OffererRejectionReason(form.rejection_reason.data),
        )
    except offerers_exceptions.VenueAlreadyRejectedException:
        mark_transaction_as_invalid()
        flash(Markup("Le partenaire culturel <b>{name}</b> est déjà rejeté").format(name=venue.name), "warning")
        if request_utils.is_request_from_htmx():
            return _render_venues_to_validate([venue_id])
        return _redirect_after_venue_validation_action()

    flash(Markup("Le partenaire culturel <b>{name}</b> a été rejeté").format(name=venue.name), "success")
    if request_utils.is_request_from_htmx():
        return _render_venues_to_validate([venue_id])
    return _redirect_after_venue_validation_action()


@venue_validation_blueprint.route("/<int:venue_id>/pending", methods=["GET"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_venue_pending_form(venue_id: int) -> response_utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .options(
            sa_orm.joinedload(offerers_models.Venue.managingOfferer)
            .joinedload(offerers_models.Offerer.tags)
            .joinedload(offerers_models.OffererTag.categories)
            .load_only(offerers_models.OffererTagCategory.name)
        )
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    form = venue_forms.CommentAndTagVenueForm(tags=_filter_homologation_tags(venue.managingOfferer.tags))

    kwargs = {
        "form": form,
        "dst": url_for("backoffice.venue_validation.set_venue_pending", venue_id=venue.id),
        "div_id": f"pending-modal-{venue.id}",  # must be consistent with parameter passed to build_lazy_modal
        "title": f"Mettre en attente le partenaire culturel {venue.name.upper()}",
        "button_text": "Mettre en attente",
        "ajax_submit": request_utils.is_request_from_htmx(),
    }

    if kwargs["ajax_submit"]:
        kwargs["target_id"] = f"#venue-row-{venue.id}"

    return render_template("components/dynamic/modal_form.html", **kwargs)


@venue_validation_blueprint.route("/<int:venue_id>/pending", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def set_venue_pending(venue_id: int) -> response_utils.BackofficeResponse:
    venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=venue_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not venue:
        raise NotFound()

    form = venue_forms.CommentAndTagVenueForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(response_utils.build_form_error_msg(form), "warning")
        if request_utils.is_request_from_htmx():
            return _render_venues_to_validate([venue_id])
        return _redirect_after_venue_validation_action()

    # Don't pass directly form.tags.data to set_offerer_pending() because this would remove non-homologation tags
    saved_homologation_tags = set(_filter_homologation_tags(venue.managingOfferer.tags))
    tags_to_add = set(form.tags.data) - saved_homologation_tags
    tags_to_remove = saved_homologation_tags - set(form.tags.data)

    offerers_api.set_venue_pending(
        venue, current_user, comment=form.comment.data, tags_to_add=tags_to_add, tags_to_remove=tags_to_remove
    )

    flash(Markup("Le partenaire culturel <b>{name}</b> a été mis en attente").format(name=venue.name), "success")
    if request_utils.is_request_from_htmx():
        return _render_venues_to_validate([venue_id])
    return _redirect_after_venue_validation_action()


def _venues_batch_action(
    api_function: typing.Callable,
    success_message: str,
    form_class: typing.Callable,
) -> response_utils.BackofficeResponse:
    form = form_class()
    if not form.validate():
        flash(response_utils.build_form_error_msg(form), "warning")
        return _render_venues_to_validate(venues_id=form.object_ids_list)

    venues = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id.in_(form.object_ids_list))
        .populate_existing()
        .with_for_update(key_share=True)
        .all()
    )

    if hasattr(form, "tags"):
        tags = form.tags.data
        previous_tags = set.intersection(*[set(venue.managingOfferer.tags) for venue in venues])
        deleted_tags = list(previous_tags.difference(set(tags)))
    else:
        deleted_tags = []

    for venue in venues:
        kwargs = {}
        if hasattr(form, "tags"):
            kwargs["tags_to_add"] = form.tags.data
            kwargs["tags_to_remove"] = deleted_tags
        if hasattr(form, "comment"):
            kwargs["comment"] = form.comment.data
        if hasattr(form, "review_all_offers"):
            kwargs["review_all_offers"] = bool(form.review_all_offers.data)
        if hasattr(form, "rejection_reason"):
            kwargs["rejection_reason"] = offerers_models.OffererRejectionReason(form.rejection_reason.data)

        api_function(venue, current_user, **kwargs)

    flash(success_message, "success")

    return _render_venues_to_validate(venues_id=form.object_ids_list)


@venue_validation_blueprint.route("/batch-validate-form", methods=["GET", "POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_batch_validate_offerer_form() -> response_utils.BackofficeResponse:
    form = venue_forms.BatchVenueValidationForm()

    if form.object_ids.data:
        information = _get_validation_action_information(form.object_ids_list)
    else:
        information = None

    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#venues-table",
        information=information,
        form=form,
        dst=url_for("backoffice.venue_validation.batch_validate_venues"),
        div_id="batch-validate-modal",
        title="Valider les partenaires culturels",
        button_text="Valider les partenaires culturels",
    )


@venue_validation_blueprint.route("/batch-validate", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_validate_offerer() -> response_utils.BackofficeResponse:
    try:
        return _venues_batch_action(
            offerers_api.validate_offerer,
            "Les partenaires culturels sélectionnés ont été validés",
            venue_forms.BatchVenueValidationForm,
        )
    except offerers_exceptions.VenueAlreadyValidatedException:
        mark_transaction_as_invalid()
        flash("Au moins un des partenaires culturels a déjà été validé", "warning")
        return ""


@venue_validation_blueprint.route("/batch-pending-form", methods=["GET", "POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_batch_venues_pending_form() -> response_utils.BackofficeResponse:
    form = venue_forms.BatchCommentAndTagVenueForm()
    if form.object_ids.data:
        if not form.validate():
            mark_transaction_as_invalid()
            flash(response_utils.build_form_error_msg(form), "warning")
            return _redirect_after_venue_validation_action()

        offerers = (
            db.session.query(offerers_models.Offerer)
            .join(offerers_models.Offerer.managedVenues)
            .filter(offerers_models.Venue.id.in_(form.object_ids_list))
            .options(
                sa_orm.load_only(offerers_models.Offerer.id),
                sa_orm.joinedload(offerers_models.Offerer.tags).load_only(
                    offerers_models.OffererTag.id, offerers_models.OffererTag.label
                ),
            )
            .all()
        )
        tags = list(set.intersection(*[set(offerer.tags) for offerer in offerers]))

        if len(tags) > 0:
            form.tags.data = tags

    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#venues-table",
        form=form,
        dst=url_for("backoffice.validation.batch_set_venues_pending"),
        div_id="batch-pending-modal",
        title="Mettre en attente les partenaires culturels",
        button_text="Mettre en attente les partenaires culturels",
    )


@venue_validation_blueprint.route("/batch-pending", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_set_venues_pending() -> response_utils.BackofficeResponse:
    return _venues_batch_action(
        offerers_api.set_venue_pending,
        "Les partenaires culturels sélectionnés ont été mis en attente",
        venue_forms.BatchCommentAndTagVenueForm,
    )


@venue_validation_blueprint.route("/batch-reject-form", methods=["GET", "POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def get_batch_reject_venues_form() -> response_utils.BackofficeResponse:
    form = venue_forms.BatchVenueRejectionForm()

    if form.object_ids.data:
        information = _get_validation_action_information(form.object_ids_list)
    else:
        information = None

    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#venues-table",
        information=information,
        form=form,
        dst=url_for("backoffice.venue_validation.batch_reject_venues"),
        div_id="batch-reject-modal",
        title="Rejeter les partenaires culturels",
        button_text="Rejeter les partenaires culturels",
    )


@venue_validation_blueprint.route("/batch-reject", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.VALIDATE_OFFERER)
def batch_reject_venues() -> response_utils.BackofficeResponse:
    try:
        return _venues_batch_action(
            offerers_api.reject_venue,
            "Les partenaires culturels sélectionnés ont été rejetés",
            venue_forms.BatchVenueRejectionForm,
        )
    except offerers_exceptions.OffererAlreadyRejectedException:
        mark_transaction_as_invalid()
        flash("Un des partenaires culturels a déjà été rejeté", "warning")
        return ""
