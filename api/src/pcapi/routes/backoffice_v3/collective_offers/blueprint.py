import datetime

from flask import current_app as app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.routes.backoffice_v3 import autocomplete
from pcapi.routes.backoffice_v3 import utils
from pcapi.routes.backoffice_v3.collective_offers.forms import EditCollectiveOfferPrice
from pcapi.routes.backoffice_v3.forms import empty as empty_forms
from pcapi.routes.backoffice_v3.forms import offer as offer_forms
from pcapi.utils import date as date_utils


blueprint = utils.child_backoffice_blueprint(
    "collective_offer",
    __name__,
    url_prefix="/pro/collective_offer",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_collective_offers(
    form: offer_forms.GetCollectiveOffersListForm,
) -> list[educational_models.CollectiveOffer]:
    base_query = educational_models.CollectiveOffer.query.options(
        sa.orm.load_only(
            educational_models.CollectiveOffer.id,
            educational_models.CollectiveOffer.name,
            educational_models.CollectiveOffer.subcategoryId,
            educational_models.CollectiveOffer.dateCreated,
            educational_models.CollectiveOffer.validation,
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).load_only(
            educational_models.CollectiveStock.beginningDatetime
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
        base_query = base_query.order_by(
            getattr(getattr(educational_models.CollectiveOffer, form.sort.data), form.order.data)()
        )

    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1).all()


@blueprint.route("", methods=["GET"])
def list_collective_offers() -> utils.BackofficeResponse:
    form = offer_forms.GetCollectiveOffersListForm(formdata=utils.get_query_params())
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
        date_created_sort_url=form.get_sort_link(".list_collective_offers") if form.sort.data else None,
    )


@blueprint.route("/<int:collective_offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
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


@blueprint.route("/<int:collective_offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.APPROVED, [collective_offer_id])
    return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)


def _batch_validate_or_reject_collective_offers(
    validation: offer_mixin.OfferValidationStatus, collective_offer_ids: list[int]
) -> bool:
    collective_offers = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id.in_(collective_offer_ids),
        educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
    ).all()

    if len(collective_offer_ids) != len(collective_offers):
        flash(
            "Seules les offres collectives en attente peuvent être validées"
            if validation is offer_mixin.OfferValidationStatus.APPROVED
            else "Seules les offres collectives en attente peuvent être rejetées",
            "danger",
        )
        return False

    collective_offer_update_succeed_ids: list[int] = []
    collective_offer_update_failed_ids: list[int] = []

    for collective_offer in collective_offers:
        new_validation_status = validation
        collective_offer.validation = new_validation_status
        collective_offer.lastValidationDate = datetime.datetime.utcnow()
        collective_offer.lastValidationType = offer_mixin.OfferValidationType.MANUAL

        if validation is offer_mixin.OfferValidationStatus.APPROVED:
            collective_offer.isActive = True

        try:
            db.session.commit()
        except Exception:  # pylint: disable=broad-except
            collective_offer_update_failed_ids.append(collective_offer.id)
            continue

        collective_offer_update_succeed_ids.append(collective_offer.id)

        recipients = (
            [collective_offer.venue.bookingEmail]
            if collective_offer.venue.bookingEmail
            else [recipient.user.email for recipient in collective_offer.venue.managingOfferer.UserOfferers]
        )

        transactional_mails.send_offer_validation_status_update_email(
            collective_offer, new_validation_status, recipients
        )

        if collective_offer.institutionId is not None:
            adage_client.notify_institution_association(serialize_collective_offer(collective_offer))

    search.async_index_collective_offer_ids(collective_offer_update_succeed_ids)

    if len(collective_offer_update_succeed_ids) == 1:
        flash(
            "L'offre collective a bien été validée"
            if validation is offer_mixin.OfferValidationStatus.APPROVED
            else "L'offre collective a bien été rejetée",
            "success",
        )
    elif collective_offer_update_succeed_ids:
        flash(
            f"Les offres collectives {', '.join(map(str, collective_offer_update_succeed_ids))} ont bien été validées"
            if validation is offer_mixin.OfferValidationStatus.APPROVED
            else f"Les offres collectives {','.join(map(str, collective_offer_update_succeed_ids))} ont bien été rejetées",
            "success",
        )

    if len(collective_offer_update_failed_ids) > 0:
        flash(
            f"Une erreur est survenue lors de la validation des offres collectives : {', '.join(map(str, collective_offer_update_failed_ids))}"
            if validation is offer_mixin.OfferValidationStatus.APPROVED
            else f"Une erreur est survenue lors du rejet des offres collectives : {', '.join(map(str, collective_offer_update_failed_ids))}",
            "danger",
        )
    return True


@blueprint.route("/<int:collective_offer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
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


@blueprint.route("/<int:collective_offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.REJECTED, [collective_offer_id])
    return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)


@blueprint.route("/batch/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_collective_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.collective_offer.batch_validate_collective_offers"),
        div_id="batch-validate-modal",
        title="Voulez-vous valider les offres collectives sélectionnées ?",
        button_text="Valider",
    )


@blueprint.route("/batch/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_collective_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.collective_offer.batch_reject_collective_offers"),
        div_id="batch-reject-modal",
        title="Voulez-vous rejeter les offres collectives sélectionnées ?",
        button_text="Rejeter",
    )


@blueprint.route("/batch/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_validate_collective_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash("L'un des identifiants sélectionnés est invalide", "danger")
        return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)

    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.APPROVED, form.object_ids_list)
    return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)


@blueprint.route("/batch/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_collective_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash("L'un des identifiants sélectionnés est invalide", "danger")
        return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)

    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.REJECTED, form.object_ids_list)
    return redirect(request.referrer or url_for("backoffice_v3_web.collective_offer.list_collective_offers"), 303)


def _is_collective_offer_price_editable(collective_offer: educational_models.CollectiveOffer) -> bool:
    # if the offer has no stock it has no price therefore its price cannot be updated
    if not collective_offer.collectiveStock:
        return False

    # if the offer is not USED it cannot be edited
    if not (collective_offer.isSoldOut and collective_offer.hasBeginningDatetimePassed):
        return False

    # cannot update an offer's price while the cashflow generation script is running
    if app.redis_client.exists(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK):  # type: ignore [attr-defined]
        return False

    # cannot update an offer's stock if it already has a processed pricing
    pricing_query = (
        db.session.query(finance_models.Pricing.id)
        .join(educational_models.CollectiveBooking, finance_models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == collective_offer.id,
            finance_models.Pricing.status.in_(
                (finance_models.PricingStatus.PROCESSED, finance_models.PricingStatus.INVOICED)
            ),
        )
    )
    if pricing_query.one_or_none():
        return False

    return True


@blueprint.route("/<int:collective_offer_id>/details", methods=["GET"])
def get_collective_offer_details(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer_query = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id == collective_offer_id
    ).options(
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
            educational_models.CollectiveStock.collectiveBookings
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.venue),
        sa.orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(offerers_models.Venue.managingOfferer),
    )
    collective_offer = collective_offer_query.one_or_none()
    if not collective_offer:
        flash("Cette offre collective n'existe pas", "warning")
        return redirect(url_for("backoffice_v3_web.collective_offer.list_collective_offers"), code=303)

    is_collective_offer_price_editable = _is_collective_offer_price_editable(collective_offer)
    return render_template(
        "collective_offer/details.html",
        collective_offer=collective_offer,
        is_collective_offer_price_editable=is_collective_offer_price_editable,
    )


@blueprint.route("/<int:collective_offer_id>/update-price", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def edit_collective_offer_price(collective_offer_id: int) -> utils.BackofficeResponse:
    redirect_url = request.referrer or url_for(
        "backoffice_v3_web.collective_offer.get_collective_offer_details", collective_offer_id=collective_offer_id
    )
    collective_offer = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == collective_offer_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
                offerers_models.Venue.managingOfferer
            ),
        )
        .one_or_none()
    )

    if not collective_offer:
        flash("Cette offre collective n'existe pas", "warning")
        return redirect(redirect_url, code=303)

    is_collective_offer_price_editable = _is_collective_offer_price_editable(collective_offer)

    if not is_collective_offer_price_editable:
        flash("Cette offre n'est pas modifiable", "warning")
        return redirect(redirect_url, code=303)

    form = EditCollectiveOfferPrice()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(redirect_url, code=303)
    price = form.price.data
    number_of_tickets = form.numberOfTickets.data

    if price > collective_offer.collectiveStock.price:
        flash("Impossible d'augmenter le prix")
        return redirect(redirect_url, code=303)

    if number_of_tickets > collective_offer.collectiveStock.numberOfTickets:
        flash("Impossible d'augmenter le nombre de participants", "warning")
        return redirect(redirect_url, code=303)

    collective_booking = (
        educational_models.CollectiveBooking.query.join(
            educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock
        )
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == collective_offer.id,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.CANCELLED,
        )
        .one()
    )

    try:
        finance_api.cancel_pricing(booking=collective_booking, reason=finance_models.PricingLogReason.CHANGE_AMOUNT)
    except finance_exceptions.NonCancellablePricingError:
        flash("Impossible, réservation est déjà remboursée (ou en cours de remboursement)", "warning")
        db.session.rollback()
        return redirect(redirect_url, code=303)

    collective_offer.collectiveStock.price = price
    collective_offer.collectiveStock.numberOfTickets = number_of_tickets
    db.session.commit()

    flash("L'offre collective a été mise à jour", "success")
    return redirect(redirect_url, code=303)


@blueprint.route("/<int:collective_offer_id>/update-price", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_collective_offer_price_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.get_or_404(collective_offer_id)
    form = EditCollectiveOfferPrice(
        price=collective_offer.collectiveStock.price,
        numberOfTickets=collective_offer.collectiveStock.numberOfTickets,
    )
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_v3_web.collective_offer.edit_collective_offer_price", collective_offer_id=collective_offer_id
        ),
        div_id="update-collective-offer-price",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Ajuster le prix de l'offre collective {collective_offer_id}",
        button_text="Ajuster le prix",
    )
