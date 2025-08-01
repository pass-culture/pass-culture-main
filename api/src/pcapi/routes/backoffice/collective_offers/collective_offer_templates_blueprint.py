import datetime
import functools

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from werkzeug.exceptions import NotFound

from pcapi.core import search
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils import date as date_utils
from pcapi.utils import string as string_utils
from pcapi.utils import urls

from . import forms as collective_offer_forms


list_collective_offer_templates_blueprint = utils.child_backoffice_blueprint(
    "collective_offer_template",
    __name__,
    url_prefix="/pro/collective-offer-template",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_collective_offer_templates_query() -> sa_orm.Query:
    return (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .options(
            sa_orm.load_only(
                educational_models.CollectiveOfferTemplate.id,
                educational_models.CollectiveOfferTemplate.name,
                educational_models.CollectiveOfferTemplate.formats,
                educational_models.CollectiveOfferTemplate.dateCreated,
                educational_models.CollectiveOfferTemplate.validation,
                educational_models.CollectiveOfferTemplate.authorId,
                educational_models.CollectiveOfferTemplate.rejectionReason,
            ),
            sa_orm.contains_eager(educational_models.CollectiveOfferTemplate.venue).options(
                sa_orm.load_only(
                    offerers_models.Venue.managingOffererId,
                    offerers_models.Venue.name,
                    offerers_models.Venue.publicName,
                ),
                sa_orm.contains_eager(offerers_models.Venue.managingOfferer).options(
                    sa_orm.load_only(
                        offerers_models.Offerer.name,
                        # needed to check if stock is bookable and compute initial/remaining stock:
                        offerers_models.Offerer.isActive,
                        offerers_models.Offerer.validationStatus,
                    ),
                    sa_orm.joinedload(offerers_models.Offerer.confidenceRule).load_only(
                        offerers_models.OffererConfidenceRule.confidenceLevel
                    ),
                    sa_orm.with_expression(
                        offerers_models.Offerer.isTopActeur,
                        offerers_models.Offerer.is_top_acteur.expression,  # type: ignore[attr-defined]
                    ),
                ),
                sa_orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                    offerers_models.OffererConfidenceRule.confidenceLevel
                ),
            ),
            sa_orm.joinedload(educational_models.CollectiveOfferTemplate.flaggingValidationRules).load_only(
                offers_models.OfferValidationRule.name
            ),
            sa_orm.joinedload(educational_models.CollectiveOfferTemplate.author).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
        )
    )


def _get_collective_offer_templates(
    form: collective_offer_forms.GetCollectiveOfferTemplatesListForm,
) -> list[educational_models.CollectiveOfferTemplate]:
    base_query = _get_collective_offer_templates_query()
    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.dateCreated <= to_datetime)

    if form.formats.data:
        base_query = base_query.filter(
            educational_models.CollectiveOfferTemplate.formats.overlap(
                sa.dialects.postgresql.array((fmt for fmt in form.formats.data))
            )
        )

    if form.venue.data:
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.venueId.in_(form.venue.data))

    if form.offerer.data:
        base_query = base_query.filter(offerers_models.Venue.managingOffererId.in_(form.offerer.data))

    if form.status.data:
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.validation.in_(form.status.data))

    if form.only_validated_offerers.data:
        base_query = base_query.filter(offerers_models.Offerer.isValidated)

    if form.q.data:
        search_query = form.q.data

        if string_utils.is_numeric(search_query):
            base_query = base_query.filter(educational_models.CollectiveOfferTemplate.id == int(search_query))
        else:
            name_query = "%{}%".format(search_query)
            base_query = base_query.filter(educational_models.CollectiveOfferTemplate.name.ilike(name_query))

    if form.sort.data:
        base_query = base_query.order_by(
            getattr(getattr(educational_models.CollectiveOfferTemplate, form.sort.data), form.order.data)()
        )

    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1).all()


def _render_collective_offers_templates(
    collective_offers_templates_ids: list[int] | None = None,
) -> utils.BackofficeResponse:
    rows = []
    if collective_offers_templates_ids:
        query = _get_collective_offer_templates_query()
        query = query.filter(educational_models.CollectiveOfferTemplate.id.in_(collective_offers_templates_ids))
        rows = query.all()

    connect_as = {}
    for collective_offer_template in rows:
        connect_as[collective_offer_template.id] = get_connect_as(
            object_type="collective_offer_template",
            object_id=collective_offer_template.id,
            pc_pro_path=urls.build_pc_pro_offer_path(collective_offer_template),
        )
    return render_template(
        "collective_offer_template/list_rows.html",
        rows=rows,
        connect_as=connect_as,
    )


@list_collective_offer_templates_blueprint.route("", methods=["GET"])
def list_collective_offer_templates() -> utils.BackofficeResponse:
    form = collective_offer_forms.GetCollectiveOfferTemplatesListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("collective_offer_template/list.html", rows=[], form=form), 400

    if form.is_empty():
        return render_template("collective_offer_template/list.html", rows=[], form=form)

    collective_offer_templates = _get_collective_offer_templates(form)

    collective_offer_templates = utils.limit_rows(collective_offer_templates, form.limit.data)

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)

    connect_as = {}
    for collective_offer_template in collective_offer_templates:
        connect_as[collective_offer_template.id] = get_connect_as(
            object_type="collective_offer_template",
            object_id=collective_offer_template.id,
            pc_pro_path=urls.build_pc_pro_offer_path(collective_offer_template),
        )

    return render_template(
        "collective_offer_template/list.html",
        rows=collective_offer_templates,
        form=form,
        connect_as=connect_as,
        date_created_sort_url=form.get_sort_link(".list_collective_offer_templates") if form.sort.data else None,
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_validate_collective_offer_template_form(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter_by(id=collective_offer_template_id)
        .one_or_none()
    )
    if not collective_offer_template:
        raise NotFound()

    form = empty_forms.EmptyForm()

    kwargs = {
        "form": form,
        "dst": url_for(
            "backoffice_web.collective_offer_template.validate_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        ),
        "div_id": f"validate-collective-offer-template-modal-{collective_offer_template.id}",
        "title": f"Validation de l'offre vitrine {collective_offer_template.name}",
        "button_text": "Valider l'offre vitrine",
    }
    if utils.is_request_from_htmx():
        return render_template(
            "components/dynamic/modal_form.html",
            target_id=f"#collective-offer-template-row-{collective_offer_template_id}",
            **kwargs,
        )
    return render_template("components/turbo/modal_form.html", **kwargs)


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_collective_offer_template(collective_offer_template_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offer_templates(OfferValidationStatus.APPROVED, [collective_offer_template_id])

    if utils.is_request_from_htmx():
        return _render_collective_offers_templates([collective_offer_template_id])
    return redirect(
        request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"),
        303,
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_reject_collective_offer_template_form(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter_by(id=collective_offer_template_id)
        .one_or_none()
    )
    if not collective_offer_template:
        raise NotFound()

    form = collective_offer_forms.RejectCollectiveOfferForm()

    kwargs = {
        "form": form,
        "dst": url_for(
            "backoffice_web.collective_offer_template.reject_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        ),
        "div_id": f"reject-collective-offer-template-modal-{collective_offer_template.id}",
        "title": f"Rejet de l'offre vitrine {collective_offer_template.name}",
        "button_text": "Rejeter l'offre vitrine",
    }
    if utils.is_request_from_htmx():
        return render_template(
            "components/dynamic/modal_form.html",
            target_id=f"#collective-offer-template-row-{collective_offer_template_id}",
            **kwargs,
        )
    return render_template("components/turbo/modal_form.html", **kwargs)


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_collective_offer_template(collective_offer_template_id: int) -> utils.BackofficeResponse:
    form = collective_offer_forms.RejectCollectiveOfferForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        if utils.is_request_from_htmx():
            return _render_collective_offers_templates()
        return redirect(
            request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"), 303
        )

    _batch_validate_or_reject_collective_offer_templates(
        OfferValidationStatus.REJECTED,
        [collective_offer_template_id],
        educational_models.CollectiveOfferRejectionReason(form.reason.data),
    )
    if utils.is_request_from_htmx():
        return _render_collective_offers_templates([collective_offer_template_id])
    return redirect(
        request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"),
        303,
    )


def _batch_validate_or_reject_collective_offer_templates(
    validation: OfferValidationStatus,
    collective_offer_template_ids: list[int],
    reason: educational_models.CollectiveOfferRejectionReason | None = None,
) -> bool:
    collective_offer_templates = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter(
            educational_models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids),
            educational_models.CollectiveOfferTemplate.validation == OfferValidationStatus.PENDING,
        )
        .all()
    )

    if len(collective_offer_template_ids) != len(collective_offer_templates):
        flash(
            (
                "Seules les offres collectives vitrine en attente peuvent être validées"
                if validation is OfferValidationStatus.APPROVED
                else "Seules les offres collectives vitrine en attente peuvent être rejetées"
            ),
            "warning",
        )
        return False

    collective_offer_template_update_succeed_ids: list[int] = []
    collective_offer_template_update_failed_ids: list[int] = []

    for collective_offer_template in collective_offer_templates:
        with atomic():
            old_validation_status = collective_offer_template.validation
            new_validation_status = validation
            collective_offer_template.validation = new_validation_status
            collective_offer_template.lastValidationDate = datetime.datetime.utcnow()
            collective_offer_template.lastValidationType = OfferValidationType.MANUAL
            collective_offer_template.lastValidationAuthorUserId = current_user.id
            if validation is OfferValidationStatus.APPROVED:
                collective_offer_template.isActive = True
                collective_offer_template.rejectionReason = None
            else:
                collective_offer_template.rejectionReason = reason

            try:
                db.session.flush()
            except Exception:
                mark_transaction_as_invalid()
                collective_offer_template_update_failed_ids.append(collective_offer_template.id)
                continue

            collective_offer_template_update_succeed_ids.append(collective_offer_template.id)

            recipients = (
                [collective_offer_template.venue.bookingEmail]
                if collective_offer_template.venue.bookingEmail
                else [
                    recipient.user.email for recipient in collective_offer_template.venue.managingOfferer.UserOfferers
                ]
            )
            offer_data = transactional_mails.get_email_data_from_offer(
                collective_offer_template, old_validation_status, new_validation_status
            )
            transactional_mails.send_offer_validation_status_update_email(offer_data, recipients)

    on_commit(
        functools.partial(
            search.async_index_collective_offer_template_ids,
            collective_offer_template_update_succeed_ids,
            reason=search.IndexationReason.OFFER_BATCH_VALIDATION,
        ),
    )

    if len(collective_offer_template_update_succeed_ids) == 1:
        flash(
            (
                "L'offre collective vitrine a été validée"
                if validation is OfferValidationStatus.APPROVED
                else "L'offre collective vitrine a été rejetée"
            ),
            "success",
        )
    elif collective_offer_template_update_succeed_ids:
        flash(
            (
                f"Les offres collectives vitrine {', '.join(map(str, collective_offer_template_update_succeed_ids))} ont été validées"
                if validation is OfferValidationStatus.APPROVED
                else f"Les offres collectives vitrine {', '.join(map(str, collective_offer_template_update_succeed_ids))} ont été rejetées"
            ),
            "success",
        )

    if len(collective_offer_template_update_failed_ids) > 0:
        flash(
            (
                f"Une erreur est survenue lors de la validation des offres collectives vitrine : {', '.join(map(str, collective_offer_template_update_failed_ids))}"
                if validation is OfferValidationStatus.APPROVED
                else f"Une erreur est survenue lors du rejet des offres collectives vitrine : {', '.join(map(str, collective_offer_template_update_failed_ids))}"
                "warning"
            ),
        )

    return True


@list_collective_offer_templates_blueprint.route("/batch/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_collective_offer_templates_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm(request.args)
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#collective-offer-template-table",
        form=form,
        dst=url_for("backoffice_web.collective_offer_template.batch_validate_collective_offer_templates"),
        div_id="batch-validate-modal",
        title="Voulez-vous valider les offres collectives vitrine sélectionnées ?",
        button_text="Valider",
    )


@list_collective_offer_templates_blueprint.route("/batch/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_collective_offer_templates_form() -> utils.BackofficeResponse:
    form = collective_offer_forms.BatchRejectCollectiveOfferForm(request.args)
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#collective-offer-template-table",
        form=form,
        dst=url_for("backoffice_web.collective_offer_template.batch_reject_collective_offer_templates"),
        div_id="batch-reject-modal",
        title="Voulez-vous rejeter les offres collectives vitrine sélectionnées ?",
        button_text="Rejeter",
    )


@list_collective_offer_templates_blueprint.route("/batch/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_validate_collective_offer_templates() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_collective_offers_templates()

    _batch_validate_or_reject_collective_offer_templates(OfferValidationStatus.APPROVED, form.object_ids_list)
    return _render_collective_offers_templates(form.object_ids_list)


@list_collective_offer_templates_blueprint.route("/batch/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_collective_offer_templates() -> utils.BackofficeResponse:
    form = collective_offer_forms.BatchRejectCollectiveOfferForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_collective_offers_templates()

    _batch_validate_or_reject_collective_offer_templates(
        OfferValidationStatus.REJECTED,
        form.object_ids_list,
        educational_models.CollectiveOfferRejectionReason(form.reason.data),
    )
    return _render_collective_offers_templates(form.object_ids_list)


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/details", methods=["GET"])
def get_collective_offer_template_details(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template_query = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter(educational_models.CollectiveOfferTemplate.id == collective_offer_template_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveOfferTemplate.venue).options(
                sa_orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                    offerers_models.OffererConfidenceRule.confidenceLevel
                ),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).options(
                    sa_orm.joinedload(offerers_models.Offerer.confidenceRule).load_only(
                        offerers_models.OffererConfidenceRule.confidenceLevel
                    ),
                    sa_orm.with_expression(
                        offerers_models.Offerer.isTopActeur,
                        offerers_models.Offerer.is_top_acteur.expression,  # type: ignore[attr-defined]
                    ),
                ),
            )
        )
    )
    collective_offer_template = collective_offer_template_query.one_or_none()

    if not collective_offer_template:
        raise NotFound()

    connect_as = get_connect_as(
        object_type="collective_offer_template",
        object_id=collective_offer_template_id,
        pc_pro_path=urls.build_pc_pro_offer_path(collective_offer_template),
    )

    return render_template(
        "collective_offer_template/details.html",
        collective_offer_template=collective_offer_template,
        connect_as=connect_as,
    )
