from pcapi import settings
from pcapi.core.finance.models import CashflowBatch
from pcapi.core.internal_notifications.api import send_internal_message


def send(batch: CashflowBatch) -> None:
    send_internal_message(
        channel=settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"L'envoi des factures du ({batch.label}) sur l'outil comptable est terminé avec succès",
                },
            }
        ],
        icon_emoji=":large_green_circle:",
    )
