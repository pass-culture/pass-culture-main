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
import pcapi.core.educational.adage_backends as adage_client
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils import date as date_utils

from . import autocomplete
from . import utils
from .forms import collective_offer as collective_offer_forms
from .forms import empty as empty_forms


list_collective_offers_blueprint = utils.child_backoffice_blueprint(
    "collective_offer",
    __name__,
    url_prefix="/pro/collective_offer",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_collective_offers(
    form: collective_offer_forms.GetCollectiveOffersListForm,
) -> list[educational_models.CollectiveOffer]:
    base_query = educational_models.CollectiveOffer.query.options(
        sa.orm.load_only(
            educational_models.CollectiveOffer.id,
            educational_models.CollectiveOffer.name,
            educational_models.CollectiveOffer.subcategoryId,
            educational_models.CollectiveOffer.dateCreated,
            educational_models.CollectiveOffer.validation,
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.venue).load_only(
            offerers_models.Venue.managingOffererId, offerers_models.Venue.name
        )
        # needed to check if stock is bookable and compute initial/remaining stock:
        .joinedload(offerers_models.Venue.managingOfferer).load_only(
            offerers_models.Offerer.name, offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus
        ),
    )
    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        base_query = base_query.filter(educational_models.CollectiveOffer.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(educational_models.CollectiveOffer.dateCreated <= to_datetime)

    if form.category.data:
        base_query = base_query.filter(
            educational_models.CollectiveOffer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.venue.data:
        base_query = base_query.filter(educational_models.CollectiveOffer.venueId.in_(form.venue.data))

    if form.offerer.data:
        base_query = base_query.join(educational_models.CollectiveOffer.venue).filter(
            offerers_models.Venue.managingOffererId.in_(form.offerer.data)
        )

    if form.status.data:
        base_query = base_query.filter(educational_models.CollectiveOffer.validation.in_(form.status.data))

    if form.only_validated_offerers.data:
        base_query = (
            base_query.join(educational_models.CollectiveOffer.venue)
            .join(offerers_models.Venue.managingOfferer)
            .filter(offerers_models.Offerer.isValidated)
        )

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
            base_query = base_query.filter(educational_models.CollectiveOffer.id == int(search_query))
        else:
            name_query = "%{}%".format(search_query)
            base_query = base_query.filter(educational_models.CollectiveOffer.name.ilike(name_query))

    if form.sort.data:
        base_query = base_query.order_by(getattr(educational_models.CollectiveOffer, form.sort.data))

    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1).all()


@list_collective_offers_blueprint.route("", methods=["GET"])
def list_collective_offers() -> utils.BackofficeResponse:
    form = collective_offer_forms.GetCollectiveOffersListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("collective_offer/list.html", rows=[], form=form), 400

    if form.is_empty():
        return render_template("collective_offer/list.html", rows=[], form=form)

    collective_offers = _get_collective_offers(form)

    if len(collective_offers) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        collective_offers = collective_offers[: form.limit.data]

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)

    return render_template(
        "collective_offer/list.html",
        rows=collective_offers,
        form=form,
    )


@list_collective_offers_blueprint.route("/<int:collective_offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_validate_collective_offer_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.get_or_404(collective_offer_id)

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_v3_web.collective_offer.validate_collective_offer", collective_offer_id=collective_offer.id
        ),
        div_id=f"validate-collective-offer-modal-{collective_offer.id}",
        title=f"Validation de l'offre {collective_offer.name}",
        button_text="Valider l'offre",
    )


@list_collective_offers_blueprint.route("/<int:collective_offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def validate_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.get_or_404(collective_offer_id)

    new_validation_status = OfferValidationStatus.APPROVED
    if collective_offer.validation != OfferValidationStatus.PENDING:
        flash("Seules les offres collectives en attente peuvent être validées", "warning")
        return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)
    collective_offer.validation = new_validation_status
    collective_offer.isActive = True

    try:
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        flash("Une erreur est survenue lors de la validation de l'offre", "warning")
        return redirect(request.referrer, 400)
    search.async_index_collective_offer_ids([collective_offer.id])

    flash("L'offre a bien été validée", "success")
    collective_offer.lastValidationDate = datetime.datetime.utcnow()
    collective_offer.lastValidationType = OfferValidationType.MANUAL
    recipients = (
        [collective_offer.venue.bookingEmail]
        if collective_offer.venue.bookingEmail
        else [recipient.user.email for recipient in collective_offer.venue.managingOfferer.UserOfferers]
    )

    transactional_mails.send_offer_validation_status_update_email(collective_offer, new_validation_status, recipients)

    if collective_offer.institutionId is not None:
        adage_client.notify_institution_association(serialize_collective_offer(collective_offer))

    return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)


@list_collective_offers_blueprint.route("/<int:collective_offer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_reject_collective_offer_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.get_or_404(collective_offer_id)

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_v3_web.collective_offer.reject_collective_offer", collective_offer_id=collective_offer.id
        ),
        div_id=f"reject-collective-offer-modal-{collective_offer.id}",
        title=f"Rejet de l'offre {collective_offer.name}",
        button_text="Rejeter l'offre",
    )


@list_collective_offers_blueprint.route("/<int:collective_offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def reject_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.get_or_404(collective_offer_id)

    new_validation_status = OfferValidationStatus.REJECTED
    if collective_offer.validation != OfferValidationStatus.PENDING:
        flash("Seules les offres collectives en attente peuvent être rejetées", "warning")
        return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)
    collective_offer.validation = new_validation_status

    try:
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        flash("Une erreur est survenue lors de la validation de l'offre", "warning")
        return redirect(request.referrer, 400)
    search.async_index_collective_offer_ids([collective_offer.id])

    flash("L'offre a bien été rejetée", "success")
    collective_offer.lastValidationDate = datetime.datetime.utcnow()
    collective_offer.lastValidationType = OfferValidationType.MANUAL
    recipients = (
        [collective_offer.venue.bookingEmail]
        if collective_offer.venue.bookingEmail
        else [recipient.user.email for recipient in collective_offer.venue.managingOfferer.UserOfferers]
    )

    transactional_mails.send_offer_validation_status_update_email(collective_offer, new_validation_status, recipients)

    if collective_offer.institutionId is not None:
        adage_client.notify_institution_association(serialize_collective_offer(collective_offer))

    return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)
