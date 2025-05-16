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
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import repository as finance_repository
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.routes.serialization import reimbursement_csv_serialize
from pcapi.utils import urls

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

    try:
        dms_stats = dms_api.get_dms_stats(bank_account.dsApplicationId)
        dms_error = None
    except dms_exceptions.DmsGraphQLApiError as e:
        dms_stats = None
        if e.is_not_found:
            dms_error = f"Le dossier {bank_account.dsApplicationId} n'existe pas"
        else:
            dms_error = e.message

    return render_template(
        "bank_account/get.html",
        search_form=pro_forms.CompactProSearchForm(
            q=request.args.get("q"), pro_type=pro_forms.TypeOptions.BANK_ACCOUNT.name
        ),
        search_dst=url_for("backoffice_web.pro.search_pro"),
        bank_account=bank_account,
        dms_stats=dms_stats,
        dms_error=dms_error,
        active_tab=request.args.get("active_tab", "linked_venues"),
        edit_form=edit_form,
    )


@bank_blueprint.route("/<int:bank_account_id>", methods=["GET"])
def get(bank_account_id: int) -> utils.BackofficeResponse:
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter(finance_models.BankAccount.id == bank_account_id)
        .options(
            sa_orm.joinedload(finance_models.BankAccount.offerer),
        )
        .one_or_none()
    )
    if not bank_account:
        raise NotFound()

    return render_bank_account_details(bank_account)


@bank_blueprint.route("/<int:bank_account_id>/linked_venues", methods=["GET"])
def get_linked_venues(bank_account_id: int) -> utils.BackofficeResponse:
    linked_venues = (
        db.session.query(offerers_models.VenueBankAccountLink)
        .filter(
            offerers_models.VenueBankAccountLink.bankAccountId == bank_account_id,
            offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
        )
        .options(
            sa_orm.joinedload(offerers_models.VenueBankAccountLink.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            )
        )
    ).all()

    connect_as = {}
    for linked_venue in linked_venues:
        connect_as[linked_venue.venue.id] = get_connect_as(
            object_type="venue",
            object_id=linked_venue.venue.id,
            pc_pro_path=urls.build_pc_pro_venue_path(linked_venue.venue),
        )

    return render_template(
        "bank_account/get/linked_venues.html",
        bank_account_id=bank_account_id,
        connect_as=connect_as,
        linked_venues=linked_venues,
    )


@bank_blueprint.route("/<int:bank_account_id>/history", methods=["GET"])
def get_history(bank_account_id: int) -> utils.BackofficeResponse:
    actions_history = (
        db.session.query(history_models.ActionHistory)
        .filter_by(bankAccountId=bank_account_id)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .options(
            sa_orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
        )
        .options(
            sa_orm.joinedload(history_models.ActionHistory.venue).load_only(
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
def get_invoices(bank_account_id: int) -> utils.BackofficeResponse:
    invoices = (
        db.session.query(finance_models.Invoice)
        .filter(finance_models.Invoice.bankAccountId == bank_account_id)
        .options(
            sa_orm.joinedload(finance_models.Invoice.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
            sa_orm.joinedload(finance_models.Invoice.bankAccount, innerjoin=True)
            .load_only(finance_models.BankAccount.id)
            .joinedload(finance_models.BankAccount.offerer, innerjoin=True)
            .load_only(offerers_models.Offerer.siren, offerers_models.Offerer.postalCode),
        )
        .order_by(finance_models.Invoice.date.desc())
    ).all()

    return render_template(
        "bank_account/get/invoices.html",
        invoices=invoices,
        bank_account_id=bank_account_id,
    )


@bank_blueprint.route("/<int:bank_account_id>/reimbursement-details", methods=["POST"])
def download_reimbursement_details(bank_account_id: int) -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            request.referrer or url_for("backoffice_web.bank_account.get", bank_account_id=bank_account_id), code=303
        )

    invoices = (
        db.session.query(finance_models.Invoice).filter(finance_models.Invoice.id.in_(form.object_ids_list)).all()
    )
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
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_bank_account(bank_account_id: int) -> utils.BackofficeResponse:
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter_by(id=bank_account_id)
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
            author=current_user,
            bank_account=bank_account,
            modified_info={"label": {"old_info": bank_account.label, "new_info": form.label.data}},
        )
        bank_account.label = form.label.data
        db.session.add(bank_account)
        flash("Les informations ont été mises à jour", "success")

    return redirect(url_for("backoffice_web.bank_account.get", bank_account_id=bank_account_id), code=303)
