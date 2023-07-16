from flask import render_template
import sqlalchemy as sa

import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerer_models
import pcapi.core.permissions.models as perm_models

from . import utils


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
