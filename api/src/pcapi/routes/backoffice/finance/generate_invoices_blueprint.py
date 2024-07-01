from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
import sqlalchemy as sa

from pcapi.core.finance import api as finance_api
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import models as finance_models
from pcapi.core.permissions import models as perm_models
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.tasks import finance_tasks


finance_invoices_blueprint = utils.child_backoffice_blueprint(
    "finance_invoices",
    __name__,
    url_prefix="/finance/invoices",
    permission=perm_models.Permissions.GENERATE_INVOICES,
)


@finance_invoices_blueprint.route("", methods=["GET"])
@atomic()
def get_finance_invoices() -> utils.BackofficeResponse:
    is_task_already_running = not finance_tasks.is_generate_invoices_queue_empty()
    number_of_invoices_to_generate = current_app.redis_client.get(finance_conf.REDIS_GENERATE_INVOICES_LENGTH)
    number_of_invoices_left_to_generate = current_app.redis_client.get(finance_conf.REDIS_INVOICES_LEFT_TO_GENERATE)

    last_cashflow_batches = (
        finance_models.CashflowBatch.query.options(sa.orm.joinedload(finance_models.CashflowBatch.cashflows))
        .order_by(finance_models.CashflowBatch.id.desc())
        .limit(2)  # The last two batches are used in the view
        .all()
    )
    last_cashflow_batch, second_last_cashflow_batch = last_cashflow_batches[0], last_cashflow_batches[1]
    last_cashflow_has_cashflows_under_review = any(
        cashflow.status == finance_models.CashflowStatus.UNDER_REVIEW for cashflow in last_cashflow_batch.cashflows
    )

    return render_template(
        "finance/invoices/get.html",
        is_task_already_running=is_task_already_running,
        number_of_invoices_to_generate=number_of_invoices_to_generate,
        number_of_invoices_left_to_generate=number_of_invoices_left_to_generate,
        last_cashflow_batch=last_cashflow_batch,
        second_last_cashflow_batch=second_last_cashflow_batch,
        last_cashflow_has_cashflows_under_review=last_cashflow_has_cashflows_under_review,
    )


@finance_invoices_blueprint.route("/generate-invoices", methods=["GET"])
@atomic()
def get_finance_invoices_generation_form() -> utils.BackofficeResponse:
    latest_cashflow_batch = finance_models.CashflowBatch.query.order_by(finance_models.CashflowBatch.id.desc()).first()
    form = empty_forms.EmptyForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.finance_invoices.generate_invoices"),
        div_id="generate-invoices-modal",
        title=f"Générer le justificatif {latest_cashflow_batch.label}",
        button_text="Générer le justificatif",
    )


@finance_invoices_blueprint.route("/generate-invoices", methods=["POST"])
@atomic()
def generate_invoices() -> utils.BackofficeResponse:
    latest_cashflow_batch = finance_models.CashflowBatch.query.order_by(finance_models.CashflowBatch.id.desc()).first()
    if not finance_tasks.is_generate_invoices_queue_empty():
        mark_transaction_as_invalid()
        flash("La tâche de génération des justificatifs est déjà en cours", "warning")
        return redirect(url_for("backoffice_web.finance_invoices.get_finance_invoices"), code=303)

    finance_api.async_generate_invoices(latest_cashflow_batch)
    flash("La tâche de génération des justificatifs a été lancée", "success")
    return redirect(url_for("backoffice_web.finance_invoices.get_finance_invoices"), code=303)
