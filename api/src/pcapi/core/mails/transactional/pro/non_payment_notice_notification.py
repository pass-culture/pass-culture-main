from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offerers import models as offerers_models
from pcapi.utils.date import get_date_formatted_for_email


def _get_notice_params(notice: offerers_models.NonPaymentNotice) -> dict:
    return {
        "AMOUNT": format_price(notice.amount, notice.offerer),
        "BATCH_LABEL": ", ".join([batch.label for batch in notice.batches]) or None,
        "DATE_RECEIVED": get_date_formatted_for_email(notice.dateReceived),
        "MOTIVATION": notice.motivation.name if notice.motivation else None,
        "OFFERER_NAME": notice.offerer.name if notice.offerer else None,
        "REFERENCE": notice.reference,
    }


def send_pending_non_payment_notice_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    match notice.motivation:
        case offerers_models.NoticeStatusMotivation.OFFERER_NOT_FOUND:
            template = TransactionalEmail.NON_PAYMENT_NOTICE_PENDING_OFFERER_NOT_FOUND.value
        case offerers_models.NoticeStatusMotivation.PRICE_NOT_FOUND:
            template = TransactionalEmail.NON_PAYMENT_NOTICE_PENDING_PRICE_NOT_FOUND.value
        case _:
            raise ValueError(notice.motivation)

    data = models.TransactionalEmailData(template=template, params=_get_notice_params(notice))
    mails.send(recipients=[notice.emitterEmail], data=data)


def send_non_payment_notice_without_continuation_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_WITHOUT_CONTINUATION.value,
        params=_get_notice_params(notice),
    )
    mails.send(recipients=[notice.emitterEmail], data=data)


def send_closed_non_payment_notice_email(
    notice: offerers_models.NonPaymentNotice, recipient_type: offerers_models.NoticeRecipientType
) -> None:
    if not notice.emitterEmail:
        return

    if recipient_type == offerers_models.NoticeRecipientType.PRO:
        template = TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_PRO.value
    elif recipient_type == offerers_models.NoticeRecipientType.SGC:
        match notice.motivation:
            case offerers_models.NoticeStatusMotivation.ALREADY_PAID:
                template = TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_SGC_ALREADY_PAID.value
            case offerers_models.NoticeStatusMotivation.REJECTED:
                template = TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_SGC_REJECTED.value
            case offerers_models.NoticeStatusMotivation.NO_LINKED_BANK_ACCOUNT:
                template = TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_SGC_NO_LINKED_BANK_ACCOUNT.value
            case _:
                raise ValueError(notice.motivation)
    else:
        raise ValueError(recipient_type)

    data = models.TransactionalEmailData(template=template, params=_get_notice_params(notice))
    mails.send(recipients=[notice.emitterEmail], data=data)
