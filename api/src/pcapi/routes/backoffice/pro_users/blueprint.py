from functools import partial

import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.core import mails as mails_api
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.email import update as email_update
from pcapi.models import beneficiary_import as beneficiary_import_models
from pcapi.models import beneficiary_import_status as beneficiary_import_status_models
from pcapi.models import db
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro import forms as pro_forms
from pcapi.routes.backoffice.pro_users import forms as pro_users_forms
from pcapi.routes.backoffice.users import forms as user_forms
from pcapi.tasks.batch_tasks import DeleteBatchUserAttributesRequest
from pcapi.tasks.batch_tasks import delete_user_attributes_task
from pcapi.utils import email as email_utils


pro_user_blueprint = utils.child_backoffice_blueprint(
    "pro_user",
    __name__,
    url_prefix="/pro/user/<int:user_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@pro_user_blueprint.route("", methods=["GET"])
def get(user_id: int) -> utils.BackofficeResponse:
    # Make sure user is pro
    user = (
        users_api.get_pro_account_base_query(user_id)
        .options(
            sa_orm.joinedload(users_models.User.UserOfferers).load_only(offerers_models.UserOfferer.validationStatus),
        )
        .one_or_none()
    )
    if not user:
        flash("Cet utilisateur n'a pas de compte pro ou n'existe pas", "warning")
        return redirect(url_for("backoffice_web.pro.search_pro"), code=303)
    form_class = pro_users_forms.EditProUserForm
    form = form_class(
        first_name=user.firstName,
        last_name=user.lastName,
        email=user.email,
        phone_number=user.phoneNumber,
        postal_code=user.postalCode,
        marketing_email_subscription=user.get_notification_subscriptions().marketing_email,
    )
    dst = url_for(".update_pro_user", user_id=user.id)

    if request.args.get("q") and request.args.get("search_rank"):
        utils.log_backoffice_tracking_data(
            event_name="ConsultCard",
            extra_data={
                "searchType": "ProSearch",
                "searchProType": pro_forms.TypeOptions.USER.name,
                "searchQuery": request.args.get("q"),
                "searchRank": request.args.get("search_rank"),
                "searchNbResults": request.args.get("total_items"),
            },
        )

    return render_template(
        "pro_user/get.html",
        search_form=pro_forms.CompactProSearchForm(q=request.args.get("q"), pro_type=pro_forms.TypeOptions.USER.name),
        search_dst=url_for("backoffice_web.pro.search_pro"),
        user=user,
        form=form,
        dst=dst,
        empty_form=empty_forms.EmptyForm(),
        **user_forms.get_toggle_suspension_args(user, suspension_type=user_forms.SuspensionUserType.PRO),
        **_get_delete_kwargs(user),
    )


@pro_user_blueprint.route("/details", methods=["GET"])
def get_details(user_id: int) -> utils.BackofficeResponse:
    user = users_api.get_pro_account_base_query(user_id).one_or_none()
    if not user:
        raise NotFound()

    actions = history_repository.find_all_actions_by_user(user_id)
    can_add_comment = utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
    user_offerers = (
        db.session.query(offerers_models.UserOfferer)
        .filter_by(userId=user_id)
        .order_by(offerers_models.UserOfferer.dateCreated)
        .options(sa_orm.joinedload(offerers_models.UserOfferer.offerer))
        .all()
    )

    form = pro_users_forms.CommentForm()
    dst = url_for("backoffice_web.pro_user.comment_pro_user", user_id=user.id)

    return render_template(
        "pro_user/get/details.html",
        user=user,
        form=form,
        dst=dst,
        actions=actions,
        can_add_comment=can_add_comment,
        user_offerers=user_offerers,
        active_tab=request.args.get("active_tab", "history"),
    )


@pro_user_blueprint.route("", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_pro_user(user_id: int) -> utils.BackofficeResponse:
    user = (
        users_api.get_pro_account_base_query(user_id).populate_existing().with_for_update(key_share=True).one_or_none()
    )
    if not user:
        raise NotFound()

    form = pro_users_forms.EditProUserForm()
    if not form.validate():
        mark_transaction_as_invalid()
        dst = url_for(".update_pro_user", user_id=user_id)
        flash("Le formulaire n'est pas valide", "warning")
        return render_template("pro_user/get.html", form=form, dst=dst, user=user), 400

    snapshot = users_api.update_user_info(
        user,
        author=current_user,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        phone_number=form.phone_number.data,
        postal_code=form.postal_code.data,
        marketing_email_subscription=form.marketing_email_subscription.data,
        commit=False,
    )

    if form.email.data and form.email.data != email_utils.sanitize_email(user.email):
        old_email = user.email
        snapshot.set("email", old=old_email, new=form.email.data)

        try:
            email_update.request_email_update_from_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            mark_transaction_as_invalid()
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            dst = url_for(".update_pro_user", user_id=user.id)
            return render_template("pro_user/get.html", form=form, dst=dst, user=user), 400

        external_attributes_api.update_external_pro(old_email)  # to delete previous user info from Brevo
        external_attributes_api.update_external_user(user)

    snapshot.add_action()
    db.session.flush()

    flash("Les informations ont été mises à jour", "success")
    return redirect(url_for(".get", user_id=user_id), code=303)


@pro_user_blueprint.route("/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def delete(user_id: int) -> utils.BackofficeResponse:
    user = users_api.get_pro_account_base_query(user_id).populate_existing().with_for_update().one_or_none()
    if not user:
        raise NotFound()

    if not _user_can_be_deleted(user):
        mark_transaction_as_invalid()
        flash("Le compte est rattaché à une entité juridique", "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    form = pro_users_forms.DeleteProUser()
    if not form.validate():
        mark_transaction_as_invalid()
        flash("Le formulaire n'est pas valide", "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    if not form.email.data == user.email:
        mark_transaction_as_invalid()
        flash("L'email saisi ne correspond pas à celui du compte", "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    # clear from mailing list
    if (
        not db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.bookingEmail == user.email)
        .limit(1)
        .count()
    ):
        on_commit(partial(mails_api.delete_contact, user.email, True))

    # clear from push notifications
    payload = DeleteBatchUserAttributesRequest(user_id=user.id)
    on_commit(partial(delete_user_attributes_task.delay, payload))

    # Delete all related objects if the user has already been created as a beneficiary
    db.session.query(beneficiary_import_status_models.BeneficiaryImportStatus).filter(
        beneficiary_import_status_models.BeneficiaryImportStatus.id.in_(
            db.session.query(beneficiary_import_status_models.BeneficiaryImportStatus)
            .with_entities(
                beneficiary_import_status_models.BeneficiaryImportStatus.id,
            )
            .join(
                beneficiary_import_status_models.BeneficiaryImportStatus.beneficiaryImport,
            )
            .filter(
                beneficiary_import_models.BeneficiaryImport.beneficiaryId == user_id,
            )
            .scalar_subquery()
        )
    ).delete(
        synchronize_session=False,
    )
    user_deposits_query = db.session.query(finance_models.Deposit).filter(finance_models.Deposit.userId == user_id)
    for deposit in user_deposits_query:
        db.session.query(finance_models.Recredit).filter(finance_models.Recredit.depositId == deposit.id).delete(
            synchronize_session=False
        )
    user_deposits_query.delete(synchronize_session=False)
    db.session.query(beneficiary_import_models.BeneficiaryImport).filter(
        beneficiary_import_models.BeneficiaryImport.beneficiaryId == user_id
    ).delete(synchronize_session=False)
    db.session.query(fraud_models.BeneficiaryFraudCheck).filter(
        fraud_models.BeneficiaryFraudCheck.userId == user_id
    ).delete(synchronize_session=False)

    db.session.query(users_models.User).filter(users_models.User.id == user_id).delete(synchronize_session=False)
    db.session.flush()
    flash("Le compte a été supprimé", "success")
    return redirect(url_for("backoffice_web.pro.search_pro"), code=303)


@pro_user_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_pro_user(user_id: int) -> utils.BackofficeResponse:
    user = (
        users_api.get_pro_account_base_query(user_id)
        .populate_existing()
        .with_for_update(key_share=True, read=True)
        .one_or_none()
    )
    if not user:
        raise NotFound()

    form = pro_users_forms.CommentForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    users_api.add_comment_to_user(user=user, author_user=current_user, comment=form.comment.data)
    flash("Le commentaire a été enregistré", "success")

    return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)


@pro_user_blueprint.route("/validate-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def validate_pro_user_email(user_id: int) -> utils.BackofficeResponse:
    user = (
        users_api.get_pro_account_base_query(user_id).populate_existing().with_for_update(key_share=True).one_or_none()
    )
    if not user:
        raise NotFound()

    if user.isEmailValidated:
        mark_transaction_as_invalid()
        flash(Markup("L'email <b>{email}</b> est déjà validé !").format(email=user.email), "warning")
    else:
        users_api.validate_pro_user_email(user=user, author_user=current_user)
        flash(Markup("L'email <b>{email}</b> est validé !").format(email=user.email), "success")
    return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)


def _user_can_be_deleted(user: users_models.User) -> bool:
    return user.has_non_attached_pro_role and len(user.roles) == 1 and not user.UserOfferers


def _get_delete_kwargs(user: users_models.User) -> dict:
    kwargs = {
        "can_be_deleted": _user_can_be_deleted(user),
        "delete_dst": url_for("backoffice_web.pro_user.delete", user_id=user.id),
        "delete_form": pro_users_forms.DeleteProUser(),
    }
    return kwargs
