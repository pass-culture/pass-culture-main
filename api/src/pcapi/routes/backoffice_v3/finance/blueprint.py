from datetime import datetime

from flask import Response
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa

from pcapi.core.bookings import models as bookings_models
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerer_models
from pcapi.core.offers import models as offers_models
import pcapi.core.permissions.models as perm_models
from pcapi.models import db
from pcapi.repository import repository
from pcapi.routes.backoffice_v3 import utils
from pcapi.routes.backoffice_v3.finance import forms


finance_incident_blueprint = utils.child_backoffice_blueprint(
    "finance_incident",
    __name__,
    url_prefix="/finance",
    permission=perm_models.Permissions.READ_INCIDENTS,
)


def _get_incidents() -> list[finance_models.FinanceIncident]:
    # TODO (akarki): implement the search and filters for the incidents page
    query = finance_models.FinanceIncident.query.options(
        sa.orm.joinedload(
            finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
        ).load_only(
            finance_models.BookingFinanceIncident.id,
            finance_models.BookingFinanceIncident.newTotalAmount,
        ),
        sa.orm.joinedload(offerer_models.Venue, finance_models.FinanceIncident.venue)
        .load_only(offerer_models.Venue.id, offerer_models.Venue.name)
        .joinedload(offerer_models.Venue.managingOfferer)
        .load_only(offerer_models.Offerer.id, offerer_models.Offerer.name),
        sa.orm.joinedload(offerer_models.Venue, finance_models.FinanceIncident.venue).joinedload(
            offerer_models.Venue.reimbursement_point_links
        ),
    )
    return query.order_by(finance_models.FinanceIncident.id).all()


@finance_incident_blueprint.route("/incidents", methods=["GET"])
def list_incidents() -> utils.BackofficeResponse:
    incidents = _get_incidents()
    return render_template("finance/incident/list.html", rows=incidents)


@finance_incident_blueprint.route("get-incident-creation-form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_incident_creation_form() -> utils.BackofficeResponse:
    form = forms.BookingIncidentForm(kind=finance_models.IncidentType.OVERPAYMENT.name)
    additional_data = {}
    # TODO (cmorel): make this field dynamically disabled/required if other incident type is selected
    # + if other type is selected, make total_amount required
    form.total_amount.flags.disabled = True

    if form.object_ids.data:
        bookings = (
            bookings_models.Booking.query.options(
                sa.orm.joinedload(bookings_models.Booking.user),
                sa.orm.joinedload(bookings_models.Booking.pricings).load_only(finance_models.Pricing.amount),
                sa.orm.joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer),
                sa.orm.joinedload(bookings_models.Booking.venue),
            )
            .filter(
                sa.and_(
                    bookings_models.Booking.id.in_(form.object_ids_list),
                    bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
                )
            )
            .all()
        )

        if not bookings or len({booking.venueId for booking in bookings}) > 1:
            return Response(
                """<div class="alert alert-info m-0">Seules les réservations ayant le statut 'remboursée' et 
                correspondant au même lieu peuvent faire l'objet d'un incident</div>"""
            )

        form.total_amount.data = (
            bookings[0].amount if len(bookings) == 1 else sum(booking.amount for booking in bookings)
        )

        additional_data = _initialize_additional_data(bookings)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.finance_incident.create_incident"),
        div_id="incident-creation-modal",
        title="Création d'un incident",
        button_text="Créer l'incident",
        additional_data=additional_data,
    )


@finance_incident_blueprint.route("/create-incident", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def create_incident() -> utils.BackofficeResponse:
    form = forms.BookingIncidentForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 301)

    bookings = (
        bookings_models.Booking.query.options(
            sa.orm.joinedload(bookings_models.Booking.pricings).load_only(finance_models.Pricing.amount),
        )
        .filter(
            sa.and_(
                bookings_models.Booking.id.in_(form.object_ids_list),
                bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
            )
        )
        .all()
    )

    venue_ids = {booking.venueId for booking in bookings}

    if len(venue_ids) > 1:
        flash("Un incident ne peut être créé qu'à partir de réservations venant du même lieu.", "warning")
        return redirect(
            request.referrer or url_for("backoffice_v3_web.individual_bookings.list_individual_bookings"), 301
        )

    booking_incident_already_created = (
        finance_models.BookingFinanceIncident.query.options(
            sa.orm.joinedload(finance_models.BookingFinanceIncident.incident)
        )
        .join(finance_models.FinanceIncident)
        .filter(
            sa.and_(
                finance_models.BookingFinanceIncident.bookingId.in_([booking.id for booking in bookings]),
                finance_models.FinanceIncident.status == finance_models.IncidentStatus.CREATED,
            )
        )
        .count()
    )

    if booking_incident_already_created:
        flash("Au moins une des réservations fait déjà l'objet d'un incident qui n'est pas encore validé.", "warning")
        return redirect(
            request.referrer or url_for("backoffice_v3_web.individual_bookings.list_individual_bookings"), 301
        )

    incident = finance_models.FinanceIncident(
        kind=form.kind.data,
        status=finance_models.IncidentStatus.CREATED,
        venueId=bookings[0].venueId,
        details={
            "origin": form.origin.data,
            "author": current_user.full_name,
            "validator": "",
            "createdAt": datetime.utcnow(),
            "validatedAt": "",
        },
    )
    repository.save(incident)

    booking_finance_incidents_to_create = []

    for booking in bookings:
        booking_finance_incidents_to_create.append(
            finance_models.BookingFinanceIncident(
                bookingId=booking.id,
                incidentId=incident.id,
                beneficiaryId=booking.userId,
                newTotalAmount=_get_booking_reimbursement_amount(booking, float(booking.amount) * 100),
            )
        )
    db.session.add_all(booking_finance_incidents_to_create)
    db.session.commit()

    flash(f"Un incident a bien été créé pour {len(bookings)} réservation(s)", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.individual_bookings.list_individual_bookings"), 301)


def _initialize_additional_data(bookings: list[bookings_models.Booking]) -> dict:
    additional_data = {}

    additional_data["Lieu"] = bookings[0].venue.name

    if len(bookings) == 1:
        booking = bookings[0]

        additional_data["ID de la réservation"] = booking.id
        additional_data["Statut de la réservation"] = booking.status.value
        additional_data["Contremarque"] = booking.token
        additional_data["Nom de l'offre"] = booking.stock.offer.name
        additional_data["Bénéficiaire"] = booking.user.full_name
        # TODO (cmorel): make this field dynamic for other incident types
        additional_data["Montant dû"] = f"{_get_booking_reimbursement_amount(booking, float(booking.amount))} €"
    else:
        additional_data["Nombre de réservations"] = len(bookings)
        # TODO (cmorel): make this field dynamic for other incident types
        total_reimbursement_amount = sum(
            _get_booking_reimbursement_amount(booking, float(booking.amount)) for booking in bookings
        )
        additional_data["Montant dû"] = f"{total_reimbursement_amount} €"

    return additional_data


def _get_booking_reimbursement_amount(booking: bookings_models.Booking, amount: float) -> int:
    reimbursement_amount = (booking.reimbursement_rate / 100) * amount if booking.reimbursement_rate else amount
    return int(reimbursement_amount)
