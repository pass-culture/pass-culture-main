from functools import partial

import sqlalchemy as sa
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from markupsafe import Markup
from sqlalchemy import orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import tasks as finance_tasks
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import blueprint as backoffice_blueprint
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.utils import access_control
from pcapi.routes.backoffice.utils import response as response_utils
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import on_commit


settlements_blueprint = backoffice_blueprint.child_backoffice_blueprint(
    "settlements",
    __name__,
    url_prefix="/finance/settlements",
    permission=perm_models.Permissions.READ_SETTLEMENTS,
)


@settlements_blueprint.route("", methods=["GET"])
def list_settlement_batches() -> response_utils.BackofficeResponse:
    total_amount_subquery = (
        db.session.query(sa.func.sum(finance_models.Settlement.amount))
        .filter(finance_models.Settlement.batchId == finance_models.SettlementBatch.id)
        .correlate(finance_models.SettlementBatch)
        .scalar_subquery()
    )

    rows = (
        db.session.query(
            finance_models.SettlementBatch.id,
            finance_models.SettlementBatch.name,
            finance_models.SettlementBatch.label,
            finance_models.SettlementBatch.dateValidated,
            total_amount_subquery.label("total_amount"),
        )
        .order_by(
            finance_models.SettlementBatch.dateValidated.desc().nulls_first(),
            finance_models.SettlementBatch.dateImported.desc(),
        )
        .all()
    )

    return render_template("finance/settlements/list.html", rows=rows)


@settlements_blueprint.route("/<int:batch_id>/validate", methods=["GET"])
@access_control.permission_required(perm_models.Permissions.MANAGE_SETTLEMENTS)
def get_validate_settlement_batch_form(batch_id: int) -> response_utils.BackofficeResponse:
    settlement_batch = (
        db.session.query(finance_models.SettlementBatch)
        .filter_by(id=batch_id)
        .options(
            sa_orm.joinedload(finance_models.SettlementBatch.settlements).load_only(finance_models.Settlement.amount)
        )
        .one_or_none()
    )
    if not settlement_batch:
        raise NotFound()

    return render_template(
        "components/dynamic/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for(".validate_settlement_batch", batch_id=batch_id),
        div_id=f"validate-settlement-batch-modal-{batch_id}",
        title=f"Validation du lot {settlement_batch.name}",
        information=Markup(
            "<p>Vous vous apprêtez à valider le lot <strong>{label}</strong> comme exécuté par la banque.</p>"
            "<p>Ce lot regroupe <strong>{count}</strong> virement{s} pour un total de <strong>{amount}</strong>.</p>"
            "<p>Cette action est irréversible. Une tâche sera lancée pour la mise à jour de l'état des factures et "
            "l'envoi d'email aux acteurs culturels, dont la fin sera notifiée sur le canal Slack #{channel}.</p>"
        ).format(
            label=settlement_batch.label,
            count=len(settlement_batch.settlements),
            s=filters.pluralize(len(settlement_batch.settlements)),
            amount=filters.format_cents(sum(settlement.amount for settlement in settlement_batch.settlements)),
            channel=settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL,
        ),
        button_text="Valider",
        ajax_submit=False,
    )


@settlements_blueprint.route("/<int:batch_id>/validate", methods=["POST"])
@access_control.permission_required(perm_models.Permissions.MANAGE_SETTLEMENTS)
def validate_settlement_batch(batch_id: int) -> response_utils.BackofficeResponse:
    settlement_batch = db.session.query(finance_models.SettlementBatch).filter_by(id=batch_id).one_or_none()
    if not settlement_batch:
        raise NotFound()

    settlement_batch.dateValidated = date_utils.get_naive_utc_now()
    db.session.add(settlement_batch)

    on_commit(
        partial(
            finance_tasks.settlement_batch_validation_task,
            finance_tasks.ValidateSettlementBatchRequest(batch_id=batch_id).model_dump(),
        )
    )

    flash(
        Markup(
            "Le lot {name} a été validé. Les virements, factures et réservations sont en cours de mise à jour"
        ).format(name=settlement_batch.name),
        "success",
    )
    return redirect(url_for(".list_settlement_batches"), code=303)
