import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.routes.backoffice import utils

from . import forms


non_payment_notices_blueprint = utils.child_backoffice_blueprint(
    "non_payment_notices",
    __name__,
    url_prefix="/non-payment-notices",
    permission=perm_models.Permissions.READ_NON_PAYMENT_NOTICES,
)


def _get_notices() -> list[offerers_models.NonPaymentNotice]:
    notices_query = (
        db.session.query(offerers_models.NonPaymentNotice)
        .options(
            sa_orm.joinedload(offerers_models.NonPaymentNotice.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.managingOffererId,
            ),
            sa_orm.joinedload(offerers_models.NonPaymentNotice.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
                offerers_models.Offerer.postalCode,
            ),
            sa_orm.joinedload(offerers_models.NonPaymentNotice.batch).load_only(finance_models.CashflowBatch.label),
        )
        .order_by(sa.desc(offerers_models.NonPaymentNotice.dateCreated))
    )

    notices = notices_query.all()
    return notices


@non_payment_notices_blueprint.route("", methods=["GET"])
def list_notices() -> utils.BackofficeResponse:
    notices = _get_notices()

    return render_template(
        "non_payment_notices/list.html",
        rows=notices,
    )


@non_payment_notices_blueprint.route("/create", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def get_create_non_payment_notice_form() -> utils.BackofficeResponse:
    form = forms.CreateNonPaymentNoticeForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.non_payment_notices.create_non_payment_notice"),
        div_id="create-non-payment-notice",  # must be consistent with parameter passed to build_lazy_modal
        title="Saisir un avis d'impayé",
        button_text="Saisir l'avis",
    )


@non_payment_notices_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def create_non_payment_notice() -> utils.BackofficeResponse:
    form = forms.CreateNonPaymentNoticeForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.non_payment_notices.list_notices"), code=303)

    try:
        notice = offerers_models.NonPaymentNotice(
            amount=form.amount.data,
            dateReceived=form.date_received.data,
            emitterEmail=form.emitter_email.data,
            emitterName=form.emitter_name.data,
            noticeType=offerers_models.NoticeType[form.notice_type.data],
            offererId=int(form.offerer.data[0]) if form.offerer.data[0] else None,
            reference=form.reference.data,
            venueId=int(form.venue.data[0]) if form.venue.data[0] else None,
        )
        db.session.add(notice)
        history_api.add_action(
            history_models.ActionType.NON_PAYMENT_NOTICE_CREATED,
            author=current_user,
            notice=notice,
            venue=notice.venue,
            offerer=notice.offerer,
        )
        db.session.flush()

        flash("L'avis d'impayé a été créé", "success")

    except sa_exc.IntegrityError as err:
        mark_transaction_as_invalid()
        flash(Markup("Erreur dans la création de l'avis d'impayé : {message}").format(message=str(err)), "warning")

    return redirect(url_for("backoffice_web.non_payment_notices.list_notices"), code=303)
