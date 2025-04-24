from collections import defaultdict
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
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.external_bookings.exceptions import ExternalBookingException
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.finance_incidents.finance_incident_notification import send_finance_incident_emails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers.exceptions import ProviderException
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.filters import pluralize
from pcapi.routes.backoffice.finance import forms
from pcapi.routes.backoffice.finance import validation
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils import date as date_utils
from pcapi.utils import string as string_utils
from pcapi.utils import urls


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
    ids_query = sa.select(finance_models.FinanceIncident.id)

    if form.incident_type.data and len(form.incident_type.data) == 1:
        ids_query = ids_query.filter(
            finance_models.FinanceIncident.kind == finance_models.IncidentType[form.incident_type.data[0]]
        )

    if form.is_collective.data or form.q.data:
        ids_query = ids_query.outerjoin(finance_models.FinanceIncident.booking_finance_incidents).outerjoin(
            finance_models.BookingFinanceIncident.collectiveBooking
        )

        if form.is_collective.data and len(form.is_collective.data) == 1:
            if form.is_collective.data[0] == "true":
                ids_query = ids_query.filter(finance_models.FinanceIncident.relates_to_collective_bookings)
            else:
                ids_query = ids_query.filter(sa.not_(finance_models.FinanceIncident.relates_to_collective_bookings))

    if form.status.data:
        # When filtering on status, always exclude closed incidents
        ids_query = ids_query.filter(
            finance_models.FinanceIncident.status.in_(form.status.data),
            sa.not_(finance_models.FinanceIncident.isClosed),
        )

    if form.origin.data:
        ids_query = ids_query.filter(
            finance_models.FinanceIncident.origin.in_(
                [finance_models.FinanceIncidentRequestOrigin[origin] for origin in form.origin.data]
            )
        )

    if form.offerer.data or form.venue.data:
        ids_query = ids_query.join(finance_models.FinanceIncident.venue)

        if form.offerer.data:
            ids_query = ids_query.filter(offerers_models.Venue.managingOffererId.in_(form.offerer.data))

        if form.venue.data:
            ids_query = ids_query.filter(offerers_models.Venue.id.in_(form.venue.data))

    if form.from_date.data or form.to_date.data:
        ids_query = ids_query.join(
            history_models.ActionHistory,
            sa.and_(
                history_models.ActionHistory.financeIncidentId == finance_models.FinanceIncident.id,
                history_models.ActionHistory.actionType == history_models.ActionType.FINANCE_INCIDENT_CREATED,
            ),
        )

        if form.from_date.data:
            from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.min.time())
            ids_query = ids_query.filter(history_models.ActionHistory.actionDate >= from_datetime)

        if form.to_date.data:
            to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.max.time())
            ids_query = ids_query.filter(history_models.ActionHistory.actionDate <= to_datetime)

    if form.q.data:
        ids_query = (
            ids_query.outerjoin(finance_models.BookingFinanceIncident.booking)
            .outerjoin(bookings_models.Booking.stock)
            .outerjoin(educational_models.CollectiveBooking.collectiveStock)
        )

        search_query = form.q.data
        or_filters = []

        if string_utils.is_numeric(search_query):
            integer_query = int(search_query)
            or_filters.extend(
                [
                    finance_models.FinanceIncident.id == integer_query,
                    bookings_models.Booking.id == integer_query,
                    offers_models.Stock.offerId == integer_query,
                    educational_models.CollectiveBooking.id == integer_query,
                    educational_models.CollectiveStock.collectiveOfferId == integer_query,
                    finance_models.FinanceIncident.zendeskId == integer_query,
                ]
            )

        if len(search_query) == TOKEN_LENGTH:
            or_filters.append(bookings_models.Booking.token == search_query)

        if or_filters:
            ids_query = ids_query.filter(sa.or_(*or_filters))
        else:
            flash("Le format de la recherche ne correspond ni à un ID ni à une contremarque", "info")
            ids_query = ids_query.filter(sa.false)

        ids_query = ids_query.distinct().order_by(sa.desc(finance_models.FinanceIncident.id)).limit(form.limit.data + 1)

    incidents_query = (
        db.session.query(finance_models.FinanceIncident)
        .filter(finance_models.FinanceIncident.id.in_(ids_query))
        .options(
            sa_orm.joinedload(finance_models.FinanceIncident.venue)
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
                offerers_models.Offerer.postalCode,
            ),
            sa_orm.joinedload(finance_models.FinanceIncident.booking_finance_incidents).options(
                sa_orm.load_only(
                    finance_models.BookingFinanceIncident.id,
                    finance_models.BookingFinanceIncident.newTotalAmount,
                ),
                sa_orm.joinedload(finance_models.BookingFinanceIncident.booking).load_only(
                    bookings_models.Booking.amount, bookings_models.Booking.quantity
                ),
                sa_orm.joinedload(finance_models.BookingFinanceIncident.collectiveBooking)
                .load_only(educational_models.CollectiveBooking.id)
                .joinedload(educational_models.CollectiveBooking.collectiveStock)
                .load_only(educational_models.CollectiveStock.price),
                sa_orm.joinedload(
                    finance_models.BookingFinanceIncident.finance_events
                ).load_only(  # because of: isClosed
                    finance_models.FinanceEvent.id
                ),
            ),
        )
        .order_by(sa.desc(finance_models.FinanceIncident.id))
    )

    incidents = incidents_query.all()
    return utils.limit_rows(incidents, form.limit.data)


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
    form = forms.CommentForm()
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
    incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()
    if not incident:
        raise NotFound()

    form = forms.CommentForm()
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
        mark_transaction_as_invalid()
        flash("L'incident a déjà été annulé", "warning")
    except finance_exceptions.FinanceIncidentAlreadyValidated:
        mark_transaction_as_invalid()
        flash("Impossible d'annuler un incident déjà validé", "warning")
    else:
        flash("L'incident a été annulé", "success")

    return redirect(url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=incident.id), 303)


@finance_incidents_blueprint.route("/<int:finance_incident_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()
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
    connect_as = {}
    for booking in bookings:
        if isinstance(booking, bookings_models.Booking):
            offer = booking.stock.offer
            connect_as[booking.id] = get_connect_as(
                object_type="offer",
                object_id=offer.id,
                pc_pro_path=urls.build_pc_pro_offer_path(offer),
            )
        else:
            offer = booking.collectiveStock.collectiveOffer
            connect_as[booking.id] = get_connect_as(
                object_type="collective_offer",
                object_id=offer.id,
                pc_pro_path=urls.build_pc_pro_offer_path(offer),
            )

    bookings_total_amount = sum(booking.total_amount for booking in bookings)
    reimbursement_pricings = [booking.reimbursement_pricing for booking in bookings if booking.reimbursement_pricing]
    initial_reimbursement_amount = sum(pricing.amount for pricing in reimbursement_pricings) * -1

    return render_template(
        "finance/incidents/get_overpayment.html",
        incident=incident,
        connect_as=connect_as,
        active_tab=request.args.get("active_tab", "bookings"),
        bookings_total_amount=bookings_total_amount,
        initial_reimbursement_amount=initial_reimbursement_amount,
    )


@finance_incidents_blueprint.route("/commercial-gesture/<int:finance_incident_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_commercial_gesture(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = _get_incident(finance_incident_id, kind=finance_models.IncidentType.COMMERCIAL_GESTURE)
    bookings = [
        (booking_incident.booking or booking_incident.collectiveBooking)
        for booking_incident in incident.booking_finance_incidents
    ]
    connect_as = {}
    for booking in bookings:
        if isinstance(booking, bookings_models.Booking):
            offer = booking.stock.offer
            connect_as[offer.id] = get_connect_as(
                object_type="offer",
                object_id=offer.id,
                pc_pro_path=urls.build_pc_pro_offer_path(offer),
            )
        else:
            offer = booking.collectiveStock.collectiveOffer
            connect_as[offer.id] = get_connect_as(
                object_type="collective_offer",
                object_id=offer.id,
                pc_pro_path=urls.build_pc_pro_offer_path(offer),
            )
    bookings_total_amount = sum(booking.total_amount for booking in bookings)

    return render_template(
        "finance/incidents/get_commercial_gesture.html",
        incident=incident,
        connect_as=connect_as,
        commercial_gesture_amount=incident.due_amount_by_offerer,
        bookings_total_amount=bookings_total_amount,
        active_tab=request.args.get("active_tab", "bookings"),
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/history", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_history(finance_incident_id: int) -> utils.BackofficeResponse:
    actions = (
        db.session.query(history_models.ActionHistory)
        .filter_by(financeIncidentId=finance_incident_id)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .options(
            sa_orm.joinedload(history_models.ActionHistory.user).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            sa_orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
        )
        .all()
    )

    return render_template(
        "finance/incidents/get/details/history.html",
        actions=actions,
        form=forms.CommentForm(),
        dst=url_for("backoffice_web.finance_incidents.comment_incident", finance_incident_id=finance_incident_id),
    )


@finance_incidents_blueprint.route("/individual-bookings/overpayment-creation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def get_individual_bookings_overpayment_creation_form() -> utils.BackofficeResponse:
    form = forms.BookingOverPaymentIncidentForm()
    additional_data = {}
    alert = None

    if form.object_ids.data:
        bookings = (
            db.session.query(bookings_models.Booking)
            .options(
                sa_orm.joinedload(bookings_models.Booking.user).load_only(
                    users_models.User.firstName, users_models.User.lastName, users_models.User.email
                ),
                sa_orm.joinedload(bookings_models.Booking.pricings).load_only(
                    finance_models.Pricing.status, finance_models.Pricing.amount, finance_models.Pricing.creationDate
                ),
                sa_orm.joinedload(bookings_models.Booking.stock)
                .load_only(offers_models.Stock.id)
                .joinedload(offers_models.Stock.offer)
                .load_only(offers_models.Offer.name),
                sa_orm.joinedload(bookings_models.Booking.venue)
                .load_only(offerers_models.Venue.publicName, offerers_models.Venue.name)
                .joinedload(offerers_models.Venue.managingOfferer)
                .load_only(offerers_models.Offerer.siren, offerers_models.Offerer.postalCode),
            )
            .filter(
                bookings_models.Booking.id.in_(form.object_ids_list),
                bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
            )
            .all()
        )

        if not (valid := validation.check_incident_bookings(bookings)):
            mark_transaction_as_invalid()
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
        additional_data=additional_data.items(),
        alert=alert,
    )


@finance_incidents_blueprint.route("/individual-bookings/commercial-gesture-creation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def get_individual_bookings_commercial_gesture_creation_form() -> utils.BackofficeResponse:
    form = forms.CommercialGestureCreationForm()
    additional_data = {}

    if form.object_ids.data:
        bookings = (
            db.session.query(bookings_models.Booking)
            .options(
                sa_orm.joinedload(bookings_models.Booking.user).load_only(
                    users_models.User.firstName, users_models.User.lastName, users_models.User.email
                ),
                sa_orm.joinedload(bookings_models.Booking.pricings).load_only(
                    finance_models.Pricing.status, finance_models.Pricing.amount, finance_models.Pricing.creationDate
                ),
                sa_orm.joinedload(bookings_models.Booking.stock)
                .load_only(offers_models.Stock.id)
                .joinedload(offers_models.Stock.offer)
                .load_only(offers_models.Offer.name),
                sa_orm.joinedload(bookings_models.Booking.venue)
                .load_only(offerers_models.Venue.publicName, offerers_models.Venue.name)
                .joinedload(offerers_models.Venue.managingOfferer)
                .load_only(offerers_models.Offerer.siren, offerers_models.Offerer.postalCode),
            )
            .filter(
                bookings_models.Booking.id.in_(form.object_ids_list),
                bookings_models.Booking.status == bookings_models.BookingStatus.CANCELLED,
            )
            .all()
        )

        if not (valid := validation.check_commercial_gesture_bookings(bookings)):
            mark_transaction_as_invalid()
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
        additional_data=additional_data.items(),
    )


@finance_incidents_blueprint.route(
    "/collective-bookings/<int:collective_booking_id>/overpayment-creation-form", methods=["GET", "POST"]
)
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def get_collective_booking_overpayment_creation_form(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking: educational_models.CollectiveBooking | None = (
        db.session.query(educational_models.CollectiveBooking)
        .filter_by(id=collective_booking_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.name
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.pricings).load_only(
                finance_models.Pricing.amount,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.startDatetime, educational_models.CollectiveStock.numberOfTickets
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
        mark_transaction_as_invalid()
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
        additional_data=additional_data.items(),
    )


@finance_incidents_blueprint.route(
    "/collective-bookings/<int:collective_booking_id>/commercial-gesture-creation-form",
    methods=["GET", "POST"],
)
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def get_collective_booking_commercial_gesture_creation_form(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking: educational_models.CollectiveBooking | None = (
        db.session.query(educational_models.CollectiveBooking)
        .filter_by(id=collective_booking_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.name
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.pricings).load_only(
                finance_models.Pricing.amount,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.startDatetime, educational_models.CollectiveStock.numberOfTickets
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
        mark_transaction_as_invalid()
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
        additional_data=additional_data.items(),
    )


@finance_incidents_blueprint.route("/individual-bookings/create-overpayment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def create_individual_booking_overpayment() -> utils.BackofficeResponse:
    form = forms.BookingOverPaymentIncidentForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer, 303)

    amount = form.total_amount.data

    bookings = (
        db.session.query(bookings_models.Booking)
        .options(
            sa_orm.joinedload(bookings_models.Booking.pricings).load_only(finance_models.Pricing.amount),
            sa_orm.joinedload(bookings_models.Booking.deposit).load_only(finance_models.Deposit.amount),
            sa_orm.joinedload(bookings_models.Booking.deposit)
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
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)

    incident = finance_api.create_overpayment_finance_incident(
        bookings=bookings,
        author=current_user,
        origin=finance_models.FinanceIncidentRequestOrigin[form.origin.data],
        zendesk_id=form.zendesk_id.data,
        comment=form.comment.data,
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
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def create_individual_booking_commercial_gesture() -> utils.BackofficeResponse:
    form = forms.CommercialGestureCreationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer, 303)

    amount = form.total_amount.data

    bookings = (
        db.session.query(bookings_models.Booking)
        .options(
            sa_orm.joinedload(bookings_models.Booking.pricings).load_only(finance_models.Pricing.amount),
            sa_orm.joinedload(bookings_models.Booking.deposit)
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
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 303)

    commercial_gesture = finance_api.create_finance_commercial_gesture(
        bookings=bookings,
        amount=amount,
        author=current_user,
        origin=finance_models.FinanceIncidentRequestOrigin[form.origin.data],
        zendesk_id=form.zendesk_id.data,
        comment=form.comment.data,
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
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def create_collective_booking_overpayment(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = (
        db.session.query(educational_models.CollectiveBooking).filter_by(id=collective_booking_id).one_or_none()
    )
    if not collective_booking:
        raise NotFound()

    redirect_url = request.referrer or url_for("backoffice_web.collective_bookings.list_collective_bookings")
    form = forms.CollectiveOverPaymentIncidentCreationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(redirect_url, 303)

    if not (valid := validation.check_incident_collective_booking(collective_booking)):
        for message in valid.messages:
            flash(message, "warning")
        mark_transaction_as_invalid()
        return redirect(redirect_url, 303)

    incident = finance_api.create_overpayment_finance_incident_collective_booking(
        collective_booking,
        author=current_user,
        origin=finance_models.FinanceIncidentRequestOrigin[form.origin.data],
        zendesk_id=form.zendesk_id.data,
        comment=form.comment.data,
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
@utils.permission_required(perm_models.Permissions.CREATE_INCIDENTS)
def create_collective_booking_commercial_gesture(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = (
        db.session.query(educational_models.CollectiveBooking).filter_by(id=collective_booking_id).one_or_none()
    )
    if not collective_booking:
        raise NotFound()

    redirect_url = request.referrer or url_for("backoffice_web.collective_bookings.list_collective_bookings")
    form = forms.CollectiveCommercialGestureCreationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(redirect_url, 303)

    if not (valid := validation.check_commercial_gesture_collective_booking(collective_booking)):
        for message in valid.messages:
            flash(message, "warning")
        mark_transaction_as_invalid()
        return redirect(redirect_url, 303)

    incident = finance_api.create_finance_commercial_gesture_collective_booking(
        collective_booking,
        author=current_user,
        origin=finance_models.FinanceIncidentRequestOrigin[form.origin.data],
        zendesk_id=form.zendesk_id.data,
        comment=form.comment.data,
    )
    incident_url = url_for(
        "backoffice_web.finance_incidents.get_incident",
        finance_incident_id=incident.id,
    )

    flash(Markup('Un nouveau <a href="{url}">geste commercial</a> a été créé.').format(url=incident_url), "success")
    return redirect(redirect_url, 303)


def _initialize_additional_data(bookings: list[bookings_models.Booking]) -> dict:
    additional_data: dict[str, typing.Any] = {}

    additional_data["Partenaire culturel"] = bookings[0].venue.common_name

    if len(bookings) == 1:
        booking = bookings[0]

        additional_data["ID de la réservation"] = booking.id
        additional_data["Statut de la réservation"] = filters.format_booking_status(booking)
        additional_data["Contremarque"] = booking.token
        additional_data["Nom de l'offre"] = booking.stock.offer.name
        additional_data["Bénéficiaire"] = booking.user.full_name
        additional_data["Montant de la réservation"] = filters.format_amount(booking.total_amount, target=booking.venue)
        additional_data["Montant remboursé à l'acteur"] = filters.format_amount(
            (
                -finance_utils.cents_to_full_unit(booking.reimbursement_pricing.amount)
                if booking.reimbursement_pricing
                else 0
            ),
            target=booking.venue,
        )
    else:
        additional_data["Nombre de réservations"] = len(bookings)
        additional_data["Montant des réservations"] = filters.format_amount(
            sum(booking.total_amount for booking in bookings)
        )
        additional_data["Montant remboursé à l'acteur"] = filters.format_amount(
            -finance_utils.cents_to_full_unit(
                sum(booking.reimbursement_pricing.amount for booking in bookings if booking.reimbursement_pricing)
            )
        )

    return additional_data


def _initialize_collective_booking_additional_data(collective_booking: educational_models.CollectiveBooking) -> dict:
    additional_data = {
        "ID de la réservation": collective_booking.id,
        "Statut de la réservation": filters.format_booking_status(collective_booking),
        "Nom de l'offre": collective_booking.collectiveStock.collectiveOffer.name,
        "Date de l'offre": filters.format_date_time(collective_booking.collectiveStock.startDatetime),
        "Établissement": collective_booking.educationalInstitution.name,
        "Nombre d'élèves": collective_booking.collectiveStock.numberOfTickets,
        "Montant de la réservation": filters.format_amount(collective_booking.total_amount),
    }

    if collective_booking.reimbursement_pricing:
        additional_data["Montant remboursé à l'acteur"] = filters.format_amount(
            -finance_utils.cents_to_full_unit(collective_booking.reimbursement_pricing.amount)
        )

    return additional_data


@finance_incidents_blueprint.route("/<int:finance_incident_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def comment_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()
    if not incident:
        raise NotFound()

    form = forms.CommentForm()

    if not form.validate():
        flash("Le formulaire comporte des erreurs", "warning")
        mark_transaction_as_invalid()
    else:
        history_api.add_action(
            history_models.ActionType.COMMENT,
            author=current_user,
            finance_incident=incident,
            comment=form.comment.data,
        )
        db.session.flush()
        flash("Le commentaire a été enregistré", "success")

    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=incident.id, active_tab="history")
    )


def _get_finance_overpayment_incident_validation_form(
    finance_incident: finance_models.FinanceIncident,
) -> utils.BackofficeResponse:
    incident_total_amount_euros = finance_utils.cents_to_full_unit(finance_incident.due_amount_by_offerer)
    bank_account_link = finance_incident.venue.current_bank_account_link
    bank_account_details_str = (
        "du partenaire culturel" if not bank_account_link else bank_account_link.bankAccount.label
    )
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
            incident_amount=filters.format_amount(incident_total_amount_euros, target=finance_incident.venue),
            details=bank_account_details_str,
        ),
    )


def _get_finance_commercial_gesture_validation_form(
    finance_incident: finance_models.FinanceIncident,
) -> utils.BackofficeResponse:
    commercial_gesture_amount = finance_utils.cents_to_full_unit(finance_incident.due_amount_by_offerer)
    bank_account_link = finance_incident.venue.current_bank_account_link
    bank_account_details_str = (
        "du partenaire culturel" if not bank_account_link else bank_account_link.bankAccount.label
    )
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
            commercial_gesture_amount=filters.format_amount(commercial_gesture_amount, target=finance_incident.venue),
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


@finance_incidents_blueprint.route("/batch-validation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_batch_finance_incidents_validation_form() -> utils.BackofficeResponse:
    form = forms.BatchIncidentValidationForm()
    incidents_type = None

    if form.object_ids.data:
        finance_incidents = (
            db.session.query(finance_models.FinanceIncident)
            .filter(
                finance_models.FinanceIncident.id.in_(form.object_ids_list),
            )
            .all()
        )

        if not (
            valid := validation.check_validate_or_cancel_finance_incidents(finance_incidents, is_validation_action=True)
        ):
            mark_transaction_as_invalid()
            return render_template(
                "components/turbo/modal_empty_form.html",
                form=empty_forms.BatchForm(),
                messages=valid.messages,
            )

        incidents_type = finance_incidents[0].kind
        if incidents_type == finance_models.IncidentType.COMMERCIAL_GESTURE:
            form = empty_forms.BatchForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.finance_incidents.batch_validate_finance_incidents"),
        div_id="batch-validate-modal",
        title=Markup("Voulez-vous valider les {kind} sélectionnés ?").format(
            kind="trop perçus" if incidents_type == finance_models.IncidentType.OVERPAYMENT else "gestes commerciaux"
        ),
        button_text="Valider",
        information=Markup("Vous allez valider {number_of_incidents} incident(s). Voulez vous continuer ?").format(
            number_of_incidents=len(form.object_ids_list),
        ),
    )


@finance_incidents_blueprint.route("/batch-validation", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def batch_validate_finance_incidents() -> utils.BackofficeResponse:
    form = forms.BatchIncidentValidationForm()

    finance_incidents = (
        db.session.query(finance_models.FinanceIncident)
        .filter(finance_models.FinanceIncident.id.in_(form.object_ids_list))
        .all()
    )

    if finance_incidents[0].kind == finance_models.IncidentType.COMMERCIAL_GESTURE:
        form = empty_forms.BatchForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for("backoffice_web.finance_incidents.list_finance_incidents"), 303)

    error_dict = defaultdict(list)
    success_count = 0
    if finance_incidents[0].kind == finance_models.IncidentType.OVERPAYMENT:
        for incident in finance_incidents:
            with atomic():
                try:
                    finance_api.validate_finance_overpayment_incident(
                        incident,
                        force_debit_note=(
                            form.compensation_mode.data == forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name
                        ),
                        author=current_user,
                    )
                    success_count += 1
                except (ExternalBookingException, ProviderException) as err:
                    error_dict[str(err) or err.__class__.__name__].append(incident.id)
                    mark_transaction_as_invalid()

    elif finance_incidents[0].kind == finance_models.IncidentType.COMMERCIAL_GESTURE:
        for incident in finance_incidents:
            with atomic():
                try:
                    finance_api.validate_finance_commercial_gesture(
                        incident,
                        author=current_user,
                    )
                    success_count += 1
                except (ExternalBookingException, ProviderException) as err:
                    error_dict[str(err) or err.__class__.__name__].append(incident.id)
                    mark_transaction_as_invalid()

    _flash_success_and_error_messages(success_count, error_dict, True)
    return redirect(request.referrer or url_for("backoffice_web.finance_incidents.list_finance_incidents"), 303)


@finance_incidents_blueprint.route("/batch-cancellation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_batch_finance_incidents_cancellation_form() -> utils.BackofficeResponse:
    form = forms.BatchIncidentCancellationForm()
    incidents_type = None

    if form.object_ids.data:
        finance_incidents = (
            db.session.query(finance_models.FinanceIncident)
            .filter(
                finance_models.FinanceIncident.id.in_(form.object_ids_list),
            )
            .all()
        )
        incidents_type = finance_incidents[0].kind

        if not (
            valid := validation.check_validate_or_cancel_finance_incidents(
                finance_incidents, is_validation_action=False
            )
        ):
            mark_transaction_as_invalid()
            return render_template(
                "components/turbo/modal_empty_form.html",
                form=empty_forms.BatchForm(),
                messages=valid.messages,
            )

    return render_template(
        "components/turbo/modal_form.html",
        form=forms.BatchIncidentCancellationForm(),
        dst=url_for("backoffice_web.finance_incidents.batch_cancel_finance_incidents"),
        div_id="batch-reject-modal",
        title=Markup("Voulez-vous annuler les {kind} sélectionnés ?").format(
            kind="trop perçus" if incidents_type == finance_models.IncidentType.OVERPAYMENT else "gestes commerciaux"
        ),
        button_text="Confirmer l'annulation",
        information=Markup("Vous allez annuler {number_of_incidents} incident(s). Voulez vous continuer ?").format(
            number_of_incidents=len(form.object_ids_list),
        ),
    )


@finance_incidents_blueprint.route("/batch-cancellation", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def batch_cancel_finance_incidents() -> utils.BackofficeResponse:
    form = forms.BatchIncidentCancellationForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        mark_transaction_as_invalid()
        return redirect(request.referrer or url_for("backoffice_web.finance_incidents.list_finance_incidents"), 303)

    finance_incidents = (
        db.session.query(finance_models.FinanceIncident)
        .filter(
            finance_models.FinanceIncident.id.in_(form.object_ids_list),
        )
        .all()
    )

    success_count = 0
    error_dict = defaultdict(list)
    for incident in finance_incidents:
        with atomic():
            try:
                finance_api.cancel_finance_incident(
                    incident,
                    comment=form.comment.data,
                    author=current_user,
                )
                success_count += 1
            except (
                finance_exceptions.FinanceIncidentAlreadyCancelled,
                finance_exceptions.FinanceIncidentAlreadyValidated,
            ) as err:
                error_dict[err.__class__.__name__].append(incident.id)
                mark_transaction_as_invalid()

    _flash_success_and_error_messages(success_count, error_dict, is_validating=False)
    return redirect(request.referrer or url_for("backoffice_web.finance_incidents.list_finance_incidents"), 303)


def _build_incident_error_str(incident_ids: list[str], message: str) -> str:
    return Markup("- {count} {message} pour {incident} ({incident_ids})").format(
        count=len(incident_ids),
        message=message,
        incident=pluralize(len(incident_ids), "l'incident", "les incidents"),
        incident_ids=",".join(incident_ids),
    )


def _flash_success_and_error_messages(
    success_count: int, error_dict: dict[str, list[int]], is_validating: bool
) -> None:
    if success_count > 0:
        flash(
            f"{success_count} {pluralize(success_count, 'incident a', 'incidents ont')} été {'validé' if is_validating else 'annulé'}{pluralize(success_count)}",
            "success",
        )

    if error_dict:
        if success_count > 0:
            error_text = Markup("Certains incidents n'ont pas pu être {action} et ont été ignorés :<br> ").format(
                action="validés" if is_validating else "annulés"
            )
        else:
            error_text = Markup("Impossible {action} ces incidents : <br>").format(
                action="de valider" if is_validating else "d'annuler"
            )
        for key in error_dict:
            incident_ids = [str(incident_id) for incident_id in error_dict[key]]
            match key:
                case "FinanceIncidentAlreadyCancelled":
                    error_text += _build_incident_error_str(
                        incident_ids,
                        f"incident{pluralize(len(incident_ids))} déjà annulé{pluralize(len(incident_ids))}",
                    )
                case "FinanceIncidentAlreadyValidated":
                    error_text += _build_incident_error_str(
                        incident_ids,
                        f"incident{pluralize(len(incident_ids))} déjà validé{pluralize(len(incident_ids))}",
                    )
                case _:
                    error_text += _build_incident_error_str(
                        incident_ids,
                        f"""erreur{pluralize(len(incident_ids))} {pluralize(len(incident_ids), "s'est produite", "se sont produites")} : "{key}" """,
                    )
        flash(error_text, "warning")


@finance_incidents_blueprint.route("/overpayment/<int:finance_incident_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def validate_finance_overpayment_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = (
        db.session.query(finance_models.FinanceIncident)
        .filter_by(
            id=finance_incident_id,
            kind=finance_models.IncidentType.OVERPAYMENT,
        )
        .one_or_none()
    )
    if not finance_incident:
        raise NotFound()
    form = forms.IncidentValidationForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    elif finance_incident.status != finance_models.IncidentStatus.CREATED:
        flash("L'incident ne peut être validé que s'il est au statut 'créé'.", "warning")
    else:
        try:
            finance_api.validate_finance_overpayment_incident(
                finance_incident=finance_incident,
                force_debit_note=form.compensation_mode.data == forms.IncidentCompensationModes.FORCE_DEBIT_NOTE.name,
                author=current_user,
            )
        except (ExternalBookingException, ProviderException) as err:
            mark_transaction_as_invalid()
            flash(
                Markup("Une erreur s'est produite : {message}").format(message=str(err) or err.__class__.__name__),
                "warning",
            )
        else:
            flash("L'incident a été validé.", "success")

    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident_id), 303
    )


@finance_incidents_blueprint.route("/commercial-gesture/<int:finance_incident_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.VALIDATE_COMMERCIAL_GESTURE)
def validate_finance_commercial_gesture(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = (
        db.session.query(finance_models.FinanceIncident)
        .filter_by(
            id=finance_incident_id,
            kind=finance_models.IncidentType.COMMERCIAL_GESTURE,
        )
        .one_or_none()
    )
    if not finance_incident:
        raise NotFound()

    if finance_incident.status != finance_models.IncidentStatus.CREATED:
        mark_transaction_as_invalid()
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
    finance_incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()

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
    finance_incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()

    if not finance_incident:
        raise NotFound()

    if finance_incident.status != finance_models.IncidentStatus.VALIDATED or finance_incident.isClosed:
        flash("Cette action ne peut être effectuée que sur un incident validé non terminé.", "warning")
        mark_transaction_as_invalid()
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

    db.session.flush()

    flash("Une note de débit sera générée à la prochaine échéance.", "success")
    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
    )


@finance_incidents_blueprint.route("/<int:finance_incident_id>/cancel-debit-note", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_finance_incident_cancel_debit_note_form(finance_incident_id: int) -> utils.BackofficeResponse:
    finance_incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()

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
    finance_incident = db.session.query(finance_models.FinanceIncident).filter_by(id=finance_incident_id).one_or_none()

    if not finance_incident:
        raise NotFound()

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

    db.session.flush()

    send_finance_incident_emails(finance_incident=finance_incident)

    flash("Vous avez fait le choix de récupérer l'argent sur les prochaines réservations de l'acteur.", "success")
    return redirect(
        url_for("backoffice_web.finance_incidents.get_incident", finance_incident_id=finance_incident.id), 303
    )


def _get_incident(finance_incident_id: int, **args: typing.Any) -> finance_models.FinanceIncident:
    incident = (
        db.session.query(finance_models.FinanceIncident)
        .filter_by(id=finance_incident_id, **args)
        .join(finance_models.FinanceIncident.venue)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                offerers_models.Venue.id == offerers_models.VenueBankAccountLink.venueId,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            ),
        )
        .outerjoin(offerers_models.VenueBankAccountLink.bankAccount)
        .options(
            # Venue info
            sa_orm.contains_eager(finance_models.FinanceIncident.venue)
            .load_only(offerers_models.Venue.id, offerers_models.Venue.name, offerers_models.Venue.publicName)
            .options(
                sa_orm.contains_eager(offerers_models.Venue.bankAccountLinks)
                .load_only(offerers_models.VenueBankAccountLink.timespan)
                .contains_eager(offerers_models.VenueBankAccountLink.bankAccount)
                .load_only(finance_models.BankAccount.id, finance_models.BankAccount.label),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).load_only(
                    offerers_models.Offerer.siren, offerers_models.Offerer.postalCode
                ),
            ),
            # Booking incidents info
            sa_orm.joinedload(finance_models.FinanceIncident.booking_finance_incidents)
            .load_only(
                finance_models.BookingFinanceIncident.id,
                finance_models.BookingFinanceIncident.newTotalAmount,
                finance_models.BookingFinanceIncident.beneficiaryId,
                finance_models.BookingFinanceIncident.bookingId,
                finance_models.BookingFinanceIncident.collectiveBookingId,
                finance_models.BookingFinanceIncident.incidentId,
            )
            .options(
                # Bookings info
                sa_orm.joinedload(finance_models.BookingFinanceIncident.booking)
                .load_only(
                    bookings_models.Booking.id,
                    bookings_models.Booking.quantity,
                    bookings_models.Booking.amount,
                    bookings_models.Booking.cancellationDate,
                    bookings_models.Booking.cancellationReason,
                    bookings_models.Booking.dateCreated,
                    bookings_models.Booking.dateUsed,
                    bookings_models.Booking.status,
                    bookings_models.Booking.token,
                    bookings_models.Booking.usedRecreditType,
                )
                .options(
                    # Booking venue info
                    sa_orm.joinedload(bookings_models.Booking.venue).load_only(offerers_models.Venue.bookingEmail),
                    # Booking user info
                    sa_orm.joinedload(bookings_models.Booking.user).load_only(
                        users_models.User.id,
                        users_models.User.firstName,
                        users_models.User.lastName,
                        users_models.User.email,
                    ),
                    # Booking deposit info
                    sa_orm.joinedload(bookings_models.Booking.deposit).load_only(finance_models.Deposit.type),
                    # Booking pricing info
                    sa_orm.joinedload(bookings_models.Booking.pricings).load_only(
                        finance_models.Pricing.amount,
                        finance_models.Pricing.status,
                        finance_models.Pricing.creationDate,
                    ),
                    # booking stock info
                    sa_orm.joinedload(bookings_models.Booking.stock)
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
                ),
                # Batch infos
                sa_orm.joinedload(finance_models.BookingFinanceIncident.finance_events)
                .load_only(finance_models.FinanceEvent.id)
                .joinedload(finance_models.FinanceEvent.pricings)
                .load_only(finance_models.Pricing.id, finance_models.Pricing.amount, finance_models.Pricing.status)
                .joinedload(finance_models.Pricing.cashflows)
                .load_only(finance_models.Cashflow.id)
                .options(
                    # Cashflow batch label
                    sa_orm.joinedload(finance_models.Cashflow.batch).load_only(finance_models.CashflowBatch.label),
                    # Invoice url
                    sa_orm.joinedload(finance_models.Cashflow.invoices).load_only(
                        finance_models.Invoice.token,
                        finance_models.Invoice.date,
                        finance_models.Invoice.reference,
                    ),
                ),
                # collective booking info
                sa_orm.joinedload(finance_models.BookingFinanceIncident.collectiveBooking)
                .load_only(
                    educational_models.CollectiveBooking.id,
                    educational_models.CollectiveBooking.status,
                    educational_models.CollectiveBooking.dateCreated,
                    educational_models.CollectiveBooking.dateUsed,
                    educational_models.CollectiveBooking.cancellationDate,
                    educational_models.CollectiveBooking.cancellationReason,
                )
                .options(
                    # collective booking educational redactor info
                    sa_orm.joinedload(educational_models.CollectiveBooking.educationalRedactor).load_only(
                        educational_models.EducationalRedactor.firstName,
                        educational_models.EducationalRedactor.lastName,
                    ),
                    # collective booking education institution info
                    sa_orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                        educational_models.EducationalInstitution.name
                    ),
                    # collective booking offer info
                    sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
                    .load_only(
                        educational_models.CollectiveStock.startDatetime, educational_models.CollectiveStock.price
                    )
                    .joinedload(educational_models.CollectiveStock.collectiveOffer)
                    .load_only(
                        educational_models.CollectiveOffer.id,
                        educational_models.CollectiveOffer.name,
                        educational_models.CollectiveOffer.formats,
                    ),
                    sa_orm.joinedload(educational_models.CollectiveBooking.pricings).load_only(
                        finance_models.Pricing.amount,
                    ),
                ),
            ),
        )
        .one_or_none()
    )

    if not incident:
        raise NotFound()

    return incident
