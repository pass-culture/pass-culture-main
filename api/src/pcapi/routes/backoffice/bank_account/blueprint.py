from datetime import datetime
from io import BytesIO

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.connectors.dms import api as dms_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import repository as finance_repository
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.serialization import reimbursement_csv_serialize
from pcapi.utils.human_ids import humanize

from . import forms


bank_blueprint = utils.child_backoffice_blueprint(
    "bank_account",
    __name__,
    url_prefix="/pro/bank-account",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def render_bank_account_details(
    bank_account: finance_models.BankAccount, edit_form: forms.EditBankAccountForm | None = None
) -> str:
    if not edit_form and utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY):
        edit_form = forms.EditBankAccountForm(label=bank_account.label)

    return render_template(
        "bank_account/get.html",
        search_form=pro_forms.CompactProSearchForm(
            q=request.args.get("q"), pro_type=pro_forms.TypeOptions.BANK_ACCOUNT.name
        ),
        search_dst=url_for("backoffice_web.pro.search_pro"),
        bank_account=bank_account,
        humanized_bank_account_id=humanize(bank_account.id),
        dms_stats=dms_api.get_dms_stats(bank_account.dsApplicationId),
        active_tab=request.args.get("active_tab", "linked_venues"),
        edit_form=edit_form,
    )


@bank_blueprint.route("/<int:bank_account_id>", methods=["GET"])
@atomic()
def get(bank_account_id: int) -> utils.BackofficeResponse:
    bank_account = (
        finance_models.BankAccount.query.filter(finance_models.BankAccount.id == bank_account_id)
        .options(
            sa.orm.joinedload(finance_models.BankAccount.offerer),
        )
        .one_or_none()
    )
    if not bank_account:
        raise NotFound()

    return render_bank_account_details(bank_account)


@bank_blueprint.route("/<int:bank_account_id>/linked_venues", methods=["GET"])
@atomic()
def get_linked_venues(bank_account_id: int) -> utils.BackofficeResponse:
    linked_venues = (
        offerers_models.VenueBankAccountLink.query.filter(
            offerers_models.VenueBankAccountLink.bankAccountId == bank_account_id,
            offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
        ).options(
            sa.orm.joinedload(offerers_models.VenueBankAccountLink.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            )
        )
    ).all()

    return render_template(
        "bank_account/get/linked_venues.html", linked_venues=linked_venues, bank_account_id=bank_account_id
    )


@bank_blueprint.route("/<int:bank_account_id>/history", methods=["GET"])
@atomic()
def get_history(bank_account_id: int) -> utils.BackofficeResponse:
    actions_history = (
        history_models.ActionHistory.query.filter_by(bankAccountId=bank_account_id)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .options(
            sa.orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
        )
        .options(
            sa.orm.joinedload(history_models.ActionHistory.venue).load_only(
                offerers_models.Venue.id, offerers_models.Venue.name, offerers_models.Venue.publicName
            )
        )
        .all()
    )

    return render_template(
        "bank_account/get/history.html",
        actions=actions_history,
    )


@bank_blueprint.route("/<int:bank_account_id>/invoices", methods=["GET"])
@atomic()
def get_invoices(bank_account_id: int) -> utils.BackofficeResponse:
    invoices = (
        finance_models.Invoice.query.filter(finance_models.Invoice.bankAccountId == bank_account_id)
        .options(
            sa.orm.joinedload(finance_models.Invoice.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
        )
        .order_by(finance_models.Invoice.date.desc())
    ).all()

    return render_template(
        "bank_account/get/invoices.html",
        invoices=invoices,
        bank_account_id=bank_account_id,
    )


@bank_blueprint.route("/<int:bank_account_id>/reimbursement-details", methods=["POST"])
@atomic()
def download_reimbursement_details(bank_account_id: int) -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            request.referrer or url_for("backoffice_web.bank_account.get", bank_account_id=bank_account_id), code=303
        )

    invoices = finance_models.Invoice.query.filter(finance_models.Invoice.id.in_(form.object_ids_list)).all()
    reimbursement_details = [
        reimbursement_csv_serialize.ReimbursementDetails(details)
        for details in finance_repository.find_all_invoices_finance_details([invoice.id for invoice in invoices])
    ]
    export_data = reimbursement_csv_serialize.generate_reimbursement_details_csv(reimbursement_details)
    export_date = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")
    return send_file(
        BytesIO(export_data.encode("utf-8-sig")),
        as_attachment=True,
        download_name=f"details_remboursements_{bank_account_id}_{export_date}.csv",
        mimetype="text/csv",
    )


@bank_blueprint.route("/<int:bank_account_id>", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_bank_account(bank_account_id: int) -> utils.BackofficeResponse:
    bank_account = (
        finance_models.BankAccount.query.filter_by(id=bank_account_id)
        .populate_existing()
        .with_for_update(key_share=True)
        .one_or_none()
    )
    if not bank_account:
        raise NotFound()

    form = forms.EditBankAccountForm()
    if not form.validate():
        msg = Markup(
            """
            <button type="button"
                    class="btn"
                    data-bs-toggle="modal"
                    data-bs-target="#edit-bank-account-modal">
                Les données envoyées comportent des erreurs. Afficher
            </button>
            """
        ).format()
        flash(msg, "warning")
        return render_bank_account_details(bank_account, edit_form=form), 400

    if bank_account.label != form.label.data:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            current_user,
            bank_account=bank_account,
            modified_info={"label": {"old_info": bank_account.label, "new_info": form.label.data}},
        )
        bank_account.label = form.label.data
        db.session.add(bank_account)
        flash("Les informations ont été mises à jour", "success")

    return redirect(url_for("backoffice_web.bank_account.get", bank_account_id=bank_account_id), code=303)
