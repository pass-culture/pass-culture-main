import datetime

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core import search
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as user_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import atomic
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils import date as date_utils

from . import forms as collective_offer_forms


list_collective_offer_templates_blueprint = utils.child_backoffice_blueprint(
    "collective_offer_template",
    __name__,
    url_prefix="/pro/collective-offer-template",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_collective_offer_templates(
    form: collective_offer_forms.GetCollectiveOfferTemplatesListForm,
) -> list[educational_models.CollectiveOfferTemplate]:
    base_query = educational_models.CollectiveOfferTemplate.query.options(
        sa.orm.load_only(
            educational_models.CollectiveOfferTemplate.id,
            educational_models.CollectiveOfferTemplate.name,
            educational_models.CollectiveOfferTemplate.formats,
            educational_models.CollectiveOfferTemplate.dateCreated,
            educational_models.CollectiveOfferTemplate.validation,
            educational_models.CollectiveOfferTemplate.authorId,
        ),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue).load_only(
            offerers_models.Venue.managingOffererId, offerers_models.Venue.name, offerers_models.Venue.publicName
        )
        # needed to check if stock is bookable and compute initial/remaining stock:
        .joinedload(offerers_models.Venue.managingOfferer)
        .load_only(
            offerers_models.Offerer.name, offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus
        )
        .joinedload(offerers_models.Offerer.confidenceRule)
        .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue)
        .joinedload(offerers_models.Venue.confidenceRule)
        .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.flaggingValidationRules).load_only(
            offers_models.OfferValidationRule.name
        ),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.author).load_only(
            user_models.User.id,
            user_models.User.firstName,
            user_models.User.lastName,
        ),
    )
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
        base_query = base_query.join(educational_models.CollectiveOfferTemplate.venue).filter(
            offerers_models.Venue.managingOffererId.in_(form.offerer.data)
        )

    if form.status.data:
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.validation.in_(form.status.data))  # type: ignore[attr-defined]

    if form.only_validated_offerers.data:
        base_query = (
            base_query.join(educational_models.CollectiveOfferTemplate.venue)
            .join(offerers_models.Venue.managingOfferer)
            .filter(offerers_models.Offerer.isValidated)
        )

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
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


@list_collective_offer_templates_blueprint.route("", methods=["GET"])
@atomic()
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

    return render_template(
        "collective_offer_template/list.html",
        rows=collective_offer_templates,
        form=form,
        date_created_sort_url=form.get_sort_link(".list_collective_offer_templates") if form.sort.data else None,
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/validate", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_validate_collective_offer_template_form(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(
        id=collective_offer_template_id
    ).one_or_none()
    if not collective_offer_template:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.collective_offer_template.validate_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        ),
        div_id=f"validate-collective-offer-template-modal-{collective_offer_template.id}",
        title=f"Validation de l'offre vitrine {collective_offer_template.name}",
        button_text="Valider l'offre vitrine",
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/validate", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_collective_offer_template(collective_offer_template_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offer_templates(OfferValidationStatus.APPROVED, [collective_offer_template_id])
    return redirect(
        request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"),
        303,
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/reject", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_reject_collective_offer_template_form(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(
        id=collective_offer_template_id
    ).one_or_none()
    if not collective_offer_template:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.collective_offer_template.reject_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        ),
        div_id=f"reject-collective-offer-template-modal-{collective_offer_template.id}",
        title=f"Rejet de l'offre vitrine {collective_offer_template.name}",
        button_text="Rejeter l'offre vitrine",
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/reject", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_collective_offer_template(collective_offer_template_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offer_templates(OfferValidationStatus.REJECTED, [collective_offer_template_id])
    return redirect(
        request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"),
        303,
    )


def _batch_validate_or_reject_collective_offer_templates(
    validation: OfferValidationStatus, collective_offer_template_ids: list[int]
) -> bool:
    collective_offer_templates = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids),
        educational_models.CollectiveOfferTemplate.validation == OfferValidationStatus.PENDING,
    ).all()

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
        old_validation_status = collective_offer_template.validation
        new_validation_status = validation
        collective_offer_template.validation = new_validation_status
        collective_offer_template.lastValidationDate = datetime.datetime.utcnow()
        collective_offer_template.lastValidationType = OfferValidationType.MANUAL
        collective_offer_template.lastValidationAuthorUserId = current_user.id
        if validation is OfferValidationStatus.APPROVED:
            collective_offer_template.isActive = True

        try:
            db.session.flush()
        except Exception:  # pylint: disable=broad-except
            collective_offer_template_update_failed_ids.append(collective_offer_template.id)
            continue

        collective_offer_template_update_succeed_ids.append(collective_offer_template.id)

        recipients = (
            [collective_offer_template.venue.bookingEmail]
            if collective_offer_template.venue.bookingEmail
            else [recipient.user.email for recipient in collective_offer_template.venue.managingOfferer.UserOfferers]
        )

        transactional_mails.send_offer_validation_status_update_email(
            collective_offer_template, old_validation_status, new_validation_status, recipients
        )

    search.async_index_collective_offer_template_ids(
        collective_offer_template_update_succeed_ids,
        reason=search.IndexationReason.OFFER_BATCH_VALIDATION,
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
                f"Une erreur est survenue lors du rejet des offres collectives vitrine : {', '.join(map(str, collective_offer_template_update_failed_ids))}"
                if validation is OfferValidationStatus.APPROVED
                else f"Une erreur est survenue lors du rejet des offres collectives vitrine : {', '.join(map(str, collective_offer_template_update_failed_ids))}"
                "warning"
            ),
        )

    return True


@list_collective_offer_templates_blueprint.route("/batch/validate", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_collective_offer_templates_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.collective_offer_template.batch_validate_collective_offer_templates"),
        div_id="batch-validate-modal",
        title="Voulez-vous valider les offres collectives vitrine sélectionnées ?",
        button_text="Valider",
    )


@list_collective_offer_templates_blueprint.route("/batch/reject", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_collective_offer_templates_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.collective_offer_template.batch_reject_collective_offer_templates"),
        div_id="batch-reject-modal",
        title="Voulez-vous rejeter les offres collectives vitrine sélectionnées ?",
        button_text="Rejeter",
    )


@list_collective_offer_templates_blueprint.route("/batch/validate", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_validate_collective_offer_templates() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"),
            303,
        )

    _batch_validate_or_reject_collective_offer_templates(OfferValidationStatus.APPROVED, form.object_ids_list)
    return redirect(
        request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"), 303
    )


@list_collective_offer_templates_blueprint.route("/batch/reject", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_collective_offer_templates() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"),
            303,
        )

    _batch_validate_or_reject_collective_offer_templates(OfferValidationStatus.REJECTED, form.object_ids_list)
    return redirect(
        request.referrer or url_for("backoffice_web.collective_offer_template.list_collective_offer_templates"), 303
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/details", methods=["GET"])
@atomic()
def get_collective_offer_template_details(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template_query = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.id == collective_offer_template_id
    ).options(
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue).joinedload(
            offerers_models.Venue.managingOfferer
        )
    )
    collective_offer_template = collective_offer_template_query.one_or_none()
    if not collective_offer_template:
        raise NotFound()
    return render_template(
        "collective_offer_template/details.html",
        collective_offer_template=collective_offer_template,
    )
