from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models


def send_pending_non_payment_notice_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_PENDING.value,
        params={"MOTIVATION": notice.motivation.name if notice.motivation else None},
    )
    mails.send(recipients=[notice.emitterEmail], data=data)


def send_non_payment_notice_without_continuation_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_WITHOUT_CONTINUATION.value,
        params={},
    )
    mails.send(recipients=[notice.emitterEmail], data=data)


def send_closed_non_payment_notice_email(notice: offerers_models.NonPaymentNotice) -> None:
    if not notice.emitterEmail:
        return

    data = models.TransactionalEmailData(
        template=TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED.value,
        params={"MOTIVATION": notice.motivation.name if notice.motivation else None},
    )
    mails.send(recipients=[notice.emitterEmail], data=data)
