import pcapi.core.mails.transactional as transactional_mails
from pcapi.settings import GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_WITHDRAWAL_UPDATED_QUEUE_NAME
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.mails_tasks import WithdrawalChangedMailRequest


@task(
    GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_WITHDRAWAL_UPDATED_QUEUE_NAME,  # type: ignore[arg-type]
    "/sendinblue/send-withdrawal-updated-emails",
)
def send_withdrawal_detail_changed_emails(payload: WithdrawalChangedMailRequest) -> None:
    for booker in payload.bookers:
        transactional_mails.send_booking_withdrawal_updated(
            recipients=booker.recipients,
            user_first_name=booker.user_first_name,
            offer_name=booker.offer_name,
            offer_token=booker.offer_token,
            offer_withdrawal_delay=payload.offer_withdrawal_delay,
            offer_withdrawal_details=payload.offer_withdrawal_details,
            offer_withdrawal_type=payload.offer_withdrawal_type,
            offerer_name=payload.offerer_name,
            venue_address=payload.venue_address,
        )
