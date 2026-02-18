from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.pro import non_payment_notice_notification
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.models.utils import get_or_404
from pcapi.models.utils import get_or_404_from_query
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms.empty import EmptyForm
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import string as string_utils
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms


non_payment_notices_blueprint = utils.child_backoffice_blueprint(
    "non_payment_notices",
    __name__,
    url_prefix="/non-payment-notices",
    permission=perm_models.Permissions.READ_NON_PAYMENT_NOTICES,
)


def _get_notices(form: forms.GetNoticesSearchForm) -> list[offerers_models.NonPaymentNotice]:
    ids_query = sa.select(offerers_models.NonPaymentNotice.id)

    if form.status.data:
        ids_query = ids_query.filter(
            offerers_models.NonPaymentNotice.status.in_(
                [offerers_models.NoticeStatus[status] for status in form.status.data]
            ),
        )

    if form.notice_type.data:
        ids_query = ids_query.filter(
            offerers_models.NonPaymentNotice.noticeType.in_(
                [offerers_models.NoticeType[notice_type] for notice_type in form.notice_type.data]
            ),
        )

    if form.offerer.data:
        ids_query = ids_query.filter(offerers_models.NonPaymentNotice.offererId.in_(form.offerer.data))

    if form.venue.data:
        ids_query = ids_query.filter(offerers_models.NonPaymentNotice.venueId.in_(form.venue.data))

    if form.batch.data:
        ids_query = ids_query.join(offerers_models.NonPaymentNotice.batches).filter(
            finance_models.CashflowBatch.id.in_(form.batch.data)
        )

    if form.from_to_date.data:
        if form.from_to_date.from_date is not None and form.from_to_date.to_date is not None:
            from_date = date_utils.date_to_localized_datetime(form.from_to_date.from_date, datetime.min.time())
            to_date = date_utils.date_to_localized_datetime(form.from_to_date.to_date, datetime.max.time())
            ids_query = ids_query.filter(offerers_models.NonPaymentNotice.dateReceived.between(from_date, to_date))

    if form.q.data:
        search_query = form.q.data

        if email_utils.is_valid_email(search_query):
            ids_query = ids_query.filter(offerers_models.NonPaymentNotice.emitterEmail == search_query)

        else:
            or_filters = []

            if string_utils.is_numeric(search_query):
                or_filters.extend([offerers_models.NonPaymentNotice.id == int(search_query)])

            search_name = f"%{clean_accents(search_query).replace(' ', '%').replace('-', '%')}%"
            or_filters.extend(
                [
                    sa.func.immutable_unaccent(offerers_models.NonPaymentNotice.emitterName).ilike(search_name),
                    offerers_models.NonPaymentNotice.reference == search_query,
                ]
            )

            ids_query = ids_query.filter(sa.or_(*or_filters))

    ids_query = ids_query.distinct().limit(form.limit.data + 1)

    notices_query = (
        db.session.query(offerers_models.NonPaymentNotice)
        .filter(offerers_models.NonPaymentNotice.id.in_(ids_query))
        .options(
            sa_orm.joinedload(offerers_models.NonPaymentNotice.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.isSoftDeleted,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.siret,
            ),
            sa_orm.joinedload(offerers_models.NonPaymentNotice.offerer).load_only(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            ),
            sa_orm.joinedload(offerers_models.NonPaymentNotice.batches).load_only(finance_models.CashflowBatch.label),
        )
        .order_by(sa.desc(offerers_models.NonPaymentNotice.dateCreated))
    )

    notices = notices_query.all()
    return utils.limit_rows(notices, form.limit.data)


@non_payment_notices_blueprint.route("", methods=["GET"])
def list_notices() -> utils.BackofficeResponse:
    search_form = forms.GetNoticesSearchForm(formdata=utils.get_query_params())

    if not search_form.validate():
        flash(utils.build_form_error_msg(search_form), "warning")
        return render_template("non_payment_notices/list.html", rows=[], form=search_form)

    notices = _get_notices(search_form)

    autocomplete.prefill_offerers_choices(search_form.offerer)
    autocomplete.prefill_venues_choices(search_form.venue)
    autocomplete.prefill_cashflow_batch_choices(search_form.batch)

    return render_template(
        "non_payment_notices/list.html",
        rows=notices,
        form=search_form,
    )


def _redirect_to_list() -> utils.BackofficeResponse:
    return redirect(request.referrer or url_for("backoffice_web.non_payment_notices.list_notices"), code=303)


@non_payment_notices_blueprint.route("/create", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def get_create_non_payment_notice_form() -> utils.BackofficeResponse:
    form = forms.CreateNonPaymentNoticeForm()

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.non_payment_notices.create_non_payment_notice"),
        div_id="create-non-payment-notice",  # must be consistent with parameter passed to build_lazy_modal
        title="Saisir un avis d'impayé",
        button_text="Enregistrer",
        ajax_submit=False,
    )


def _create_or_update_non_payment_notice(
    form: forms.CreateNonPaymentNoticeForm, notice: offerers_models.NonPaymentNotice | None = None
) -> utils.BackofficeResponse:
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_to_list()

    offerer = db.session.get(offerers_models.Offerer, int(form.offerer.data[0])) if form.offerer.data[0] else None
    venue = db.session.get(offerers_models.Venue, int(form.venue.data[0])) if form.venue.data[0] else None

    data = {
        "amount": form.amount.data,
        "fees": form.fees.data,
        "dateReceived": form.date_received.data,
        "emitterEmail": form.emitter_email.data,
        "emitterName": form.emitter_name.data,
        "noticeType": offerers_models.NoticeType[form.notice_type.data],
        "reference": form.reference.data,
        "offerer": offerer,
        "venue": venue,
    }

    try:
        if notice:
            has_offerer_or_venue_changed = (
                data["offerer"] and data["offerer"] != notice.offerer or data["venue"] and data["venue"] != notice.venue
            )
            for key, value in data.items():
                setattr(notice, key, value)
        else:
            has_offerer_or_venue_changed = data["offerer"] or data["venue"]
            notice = offerers_models.NonPaymentNotice(**data)

        db.session.add(notice)
        if has_offerer_or_venue_changed:
            db.session.flush()  # mandatory to get notice.id
            history_api.add_action(
                history_models.ActionType.NON_PAYMENT_NOTICE_CREATED,
                author=current_user,
                offerer=data["offerer"],
                venue=data["venue"],
                non_payment_notice_id=notice.id,
            )
        db.session.flush()
        flash("L'avis d'impayé a été enregistré", "success")

    except sa_exc.IntegrityError as err:
        mark_transaction_as_invalid()
        flash(Markup("Erreur dans l'enregistrement de l'avis d'impayé : {message}").format(message=str(err)), "warning")

    return _redirect_to_list()


@non_payment_notices_blueprint.route("/create", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def create_non_payment_notice() -> utils.BackofficeResponse:
    form = forms.CreateNonPaymentNoticeForm()
    return _create_or_update_non_payment_notice(form)


@non_payment_notices_blueprint.route("/<int:notice_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def get_edit_form(notice_id: int) -> utils.BackofficeResponse:
    notice: offerers_models.NonPaymentNotice = get_or_404(offerers_models.NonPaymentNotice, notice_id)

    form = forms.EditNonPaymentNoticeForm(
        date_received=notice.dateReceived,
        notice_type=notice.noticeType.name,
        amount=notice.amount,
        fees=notice.fees,
        reference=notice.reference,
        emitter_name=notice.emitterName,
        emitter_email=notice.emitterEmail,
    )

    if notice.offererId:
        form.offerer.data = [str(notice.offererId)]
        autocomplete.prefill_offerers_choices(form.offerer)

    if notice.venueId:
        form.venue.data = [str(notice.venueId)]
        autocomplete.prefill_venues_choices(form.venue)

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.non_payment_notices.edit", notice_id=notice_id),
        div_id=f"edit-modal-{notice_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier les informations",
        button_text="Enregistrer",
        ajax_submit=False,
    )


@non_payment_notices_blueprint.route("/<int:notice_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def edit(notice_id: int) -> utils.BackofficeResponse:
    notice: offerers_models.NonPaymentNotice = get_or_404(offerers_models.NonPaymentNotice, notice_id)

    form = forms.EditNonPaymentNoticeForm()
    return _create_or_update_non_payment_notice(form, notice)


@non_payment_notices_blueprint.route("/<int:notice_id>/pending", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def get_set_pending_form(notice_id: int) -> utils.BackofficeResponse:
    form = forms.SetPendingForm()

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.non_payment_notices.set_pending", notice_id=notice_id),
        div_id=f"pending-modal-{notice_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Mettre en attente",
        button_text="Mettre en attente",
        ajax_submit=False,
    )


def _get_notice(notice_id: int) -> offerers_models.NonPaymentNotice:
    query = db.session.query(offerers_models.NonPaymentNotice).options(
        sa_orm.joinedload(offerers_models.NonPaymentNotice.offerer).load_only(offerers_models.Offerer.name),
        sa_orm.joinedload(offerers_models.NonPaymentNotice.batches).load_only(finance_models.CashflowBatch.label),
    )
    return get_or_404_from_query(query, notice_id)


@non_payment_notices_blueprint.route("/<int:notice_id>/pending", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def set_pending(notice_id: int) -> utils.BackofficeResponse:
    notice = _get_notice(notice_id)

    form = forms.SetPendingForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_to_list()

    notice.status = offerers_models.NoticeStatus.PENDING
    notice.motivation = offerers_models.NoticeStatusMotivation(form.motivation.data)
    db.session.add(notice)

    non_payment_notice_notification.send_pending_non_payment_notice_email(notice)

    return _redirect_to_list()


@non_payment_notices_blueprint.route("/<int:notice_id>/no-continuation", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def get_set_no_continuation_form(notice_id: int) -> utils.BackofficeResponse:
    return render_template(
        "components/dynamic/modal_form.html",
        form=EmptyForm(),
        dst=url_for("backoffice_web.non_payment_notices.set_no_continuation", notice_id=notice_id),
        div_id=f"no-continuation-modal-{notice_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Classer sans suite",
        button_text="Classer sans suite",
        ajax_submit=False,
    )


@non_payment_notices_blueprint.route("/<int:notice_id>/no-continuation", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def set_no_continuation(notice_id: int) -> utils.BackofficeResponse:
    notice = _get_notice(notice_id)

    notice.status = offerers_models.NoticeStatus.WITHOUT_CONTINUATION
    db.session.add(notice)

    non_payment_notice_notification.send_non_payment_notice_without_continuation_email(notice)

    return _redirect_to_list()


@non_payment_notices_blueprint.route("/<int:notice_id>/close", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def get_close_form(notice_id: int) -> utils.BackofficeResponse:
    return render_template(
        "components/dynamic/modal_form.html",
        form=forms.CloseForm(),
        dst=url_for("backoffice_web.non_payment_notices.close", notice_id=notice_id),
        div_id=f"close-modal-{notice_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Terminer",
        button_text="Terminer",
        ajax_submit=False,
    )


@non_payment_notices_blueprint.route("/<int:notice_id>/close", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES)
def close(notice_id: int) -> utils.BackofficeResponse:
    notice = _get_notice(notice_id)

    form = forms.CloseForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_to_list()

    if form.batch.data:
        batches = (
            db.session.query(finance_models.CashflowBatch)
            .filter(finance_models.CashflowBatch.id.in_(form.batch.data))
            .all()
        )
    else:
        batches = []

    notice.status = offerers_models.NoticeStatus.CLOSED
    notice.motivation = offerers_models.NoticeStatusMotivation[form.motivation.data]
    notice.batches = batches
    db.session.add(notice)
    db.session.flush()
    db.session.refresh(notice)

    recipient_type = offerers_models.NoticeRecipientType[form.recipient.data]
    non_payment_notice_notification.send_closed_non_payment_notice_email(notice, recipient_type)

    return _redirect_to_list()
