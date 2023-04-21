import datetime

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils import date as date_utils

from . import autocomplete
from . import utils
from .forms import collective_offer_template as collective_offer_template_forms
from .forms import empty as empty_forms


list_collective_offer_templates_blueprint = utils.child_backoffice_blueprint(
    "collective_offer_template",
    __name__,
    url_prefix="/pro/collective_offer_template",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_collective_offer_templates(
    form: collective_offer_template_forms.GetCollectiveOfferTemplatesListForm,
) -> list[educational_models.CollectiveOfferTemplate]:
    base_query = educational_models.CollectiveOfferTemplate.query.options(
        sa.orm.load_only(
            educational_models.CollectiveOfferTemplate.id,
            educational_models.CollectiveOfferTemplate.name,
            educational_models.CollectiveOfferTemplate.subcategoryId,
            educational_models.CollectiveOfferTemplate.dateCreated,
            educational_models.CollectiveOfferTemplate.validation,
        ),
        sa.orm.joinedload(educational_models.CollectiveOfferTemplate.venue).load_only(
            offerers_models.Venue.managingOffererId, offerers_models.Venue.name
        )
        # needed to check if stock is bookable and compute initial/remaining stock:
        .joinedload(offerers_models.Venue.managingOfferer).load_only(
            offerers_models.Offerer.name, offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus
        ),
    )
    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.dateCreated <= to_datetime)

    if form.category.data:
        base_query = base_query.filter(
            educational_models.CollectiveOfferTemplate.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.venue.data:
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.venueId.in_(form.venue.data))

    if form.offerer.data:
        base_query = base_query.join(educational_models.CollectiveOfferTemplate.venue).filter(
            offerers_models.Venue.managingOffererId.in_(form.offerer.data)
        )

    if form.status.data:
        base_query = base_query.filter(educational_models.CollectiveOfferTemplate.validation.in_(form.status.data))

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
        base_query = base_query.order_by(getattr(educational_models.CollectiveOfferTemplate, form.sort.data))

    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1).all()


@list_collective_offer_templates_blueprint.route("", methods=["GET"])
def list_collective_offer_templates() -> utils.BackofficeResponse:
    form = collective_offer_template_forms.GetCollectiveOfferTemplatesListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("collective_offer_template/list.html", rows=[], form=form), 400

    if form.is_empty():
        return render_template("collective_offer_template/list.html", rows=[], form=form)

    collective_offer_templates = _get_collective_offer_templates(form)

    if len(collective_offer_templates) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        collective_offer_templates = collective_offer_templates[: form.limit.data]

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)

    return render_template(
        "collective_offer_template/list.html",
        rows=collective_offer_templates,
        form=form,
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_validate_collective_offer_template_form(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.get_or_404(
        collective_offer_template_id
    )

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_v3_web.collective_offer_template.validate_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        ),
        div_id=f"validate-collective-offer-template-modal-{collective_offer_template.id}",
        title=f"Validation de l'offre vitrine {collective_offer_template.name}",
        button_text="Valider l'offre vitrine",
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def validate_collective_offer_template(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.get_or_404(
        collective_offer_template_id
    )

    new_validation_status = OfferValidationStatus.APPROVED
    if collective_offer_template.validation != OfferValidationStatus.PENDING:
        flash("Seules les offres collectives vitrines en attente peuvent être validées", "warning")
        return redirect(
            request.referrer or url_for("backoffice_v3_web.collective_offer_template.list_collective_offer_templates"),
            303,
        )
    collective_offer_template.validation = new_validation_status
    collective_offer_template.isActive = True

    try:
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        flash("Une erreur est survenue lors de la validation de l'offre vitrine", "warning")
        return redirect(request.referrer, 400)
    search.async_index_collective_offer_template_ids([collective_offer_template.id])

    flash("L'offre a bien été validée", "success")
    collective_offer_template.lastValidationDate = datetime.datetime.utcnow()
    collective_offer_template.lastValidationType = OfferValidationType.MANUAL
    recipients = (
        [collective_offer_template.venue.bookingEmail]
        if collective_offer_template.venue.bookingEmail
        else [recipient.user.email for recipient in collective_offer_template.venue.managingOfferer.UserOfferers]
    )

    transactional_mails.send_offer_validation_status_update_email(
        collective_offer_template, new_validation_status, recipients
    )

    return redirect(
        request.referrer or url_for("backoffice_v3_web.collective_offer_template.list_collective_offer_templates"), 303
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_reject_collective_offer_template_form(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.get_or_404(
        collective_offer_template_id
    )

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_v3_web.collective_offer_template.reject_collective_offer_template",
            collective_offer_template_id=collective_offer_template.id,
        ),
        div_id=f"reject-collective-offer-template-modal-{collective_offer_template.id}",
        title=f"Rejet de l'offre vitrine {collective_offer_template.name}",
        button_text="Rejeter l'offre vitrine",
    )


@list_collective_offer_templates_blueprint.route("/<int:collective_offer_template_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def reject_collective_offer_template(collective_offer_template_id: int) -> utils.BackofficeResponse:
    collective_offer_template = educational_models.CollectiveOfferTemplate.query.get_or_404(
        collective_offer_template_id
    )

    new_validation_status = OfferValidationStatus.REJECTED
    if collective_offer_template.validation != OfferValidationStatus.PENDING:
        flash("Seules les offres collectives vitrines en attente peuvent être rejetées", "warning")
        return redirect(
            request.referrer or url_for("backoffice_v3_web.collective_offer_template.list_collective_offer_templates"),
            303,
        )
    collective_offer_template.validation = new_validation_status

    try:
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        flash("Une erreur est survenue lors de la validation de l'offre vitrine", "warning")
        return redirect(request.referrer, 400)
    search.async_index_collective_offer_template_ids([collective_offer_template.id])

    flash("L'offre vitrine a bien été rejetée", "success")
    collective_offer_template.lastValidationDate = datetime.datetime.utcnow()
    collective_offer_template.lastValidationType = OfferValidationType.MANUAL
    recipients = (
        [collective_offer_template.venue.bookingEmail]
        if collective_offer_template.venue.bookingEmail
        else [recipient.user.email for recipient in collective_offer_template.venue.managingOfferer.UserOfferers]
    )

    transactional_mails.send_offer_validation_status_update_email(
        collective_offer_template, new_validation_status, recipients
    )

    return redirect(
        request.referrer or url_for("backoffice_v3_web.collective_offer_template.list_collective_offer_templates"), 303
    )
