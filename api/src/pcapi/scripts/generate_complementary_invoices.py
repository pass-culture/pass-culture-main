import collections
import datetime
import itertools
import logging
import secrets
import statistics
import time

import click
from flask import render_template
import pytz
import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.logging import log_elapsed
import pcapi.core.payments.models as payments_models
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


BATCHES_TO_GENERATE = [
    "VIR57",
    "VIR58",
    "VIR59",
    "VIR60",
    "VIR61",
    "VIR62",
    "VIR63",
    "VIR64",
    "VIR65",
    "VIR66",
    "VIR67",
]


def _get_eta(total: int, current: int, elapsed_per_invoice: list[float]) -> str:
    left_to_do = total - current
    left_to_wait = left_to_do * statistics.mean(elapsed_per_invoice)
    eta = pytz.utc.localize(datetime.datetime.utcnow() + datetime.timedelta(seconds=left_to_wait)).astimezone(
        pytz.timezone("Europe/Paris")
    )
    return eta.strftime("%d/%m/%Y %H:%M:%S")


# FIXME (dbaty, 2022-09-21): remove this command and the HTML template
# once invoices have been generated.
@blueprint.cli.command("generate_complementary_invoices")
@click.option("--after-id", help="Limit to invoices id after ID (not included)", default=0)
@click.option("--only-id", help="Limit to this specific invoice id", default=0)
def generate_complementary_invoices(after_id: int, only_id: int) -> None:
    """Generate and store complementary invoices, up to cashflow batch N
    (included).
    """
    invoices = (
        finance_models.Invoice.query.join(finance_models.Invoice.cashflows)
        .join(finance_models.Cashflow.batch)
        .filter(finance_models.CashflowBatch.label.in_(BATCHES_TO_GENERATE))
        .options(sqla_orm.contains_eager(finance_models.Invoice.cashflows))
    )
    if after_id:
        invoices = invoices.filter(finance_models.Invoice.id > after_id)
    if only_id:
        invoices = invoices.filter(finance_models.Invoice.id == only_id)
    invoices = invoices.distinct(finance_models.Invoice.id).order_by(finance_models.Invoice.id)
    total = invoices.count()
    print(f"Found {total} invoices to generate")
    done = 0
    elapsed_per_invoice = []
    for original_invoice in invoices:
        start = time.perf_counter()
        with log_elapsed(
            logger,
            f"Generated complementary invoice {original_invoice.id}: {original_invoice.reference}.2",
        ):
            reimbursement_point_id = original_invoice.reimbursementPointId
            cashflow_ids = [c.id for c in original_invoice.cashflows]
            # It's important to call our custom function (defined
            # below) and NOT `core.finance.api._generate_invoice()`.
            complementary_invoice = _custom_generate_invoice(
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
                original_invoice=original_invoice,
            )
            # Again, call our custom function that uses a custom
            # template.
            html = _custom_generate_invoice_html(
                complementary_invoice,
                use_reimbursement_point=True,
            )
            finance_api._store_invoice_pdf(complementary_invoice.storage_object_id, html)
        done += 1
        elapsed = time.perf_counter() - start
        elapsed_per_invoice.append(elapsed)
        if done % 100 == 0:
            eta = _get_eta(total, done, elapsed_per_invoice)
            print(f"  => {done} done, ETA = {eta}")


def _custom_generate_invoice_html(invoice: finance_models.Invoice, use_reimbursement_point: bool) -> str:
    context = finance_api._prepare_invoice_context(invoice, use_reimbursement_point)
    context["original_reference_number"] = invoice.reference.replace(".2", "")
    return render_template("invoices/complementary_invoice.html", **context)


# This is a copy of `core.finance.api._generate_invoice()`, except:
# - we control the invoice reference (and do not increment the
#   `reference_number` table);
# - we do not update the statuses of cashflows, pricings and bookings
#   (because it's been done when generating the original invoice);
def _custom_generate_invoice(
    reimbursement_point_id: int | None,
    cashflow_ids: list[int],
    original_invoice: finance_models.Invoice,
) -> finance_models.Invoice:
    invoice = finance_models.Invoice(
        reimbursementPointId=reimbursement_point_id,
        date=original_invoice.date,
    )
    total_reimbursed_amount = 0
    cashflows = finance_models.Cashflow.query.filter(finance_models.Cashflow.id.in_(cashflow_ids)).options(
        sqla_orm.joinedload(finance_models.Cashflow.pricings)
        .options(sqla_orm.joinedload(finance_models.Pricing.lines))
        .options(sqla_orm.joinedload(finance_models.Pricing.customRule))
    )
    pricings_and_rates_by_rule_group = collections.defaultdict(list)
    pricings_by_custom_rule = collections.defaultdict(list)

    cashflows_pricings = [cf.pricings for cf in cashflows]
    flat_pricings = list(itertools.chain.from_iterable(cashflows_pricings))
    for pricing in flat_pricings:
        rule_reference = pricing.standardRule or pricing.customRuleId
        rule = finance_api.find_reimbursement_rule(rule_reference)
        if isinstance(rule, payments_models.CustomReimbursementRule):
            pricings_by_custom_rule[rule].append(pricing)
        else:
            pricings_and_rates_by_rule_group[rule.group].append((pricing, rule.rate))  # type: ignore [attr-defined]

    invoice_lines = []
    for rule_group, pricings_and_rates in pricings_and_rates_by_rule_group.items():
        rates = collections.defaultdict(list)
        for pricing, rate in pricings_and_rates:
            rates[rate].append(pricing)
        for rate, pricings in rates.items():
            invoice_line, reimbursed_amount = finance_api._make_invoice_line(rule_group, pricings, rate)  # type: ignore [arg-type]
            invoice_lines.append(invoice_line)
            total_reimbursed_amount += reimbursed_amount

    for custom_rule, pricings in pricings_by_custom_rule.items():
        # An InvoiceLine rate will be calculated for a CustomRule with a set reimbursed amount
        invoice_line, reimbursed_amount = finance_api._make_invoice_line(custom_rule.group, pricings, custom_rule.rate)  # type: ignore [arg-type]
        invoice_lines.append(invoice_line)
        total_reimbursed_amount += reimbursed_amount

    invoice.amount = total_reimbursed_amount
    # As of Python 3.9, DEFAULT_ENTROPY is 32 bytes
    invoice.token = secrets.token_urlsafe()
    invoice.reference = original_invoice.reference + ".2"
    db.session.add(invoice)
    db.session.flush()
    for line in invoice_lines:
        line.invoiceId = invoice.id
    db.session.bulk_save_objects(invoice_lines)
    cf_links = [finance_models.InvoiceCashflow(invoiceId=invoice.id, cashflowId=cashflow.id) for cashflow in cashflows]
    db.session.bulk_save_objects(cf_links)
    db.session.commit()
    return invoice
