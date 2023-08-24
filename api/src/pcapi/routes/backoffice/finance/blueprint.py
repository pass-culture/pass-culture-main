from datetime import datetime

from flask import Response
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import repository
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.finance import forms
from pcapi.routes.backoffice.offerers import forms as offerer_forms
from pcapi.utils.human_ids import humanize


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
    )
    return query.order_by(finance_models.FinanceIncident.id).all()


@finance_incident_blueprint.route("/incidents", methods=["GET"])
def list_incidents() -> utils.BackofficeResponse:
    incidents = _get_incidents()
    return render_template("finance/incident/list.html", rows=incidents)


def render_finance_incident(incident: finance_models.FinanceIncident) -> utils.BackofficeResponse:
    if incident.venue.current_reimbursement_point_id:
        current_reimbursement_point = offerer_models.Venue.query.get(incident.venue.current_reimbursement_point_id)
    else:
        current_reimbursement_point = incident.venue

    return render_template(
        "finance/incident/get.html",
        booking_finance_incidents=incident.booking_finance_incidents,
        total_amount=sum(
            bookingIncident.booking.pricing.amount for bookingIncident in incident.booking_finance_incidents
        ),
        incident=incident,
        reimbursement_point=current_reimbursement_point,
        reimbursement_point_humanized_id=humanize(current_reimbursement_point.id),
        active_tab=request.args.get("active_tab", "bookings"),
    )


@finance_incident_blueprint.route("/incident/<int:finance_incident_id>/cancel", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def get_finance_incident_cancellation_form(finance_incident_id: int) -> utils.BackofficeResponse:
    form = offerer_forms.CommentForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.finance_incident.cancel_finance_incident", finance_incident_id=finance_incident_id),
        div_id=f"reject-finance-incident-modal-{finance_incident_id}",
        title="Annuler l'incident",
        button_text="Confirmer l'annulation",
    )


def _cancel_finance_incident(incident: finance_models.FinanceIncident, comment: str) -> None:
    if incident.status == finance_models.IncidentStatus.CANCELLED:
        raise finance_exceptions.FinanceIncidentAlreadyCancelled
    if incident.status == finance_models.IncidentStatus.VALIDATED:
        raise finance_exceptions.FinanceIncidentAlreadyValidated

    incident.status = finance_models.IncidentStatus.CANCELLED

    action = history_api.log_action(
        history_models.ActionType.FINANCE_INCIDENT_CANCELLED,
        author=current_user,
        finance_incident=incident,
        comment=comment,
        save=False,
    )

    repository.save(incident, action)


@finance_incident_blueprint.route("/incident/<int:finance_incident_id>/cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def cancel_finance_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident: finance_models.FinanceIncident = finance_models.FinanceIncident.query.get_or_404(finance_incident_id)

    form = offerer_forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return render_finance_incident(incident)

    try:
        _cancel_finance_incident(incident, form.comment.data)
    except finance_exceptions.FinanceIncidentAlreadyCancelled:
        flash("L'incident a déjà été annulé", "warning")
        return render_finance_incident(incident)
    except finance_exceptions.FinanceIncidentAlreadyValidated:
        flash("Impossible d'annuler un incident déjà validé", "warning")
        return render_finance_incident(incident)

    flash("L'incident a été annulé avec succès", "success")
    return render_finance_incident(incident)


@finance_incident_blueprint.route("/incident/<int:finance_incident_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_INCIDENTS)
def get_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = (
        finance_models.FinanceIncident.query.filter_by(id=finance_incident_id)
        .options(
            # Venue infos
            sa.orm.joinedload(offerer_models.Venue, finance_models.FinanceIncident.venue).load_only(
                offerer_models.Venue.id, offerer_models.Venue.name
            ),
            # Booking incidents infos
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            ).load_only(
                finance_models.BookingFinanceIncident.id,
                finance_models.BookingFinanceIncident.newTotalAmount,
            )
            # Bookings infos
            .joinedload(finance_models.BookingFinanceIncident.booking).load_only(
                bookings_models.Booking.id,
                bookings_models.Booking.cancellationDate,
                bookings_models.Booking.cancellationReason,
                bookings_models.Booking.dateCreated,
                bookings_models.Booking.dateUsed,
                bookings_models.Booking.status,
                bookings_models.Booking.token,
            )
            # Booking venue infos
            .joinedload(bookings_models.Booking.venue).load_only(offerer_models.Venue.bookingEmail),
            # booking user infos
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
            # booking deposit infos
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.booking)
            .joinedload(bookings_models.Booking.deposit)
            .load_only(finance_models.Deposit.type),
            # booking pricing infos
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
            # booking stock infos
            sa.orm.joinedload(
                finance_models.BookingFinanceIncident, finance_models.FinanceIncident.booking_finance_incidents
            )
            .joinedload(finance_models.BookingFinanceIncident.booking)
            .joinedload(bookings_models.Booking.stock)
            .load_only(
                offers_models.Stock.beginningDatetime,
            )
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.url,
                offers_models.Offer.subcategoryId,
            ),
        )
        .one_or_none()
    )

    if not incident:
        raise NotFound()

    return render_finance_incident(incident)


@finance_incident_blueprint.route("/incident/<int:finance_incident_id>/history", methods=["GET"])
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
        "finance/incident/get/details/history.html",
        actions=actions,
        form=offerer_forms.CommentForm(),
        dst=url_for("backoffice_web.finance_incident.comment_incident", finance_incident_id=finance_incident_id),
    )


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
        dst=url_for("backoffice_web.finance_incident.create_incident"),
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
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 301)

    booking_incident_already_created_or_validated = (
        finance_models.BookingFinanceIncident.query.options(
            sa.orm.joinedload(finance_models.BookingFinanceIncident.incident)
        )
        .join(finance_models.FinanceIncident)
        .filter(
            sa.and_(
                finance_models.BookingFinanceIncident.bookingId.in_([booking.id for booking in bookings]),
                finance_models.FinanceIncident.status.in_(
                    [finance_models.IncidentStatus.CREATED, finance_models.IncidentStatus.VALIDATED]
                ),
            )
        )
        .count()
    )

    if booking_incident_already_created_or_validated:
        flash("Au moins une des réservations fait déjà l'objet d'un incident qui n'est pas encore validé.", "warning")
        return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 301)

    incident = finance_models.FinanceIncident(
        kind=form.kind.data,
        status=finance_models.IncidentStatus.CREATED,
        venueId=bookings[0].venueId,
        details={
            "origin": form.origin.data,
            "author": current_user.full_name,
            "validator": "",
            "createdAt": datetime.utcnow().isoformat(),
            "validatedAt": "",
        },
    )

    action = history_api.log_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=current_user,
        finance_incident=incident,
        comment=form.origin.data,
        save=False,
    )

    repository.save(incident, action)

    booking_finance_incidents_to_create = []

    for booking in bookings:
        booking_finance_incidents_to_create.append(
            finance_models.BookingFinanceIncident(
                bookingId=booking.id,
                incidentId=incident.id,
                beneficiaryId=booking.userId,
                newTotalAmount=-booking.pricing.amount,
            )
        )
    db.session.add_all(booking_finance_incidents_to_create)
    db.session.commit()

    flash(f"Un incident a bien été créé pour {len(bookings)} réservation(s)", "success")
    return redirect(request.referrer or url_for("backoffice_web.individual_bookings.list_individual_bookings"), 301)


def _initialize_additional_data(bookings: list[bookings_models.Booking]) -> dict:
    additional_data = {"Lieu": bookings[0].venue.name}

    if len(bookings) == 1:
        booking = bookings[0]

        additional_data["ID de la réservation"] = booking.id
        additional_data["Statut de la réservation"] = booking.status.value
        additional_data["Contremarque"] = booking.token
        additional_data["Nom de l'offre"] = booking.stock.offer.name
        additional_data["Bénéficiaire"] = booking.user.full_name
    else:
        additional_data["Nombre de réservations"] = len(bookings)

    return additional_data


@finance_incident_blueprint.route("/incident/<int:finance_incident_id>/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_INCIDENTS)
def comment_incident(finance_incident_id: int) -> utils.BackofficeResponse:
    incident = finance_models.FinanceIncident.query.get_or_404(finance_incident_id)

    form = offerer_forms.CommentForm()

    if not form.validate():
        flash("Le formulaire comporte des erreurs", "warning")
    else:
        history_api.log_action(
            history_models.ActionType.COMMENT,
            author=current_user,
            finance_incident=incident,
            comment=form.comment.data,
            save=True,
        )
        flash("Commentaire enregistré", "success")

    return redirect(
        url_for("backoffice_web.finance_incident.get_incident", finance_incident_id=incident.id, active_tab="history")
    )
