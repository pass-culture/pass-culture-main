from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offerers import models as offerers_models
from pcapi.utils.date import get_date_formatted_for_email


def _get_notice_params(notice: offerers_models.NonPaymentNotice) -> dict:
    return {
        "AMOUNT": format_price(notice.amount, notice.offerer),
        "BATCH_LABEL": notice.batch.label if notice.batch else None,
        "DATE_RECEIVED": get_date_formatted_for_email(notice.dateReceived),
        "MOTIVATION": notice.motivation.name if notice.motivation else None,
        "NOTICE_TYPE": notice.noticeType.value,
        "OFFERER_NAME": notice.offerer.name if notice.offerer else None,
    }


def send_pending_non_payment_notice_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_PENDING.value,
        params=_get_notice_params(notice),
    )
    mails.send(recipients=[notice.emitterEmail], data=data)


def send_non_payment_notice_without_continuation_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_WITHOUT_CONTINUATION.value,
        params=_get_notice_params(notice),
    )
    mails.send(recipients=[notice.emitterEmail], data=data)


def send_closed_non_payment_notice_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED.value,
        params=_get_notice_params(notice),
    )
    mails.send(recipients=[notice.emitterEmail], data=data)
