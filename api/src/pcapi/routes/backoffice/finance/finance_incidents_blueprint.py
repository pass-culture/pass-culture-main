from datetime import datetime
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

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.finance_incidents.finance_incident_notification import send_finance_incident_emails
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.finance import forms
from pcapi.routes.backoffice.finance import validation
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.offerers import forms as offerer_forms
from pcapi.utils import date as date_utils


TOKEN_LENGTH = 6


finance_incidents_blueprint = utils.child_backoffice_blueprint(
    "finance_incidents",
    __name__,
    url_prefix="/finance/incidents",
    permission=perm_models.Permissions.READ_INCIDENTS,
)


def _get_incidents(
    form: forms.GetIncidentsSearchForm,
) -> list[finance_models.FinanceIncident]:
    query = (
        finance_models.FinanceIncident.query.join(finance_models.FinanceIncident.venue)
        .outerjoin(finance_models.FinanceIncident.booking_finance_incidents)
        .outerjoin(finance_models.BookingFinanceIncident.booking)
        .outerjoin(bookings_models.Booking.stock)
        .outerjoin(finance_models.BookingFinanceIncident.collectiveBooking)
        .outerjoin(educational_models.CollectiveBooking.collectiveStock)
    )

    if form.status.data:
        # When filtering on status, always exclude closed incidents
        query = query.filter(
            finance_models.FinanceIncident.status.in_(form.status.data),
            sa.not_(finance_models.FinanceIncident.isClosed),
        )

    if form.offerer.data:
        query = query.filter(offerer_models.Venue.managingOffererId.in_(form.offerer.data))

    if form.venue.data:
        query = query.filter(offerer_models.Venue.id.in_(form.venue.data))

    if form.from_date.data or form.to_date.data:
        query = query.join(
            history_models.ActionHistory,
            sa.and_(
                history_models.ActionHistory.financeIncidentId == finance_models.FinanceIncident.id,
                history_models.ActionHistory.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED,
            ),
        )

        if form.from_date.data:
            from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.min.time())
            query = query.filter(history_models.ActionHistory.actionDate >= from_datetime)

        if form.to_date.data:
            to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.max.time())
            query = query.filter(history_models.ActionHistory.actionDate <= to_datetime)

    if form.q.data:
        search_query = form.q.data
        or_filters = []

        if search_query.isnumeric():
            integer_query = int(search_query)
            or_filters.extend(
                [
                    finance_models.FinanceIncident.id == integer_query,
                    bookings_models.Booking.id == integer_query,
                    offers_models.Stock.offerId == integer_query,
                    educational_models.CollectiveBooking.id == integer_query,
                    educational_models.CollectiveStock.collectiveOfferId == integer_query,
                ]
            )

        if len(search_query) == TOKEN_LENGTH:
            or_filters.append(bookings_models.Booking.token == search_query)

        if or_filters:
            query = query.filter(sa.or_(*or_filters))
        else:
            flash("Le format de la recherche ne correspond ni à un ID ni à une contremarque", "info")
            query = query.filter(sa.false)

    query = query.options(
        sa.orm.contains_eager(finance_models.FinanceIncident.venue)
        .load_only(offerer_models.Venue.id, offerer_models.Venue.name, offerer_models.Venue.publicName)
        .joinedload(offerer_models.Venue.managingOfferer)
        .load_only(offerer_models.Offerer.id, offerer_models.Offerer.name),
        sa.orm.contains_eager(finance_models.FinanceIncident.booking_finance_incidents)
        .load_only(finance_models.BookingFinanceIncident.id, finance_models.BookingFinanceIncident.newTotalAmount)
        .contains_eager(finance_models.BookingFinanceIncident.booking)
        .load_only(bookings_models.Booking.amount, bookings_models.Booking.quantity),
        sa.orm.contains_eager(finance_models.FinanceIncident.booking_finance_incidents)
        .contains_eager(finance_models.BookingFinanceIncident.collectiveBooking)
        .load_only(educational_models.CollectiveBooking.id)
        .contains_eager(educational_models.CollectiveBooking.collectiveStock)
        .load_only(educational_models.CollectiveStock.price),
        sa.orm.contains_eager(finance_models.FinanceIncident.booking_finance_incidents)
        .joinedload(finance_models.BookingFinanceIncident.finance_events)  # because of: isClosed
        .load_only(finance_models.FinanceEvent.id),
    )

    return query.order_by(sa.desc(finance_models.FinanceIncident.id)).all()


@finance_incidents_blueprint.route("", methods=["GET"])
def list_incidents() -> utils.BackofficeResponse:
    search_form = forms.GetIncidentsSearchForm(formdata=utils.get_query_params())

    incidents = _get_incidents(search_form)

    autocomplete.prefill_offerers_choices(search_form.offerer)
    autocomplete.prefill_venues_choices(search_form.venue)

    return render_template(
        "finance/incidents/list.html",
        rows=incidents,
        form=search_form,
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/cancel", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_finance_incident_cancellation_form(finance_incident_id: int) -> utils.BackofficeResponse:
    form = offerer_forms.CommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.finance_incidents.cancel_finance_incident", finance_incident_id=finance_incident_id
        ),
        div_id=f"reject-finance-incident-modal-{finance_incident_id}",
        title="Annuler l'incident",
        button_text="Confirmer l'annulation",
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def cancel_finance_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident: finance_models.FinanceIncident = _get_incident(finance_incident_id)

    form = offerer_forms.CommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=incident.id), 303)
    try:
        finance_api.cancel_finance_incident(
            incident=incident,
            comment=form.comment.data,
            author=current_user,
        )
    except finance_exceptions.FinanceIncidentAlreadyCancelled:
        flash("L'incident a déjà été annulé", "warning")
    except finance_exceptions.FinanceIncidentAlreadyValidated:
        flash("Impossible d'annuler un incident déjà validé", "warning")
    else:
        flash("L'incident a été annulé", "success")

    return redirect(url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=incident.id), 303)


@finance_incidents_blueprint.route("/<int:finance_incident_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = finance_models.FinanceIncident.query.filter_by(id=finance_incident_id).one_or_none()
    if incident is None:
        raise NotFound()

    if incident.kind.value == finance_models.IncidentType.COMMERCIAL_GESTURE.value:
        return redirect(
            url_for("backoffice_web.finance_incidents.get_commercial_gesture", finance_incident_id=finance_incident_id),
            303,
        )

    if incident.kind.value == finance_models.IncidentType.OVERPAYMENT.value:
        return redirect(
            url_for(
                "backoffice_web.finance_incidents.get_incident_overpayment", finance_incident_id=finance_incident_id
            ),
            303,
        )

    raise NotFound()


@finance_incidents_blueprint.route("/overpayment/<int:finance_incident_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_incident_overpayment(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = _get_incident(finance_incident_id, kind=finance_models.IncidentType.OVERPAYMENT)
    bookings = [
        (booking_incident.booking or booking_incident.collectiveBooking)
        for booking_incident in incident.booking_finance_incidents
    ]
    bookings_total_amount = sum(booking.total_amount for booking in bookings)
    reimbursement_pricings = [booking.reimbursement_pricing for booking in bookings if booking.reimbursement_pricing]
    initial_reimbursement_amount = sum(pricing.amount for pricing in reimbursement_pricings) * -1

    return render_template(
        "finance/incidents/get_overpayment.html",
        booking_finance_incidents=incident.booking_finance_incidents,
        incident=incident,
        active_tab=request.args.get("active_tab", "bookings"),
        bookings_total_amount=bookings_total_amount,
        initial_reimbursement_amount=initial_reimbursement_amount,
    )


@finance_incidents_blueprint.route("/commercial-gesture/<int:finance_incident_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_commercial_gesture(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = _get_incident(finance_incident_id, kind=finance_models.IncidentType.COMMERCIAL_GESTURE)
    commercial_gesture_amount = sum(
        (booking_finance_incident.commercial_gesture_amount or 0)
        for booking_finance_incident in incident.booking_finance_incidents
    )
    bookings_total_amount = sum(
        (booking_incident.booking or booking_incident.collectiveBooking).total_amount
        for booking_incident in incident.booking_finance_incidents
    )

    return render_template(
        "finance/incidents/get_commercial_gesture.html",
        incident=incident,
        commercial_gesture_amount=commercial_gesture_amount,
        bookings_total_amount=bookings_total_amount,
        active_tab=request.args.get("active_tab", "bookings"),
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/history", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_history(finance_incident_id: int) -> utils.BackofficeResponse:
    actions = (
        history_models.ActionHistory.query.filter_by(financeIncidentId=finance_incident_id)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .options(
            sa.orm.joinedload(history_models.ActionHistory.user).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            sa.orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
        )
        .all()
    )

    return render_template(
        "finance/incidents/get/details/history.html",
        actions=actions,
        form=offerer_forms.CommentForm(),
        dst=url_for("backoffice_web.finance_incidents.comment_incident", finance_incident_id=finance_incident_id),
    )


@finance_incidents_blueprint.route("/individual-bookings/overpayment-creation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_individual_bookings_overpayment_creation_form() -> utils.BackofficeResponse:
    form = forms.BookingOverPaymentIncidentForm()
    additional_data = {}
    alert = None

    if form.object_ids.data:
        bookings = (
            bookings_models.Booking.query.options(
                sa.orm.joinedload(bookings_models.Booking.user).load_only(
                    users_models.User.firstName, users_models.User.lastName, users_models.User.email
                ),
                sa.orm.joinedload(bookings_models.Booking.pricings).load_only(
                    finance_models.Pricing.status, finance_models.Pricing.amount, finance_models.Pricing.creationDate
                ),
                sa.orm.joinedload(bookings_models.Booking.stock)
                .load_only(offers_models.Stock.id)
                .joinedload(offers_models.Stock.offer)
                .load_only(offers_models.Offer.name),
                sa.orm.joinedload(bookings_models.Booking.venue).load_only(
                    offerer_models.Venue.publicName, offerer_models.Venue.name
                ),
            )
            .filter(
                bookings_models.Booking.id.in_(form.object_ids_list),
                bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
            )
            .all()
        )

        if not (valid := validation.check_incident_bookings(bookings)):
            return render_template(
                "components/turbo/modal_empty_form.html",
                form=empty_forms.BatchForm(),
                messages=valid.messages,
            )

        min_amount, max_amount = validation.get_overpayment_incident_amount_interval(bookings)

        form.total_amount.data = max_amount
        additional_data = _initialize_additional_data(bookings)
        if len(bookings) > 1:
            form.total_amount.flags.readonly = True
            alert = (
                "Le montant n'est pas modifiable parce qu'il n'est possible de créer qu'un "
                "incident trop perçu total si plusieurs réservations sont sélectionnées."
            )
        else:
            form.total_amount.flags.max = max_amount
            form.total_amount.flags.min = min_amount

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.finance_incidents.create_individual_booking_overpayment"),
        div_id="overpayment-creation-modal",
        title="Création d'un incident",
        button_text="Créer l'incident",
        additional_data=additional_data,
        alert=alert,
    )


@finance_incidents_blueprint.route("/individual-bookings/commercial-gesture-creation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_individual_bookings_commercial_gesture_creation_form() -> utils.BackofficeResponse:
    form = forms.CommercialGestureCreationForm()
    additional_data = {}

    if form.object_ids.data:
        bookings = (
            bookings_models.Booking.query.options(
                sa.orm.joinedload(bookings_models.Booking.user).load_only(
                    users_models.User.firstName, users_models.User.lastName, users_models.User.email
                ),
                sa.orm.joinedload(bookings_models.Booking.pricings).load_only(
                    finance_models.Pricing.status, finance_models.Pricing.amount, finance_models.Pricing.creationDate
                ),
                sa.orm.joinedload(bookings_models.Booking.stock)
                .load_only(offers_models.Stock.id)
                .joinedload(offers_models.Stock.offer)
                .load_only(offers_models.Offer.name),
                sa.orm.joinedload(bookings_models.Booking.venue).load_only(
                    offerer_models.Venue.publicName, offerer_models.Venue.name
                ),
            )
            .filter(
                bookings_models.Booking.id.in_(form.object_ids_list),
                bookings_models.Booking.status == bookings_models.BookingStatus.CANCELLED,
            )
            .all()
        )

        if not (valid := validation.check_commercial_gesture_bookings(bookings)):
            return render_template(
                "components/turbo/modal_empty_form.html",
                form=empty_forms.BatchForm(),
                messages=valid.messages,
            )

        min_amount, max_amount = validation.get_commercial_gesture_amount_interval(bookings)
        form.total_amount.data = max_amount
        form.total_amount.flags.max = max_amount
        form.total_amount.flags.min = min_amount

        additional_data = _initialize_additional_data(bookings)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.finance_incidents.create_individual_booking_commercial_gesture"),
        div_id="commercial-gesture-creation-modal",
        title="Création d'un geste commercial",
        button_text="Créer le geste commercial",
        additional_data=additional_data,
    )


@finance_incidents_blueprint.route(
    "/collective-bookings/<int:collective_booking_id>/overpayment-creation-form", methods=["GET", "POST"]
)
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_collective_booking_overpayment_creation_form(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking: educational_models.CollectiveBooking = (
        educational_models.CollectiveBooking.query.filter_by(id=collective_booking_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.name
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.pricings).load_only(
                finance_models.Pricing.amount,
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.beginningDatetime, educational_models.CollectiveStock.numberOfTickets
            )
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(educational_models.CollectiveOffer.name),
        )
        .one_or_none()
    )
    if not collective_booking:
        raise NotFound()

    form = forms.CollectiveOverPaymentIncidentCreationForm()
    additional_data = _initialize_collective_booking_additional_data(collective_booking)

    if not (valid := validation.check_incident_collective_booking(collective_booking)):
        return render_template(
            "components/turbo/modal_empty_form.html",
            form=empty_forms.BatchForm(),
            messages=valid.messages,
            div_id=f"overpayment-creation-modal-{collective_booking_id}",
        )

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.finance_incidents.create_collective_booking_overpayment",
            collective_booking_id=collective_booking_id,
        ),
        div_id=f"overpayment-creation-modal-{collective_booking_id}",
        title="Création d'un incident",
        button_text="Créer l'incident",
        additional_data=additional_data,
    )


@finance_incidents_blueprint.route(
    "/collective-bookings/<int:collective_booking_id>/commercial-gesture-creation-form",
    methods=["GET", "POST"],
)
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_collective_booking_commercial_gesture_creation_form(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking: educational_models.CollectiveBooking = (
        educational_models.CollectiveBooking.query.filter_by(id=collective_booking_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.name
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.pricings).load_only(
                finance_models.Pricing.amount,
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.beginningDatetime, educational_models.CollectiveStock.numberOfTickets
            )
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(educational_models.CollectiveOffer.name),
        )
        .one_or_none()
    )
    if not collective_booking:
        raise NotFound()

    form = forms.CollectiveCommercialGestureCreationForm()
    additional_data = _initialize_collective_booking_additional_data(collective_booking)

    if not (valid := validation.check_commercial_gesture_collective_booking(collective_booking)):
        return render_template(
            "components/turbo/modal_empty_form.html",
            form=empty_forms.BatchForm(),
            messages=valid.messages,
            div_id=f"commercial-gesture-creation-modal-{collective_booking_id}",
        )

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.finance_incidents.create_collective_booking_commercial_gesture",
            collective_booking_id=collective_booking_id,
        ),
        div_id=f"commercial-gesture-creation-modal-{collective_booking_id}",
        title="Création d'un geste commercial",
        button_text="Créer le geste commercial",
        additional_data=additional_data,
    )


@finance_incidents_blueprint.route("/individual-bookings/create-overpayment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def create_individual_booking_overpayment() -> utils.BackofficeResponse:
    form = forms.BookingOverPaymentIncidentForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    amount = form.total_amount.data

    bookings = (
        bookings_models.Booking.query.options(
            sa.orm.joinedload(bookings_models.Booking.pricings).load_only(finance_models.Pricing.amount),
            sa.orm.joinedload(bookings_models.Booking.deposit).load_only(finance_models.Deposit.amount),
            sa.orm.joinedload(bookings_models.Booking.deposit)
            .joinedload(finance_models.Deposit.user)
            .load_only(users_models.User.id),
        )
        .filter(
            bookings_models.Booking.id.in_(form.object_ids_list),
            bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
        )
        .all()
    )

    if len(bookings) != len(form.object_ids_list):
        flash(
            'Au moins une des réservations sélectionnées est dans un état différent de "remboursé".',
            "warning",
        )
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)

    if not (valid := validation.check_incident_bookings(bookings) and validation.check_total_amount(amount, bookings)):
        for message in valid.messages:
            flash(message, "warning")
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)

    incident = finance_api.create_overpayment_finance_incident(
        bookings=bookings,
        author=current_user,
        origin=form.origin.data,
        amount=amount,
    )
    incident_url = url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=incident.id)

    flash(
        Markup('Un nouvel <a href="{url}">incident</a> a été créé pour {count} réservation{s}.').format(
            url=incident_url, count=len(bookings), s="" if len(bookings) == 1 else "s"
        ),
        "success",
    )
    return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)


@finance_incidents_blueprint.route("/individual-bookings/create-commercial-gesture", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def create_individual_booking_commercial_gesture() -> utils.BackofficeResponse:
    form = forms.CommercialGestureCreationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    amount = form.total_amount.data

    bookings = (
        bookings_models.Booking.query.options(
            sa.orm.joinedload(bookings_models.Booking.pricings).load_only(finance_models.Pricing.amount),
            sa.orm.joinedload(bookings_models.Booking.deposit)
            .load_only(finance_models.Deposit.amount)
            .joinedload(finance_models.Deposit.user)
            .load_only(users_models.User.id),
        )
        .filter(
            bookings_models.Booking.id.in_(form.object_ids_list),
            bookings_models.Booking.status == bookings_models.BookingStatus.CANCELLED,
        )
        .all()
    )

    if len(bookings) != len(form.object_ids_list):
        flash(
            'Au moins une des réservations sélectionnées est dans un état différent de "annulée".',
            "warning",
        )
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)

    if not (
        valid := validation.check_commercial_gesture_bookings(bookings)
        and validation.check_commercial_gesture_total_amount(amount, bookings)
    ):
        for message in valid.messages:
            flash(message, "warning")
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)

    commercial_gesture = finance_api.create_finance_commercial_gesture(
        bookings=bookings,
        amount=amount,
        author=current_user,
        origin=form.origin.data,
    )
    incident_url = url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=commercial_gesture.id)

    flash(
        Markup('Un nouveau <a href="{url}">geste commercial</a> a été créé pour {count} réservation{s}.').format(
            url=incident_url, count=len(bookings), s="" if len(bookings) == 1 else "s"
        ),
        "success",
    )

    return redirect(request.referrer or url_for("backoffice_web.collective_bookings.list_collective_bookings"), 303)


@finance_incidents_blueprint.route(
    "/collective-bookings/<int:collective_booking_id>/create-overpayment", methods=["POST"]
)
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def create_collective_booking_overpayment(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = educational_models.CollectiveBooking.query.filter_by(id=collective_booking_id).one_or_none()
    if not collective_booking:
        raise NotFound()

    redirect_url = request.referrer or url_for("backoffice_web.collective_bookings.list_collective_bookings")
    form = forms.CollectiveOverPaymentIncidentCreationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(redirect_url, 303)

    if not (valid := validation.check_incident_collective_booking(collective_booking)):
        for message in valid.messages:
            flash(message, "warning")
        return redirect(redirect_url, 303)

    incident = finance_api.create_overpayment_finance_incident_collective_booking(
        collective_booking,
        author=current_user,
        origin=form.origin.data,
    )
    incident_url = url_for(
        "backoffice_web.finance_incidents.get_incident",
        finance_incident_id=incident.id,
    )

    flash(Markup('Un nouvel <a href="{url}">incident</a> a été créé.').format(url=incident_url), "success")
    return redirect(redirect_url, 303)


@finance_incidents_blueprint.route(
    "/collective-bookings/<int:collective_booking_id>/create-commercial-gesture", methods=["POST"]
)
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def create_collective_booking_commercial_gesture(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = educational_models.CollectiveBooking.query.filter_by(id=collective_booking_id).one_or_none()
    if not collective_booking:
        raise NotFound()

    redirect_url = request.referrer or url_for("backoffice_web.collective_bookings.list_collective_bookings")
    form = forms.CollectiveCommercialGestureCreationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(redirect_url, 303)

    if not (valid := validation.check_commercial_gesture_collective_booking(collective_booking)):
        for message in valid.messages:
            flash(message, "warning")
        return redirect(redirect_url, 303)

    incident = finance_api.create_finance_commercial_gesture_collective_booking(
        collective_booking,
        author=current_user,
        origin=form.origin.data,
    )
    incident_url = url_for(
        "backoffice_web.finance_incidents.get_incident",
        finance_incident_id=incident.id,
    )

    flash(Markup('Un nouveau <a href="{url}">geste commercial</a> a été créé.').format(url=incident_url), "success")
    return redirect(redirect_url, 303)


def _initialize_additional_data(bookings: list[bookings_models.Booking]) -> dict:
    additional_data: dict[str, typing.Any] = {"Lieu": bookings[0].venue.common_name}

    if len(bookings) == 1:
        booking = bookings[0]

        additional_data["ID de la réservation"] = booking.id
        additional_data["Statut de la réservation"] = filters.format_booking_status(booking)
        additional_data["Contremarque"] = booking.token
        additional_data["Nom de l'offre"] = booking.stock.offer.name
        additional_data["Bénéficiaire"] = booking.user.full_name
        additional_data["Montant de la réservation"] = filters.format_amount(booking.total_amount)
        additional_data["Montant remboursé à l'acteur"] = filters.format_amount(
            -finance_utils.to_euros(booking.reimbursement_pricing.amount) if booking.reimbursement_pricing else 0
        )
    else:
        additional_data["Nombre de réservations"] = len(bookings)
        additional_data["Montant des réservations"] = filters.format_amount(
            sum(booking.total_amount for booking in bookings)
        )
        additional_data["Montant remboursé à l'acteur"] = filters.format_amount(
            -finance_utils.to_euros(
                sum(booking.reimbursement_pricing.amount for booking in bookings if booking.reimbursement_pricing)
            )
        )

    return additional_data


def _initialize_collective_booking_additional_data(collective_booking: educational_models.CollectiveBooking) -> dict:
    additional_data = {
        "ID de la réservation": collective_booking.id,
        "Statut de la réservation": filters.format_booking_status(collective_booking),
        "Nom de l'offre": collective_booking.collectiveStock.collectiveOffer.name,
        "Date de l'offre": filters.format_date_time(collective_booking.collectiveStock.beginningDatetime),
        "Établissement": collective_booking.educationalInstitution.name,
        "Nombre d'élèves": collective_booking.collectiveStock.numberOfTickets,
        "Montant de la réservation": filters.format_amount(collective_booking.total_amount),
    }

    if collective_booking.reimbursement_pricing:
        additional_data["Montant remboursé à l'acteur"] = filters.format_amount(
            -finance_utils.to_euros(collective_booking.reimbursement_pricing.amount)
        )

    return additional_data


@finance_incidents_blueprint.route("/<int:finance_incident_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def comment_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = finance_models.FinanceIncident.query.filter_by(id=finance_incident_id).one_or_none()
    if not incident:
        raise NotFound()

    form = offerer_forms.CommentForm()

    if not form.validate():
        flash("Le formulaire comporte des erreurs", "warning")
    else:
        history_api.add_action(
            history_models.ActionType.COMMENT,
            author=current_user,
            finance_incident=incident,
            comment=form.comment.data,
        )
        db.session.commit()
        flash("Le commentaire a été enregistré", "success")

    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=incident.id, active_tab="history")
    )


def _get_finance_overpayment_incident_validation_form(
    finance_incident: finance_models.FinanceIncident,
) -> utils.BackofficeResponse:
    incident_total_amount_euros = finance_utils.to_euros(finance_incident.due_amount_by_offerer)
    bank_account_link = finance_incident.venue.current_bank_account_link
    bank_account_details_str = "du lieu" if not bank_account_link else bank_account_link.bankAccount.label
    validation_url = "backoffice_web.finance_incidents.validate_finance_overpayment_incident"

    return render_template(
        "components/turbo/modal_form.html",
        form=forms.IncidentValidationForm(),
        dst=url_for(validation_url, finance_incident_id=finance_incident.id),
        div_id=f"finance-incident-validation-modal-{finance_incident.id}",
        title="Valider l'incident",
        button_text="Confirmer",
        information=Markup(
            "Vous allez valider un incident de {incident_amount} sur le compte bancaire {details}. "
            "Voulez-vous continuer ?"
        ).format(
            incident_amount=filters.format_amount(incident_total_amount_euros),
            details=bank_account_details_str,
        ),
    )


def _get_finance_commercial_gesture_validation_form(
    finance_incident: finance_models.FinanceIncident,
) -> utils.BackofficeResponse:
    commercial_gesture_amount = finance_utils.to_euros(finance_incident.commercial_gesture_amount)
    bank_account_link = finance_incident.venue.current_bank_account_link
    bank_account_details_str = "du lieu" if not bank_account_link else bank_account_link.bankAccount.label
    validation_url = "backoffice_web.finance_incidents.validate_finance_commercial_gesture"

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for(validation_url, finance_incident_id=finance_incident.id),
        div_id=f"finance-incident-validation-modal-{finance_incident.id}",
        title="Valider le geste commercial",
        button_text="Confirmer",
        information=Markup(
            "Vous allez valider un geste commercial de {commercial_gesture_amount} sur le compte bancaire {details}. "
            "Voulez-vous continuer ?"
        ).format(
            commercial_gesture_amount=filters.format_amount(commercial_gesture_amount),
            details=bank_account_details_str,
        ),
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_finance_incident_validation_form(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = _get_incident(finance_incident_id)
    if finance_incident.kind == finance_models.IncidentType.COMMERCIAL_GESTURE:
        return _get_finance_commercial_gesture_validation_form(finance_incident)

    return _get_finance_overpayment_incident_validation_form(finance_incident)


@finance_incidents_blueprint.route("/overpayment/<int:finance_incident_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def validate_finance_overpayment_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = _get_incident(finance_incident_id, kind=finance_models.IncidentType.OVERPAYMENT)
    form = forms.IncidentValidationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    elif finance_incident.status != finance_models.IncidentStatus.CREATED:
        flash("L'incident ne peut être validé que s'il est au statut 'créé'.", "warning")
    else:
        finance_api.validate_finance_overpayment_incident(
            finance_incident=finance_incident,
            force_debit_note=form.compensation_mode.data == forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name,
            author=current_user,
        )
        flash("L'incident a été validé.", "success")

    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident_id), 303
    )


@finance_incidents_blueprint.route("/commercial-gesture/<int:finance_incident_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_COMMERCIAL_GESTURE)
def validate_finance_commercial_gesture(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = _get_incident(finance_incident_id, kind=finance_models.IncidentType.COMMERCIAL_GESTURE)

    if finance_incident.status != finance_models.IncidentStatus.CREATED:
        flash("Le geste commercial ne peut être validé que s'il est au statut 'créé'.", "warning")
    else:
        finance_api.validate_finance_commercial_gesture(
            finance_incident=finance_incident,
            author=current_user,
        )
        flash("Le geste commercial a été validé.", "success")

    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/force-debit-note", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_finance_incident_force_debit_note_form(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = finance_models.FinanceIncident.query.filter_by(id=finance_incident_id).one_or_none()

    if not finance_incident:
        raise NotFound()

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_web.finance_incidents.force_debit_note", finance_incident_id=finance_incident_id),
        div_id=f"finance-incident-force-debit-note-modal-{finance_incident_id}",
        title="Générer une note de débit",
        button_text="Confirmer",
        information='Vous allez choisir le mode de compensation "Note de débit", une note de débit sera envoyée à l\'acteur culturel à la prochaine échéance. Voulez-vous continuer ?',
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/force-debit-note", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def force_debit_note(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = _get_incident(finance_incident_id)

    if finance_incident.status != finance_models.IncidentStatus.VALIDATED or finance_incident.isClosed:
        flash("Cette action ne peut être effectuée que sur un incident validé non terminé.", "warning")
        return redirect(
            url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
        )

    finance_incident.forceDebitNote = True
    db.session.add(finance_incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE,
        author=current_user,
        finance_incident=finance_incident,
        modified_info={
            "force_debit_note": {"old_info": False, "new_info": True},
        },
    )

    db.session.commit()

    flash("Une note de débit sera générée à la prochaine échéance.", "success")
    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/cancel-debit-note", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_finance_incident_cancel_debit_note_form(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = finance_models.FinanceIncident.query.filter_by(id=finance_incident_id).one_or_none()

    if not finance_incident:
        raise NotFound()

    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for("backoffice_web.finance_incidents.cancel_debit_note", finance_incident_id=finance_incident_id),
        div_id=f"finance-incident-cancel-debit-note-modal-{finance_incident_id}",
        title="Récupérer l'argent sur les prochaines réservations",
        button_text="Confirmer",
        information='Vous allez choisir le mode de compensation "Récupération sur les prochaines réservations", un mail sera envoyé à la suite de la confirmation. Voulez-vous continuer ?',
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/cancel-debit-note", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def cancel_debit_note(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = _get_incident(finance_incident_id)

    if finance_incident.status != finance_models.IncidentStatus.VALIDATED or finance_incident.isClosed:
        flash("Cette action ne peut être effectuée que sur un incident validé non terminé.", "warning")
        return redirect(
            url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
        )

    finance_incident.forceDebitNote = False
    db.session.add(finance_incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE,
        author=current_user,
        finance_incident=finance_incident,
        modified_info={
            "force_debit_note": {"old_info": True, "new_info": False},
        },
    )

    db.session.commit()

    send_finance_incident_emails(finance_incident)

    flash("Vous avez fait le choix de récupérer l'argent sur les prochaines réservations de l'acteur.", "success")
    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
    )


def _get_incident(finance_incident_id: int, **args: typing.Any) -> finance_models.FinanceIncident:
    incident = (
        finance_models.FinanceIncident.query.filter_by(id=finance_incident_id, **args)
        .join(finance_models.FinanceIncident.venue)
        .outerjoin(
            offerer_models.VenueBankAccountLink,
            sa.and_(
                offerer_models.Venue.id == offerer_models.VenueBankAccountLink.venueId,
                offerer_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .outerjoin(offerer_models.VenueBankAccountLink.bankAccount)
        .options(
            # Venue info
            sa.orm.joinedload(offerer_models.Venue, finance_models.FinanceIncident.venue)
            .load_only(offerer_models.Venue.id, offerer_models.Venue.name, offerer_models.Venue.publicName)
            .contains_eager(offerer_models.Venue.bankAccountLinks)
            .load_only(offerer_models.VenueBankAccountLink.timespan)
            .contains_eager(offerer_models.VenueBankAccountLink.bankAccount)
            .load_only(finance_models.BankAccount.id, finance_models.BankAccount.label),
            # Booking incidents info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            ).load_only(
                finance_models.BookingFinanceIncident.id,
                finance_models.BookingFinanceIncident.newTotalAmount,
                finance_models.BookingFinanceIncident.beneficiaryId,
                finance_models.BookingFinanceIncident.bookingId,
                finance_models.BookingFinanceIncident.collectiveBookingId,
                finance_models.BookingFinanceIncident.incidentId,
            )
            # Bookings info
            .joinedload(finance_models.BookingFinanceIncident.booking).load_only(
                bookings_models.Booking.id,
                bookings_models.Booking.quantity,
                bookings_models.Booking.amount,
                bookings_models.Booking.cancellationDate,
                bookings_models.Booking.cancellationReason,
                bookings_models.Booking.dateCreated,
                bookings_models.Booking.dateUsed,
                bookings_models.Booking.status,
                bookings_models.Booking.token,
            )
            # Booking venue info
            .joinedload(bookings_models.Booking.venue).load_only(offerer_models.Venue.bookingEmail),
            # booking user info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.booking)
            .joinedload(bookings_models.Booking.user)
            .load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.email,
            ),
            # booking deposit info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.booking)
            .joinedload(bookings_models.Booking.deposit)
            .load_only(finance_models.Deposit.type),
            # booking pricing info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.booking)
            .joinedload(bookings_models.Booking.pricings)
            .load_only(
                finance_models.Pricing.amount,
                finance_models.Pricing.status,
                finance_models.Pricing.creationDate,
            ),
            # booking stock info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.booking)
            .joinedload(bookings_models.Booking.stock)
            .load_only(
                offers_models.Stock.beginningDatetime,
                offers_models.Stock.price,
            )
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.url,
                offers_models.Offer.subcategoryId,
            ),
            # collective booking info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.collectiveBooking)
            .load_only(
                educational_models.CollectiveBooking.id,
                educational_models.CollectiveBooking.status,
                educational_models.CollectiveBooking.dateCreated,
                educational_models.CollectiveBooking.dateUsed,
                educational_models.CollectiveBooking.cancellationDate,
                educational_models.CollectiveBooking.cancellationReason,
            )
            # collective booking educational redactor info
            .joinedload(educational_models.CollectiveBooking.educationalRedactor).load_only(
                educational_models.EducationalRedactor.firstName, educational_models.EducationalRedactor.lastName
            ),
            # collective booking education institution info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.collectiveBooking)
            .joinedload(educational_models.CollectiveBooking.educationalInstitution)
            .load_only(educational_models.EducationalInstitution.name),
            # collective booking offer info
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.collectiveBooking)
            .joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(educational_models.CollectiveStock.beginningDatetime, educational_models.CollectiveStock.price)
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.name,
                educational_models.CollectiveOffer.subcategoryId,
                educational_models.CollectiveOffer.formats,
            ),
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.collectiveBooking)
            .joinedload(educational_models.CollectiveBooking.pricings)
            .load_only(
                finance_models.Pricing.amount,
            ),
        )
        .one_or_none()
    )

    if not incident:
        raise NotFound()

    return incident
