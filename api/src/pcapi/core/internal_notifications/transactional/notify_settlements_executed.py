from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.internal_notifications.api import send_internal_message


def send(batch: finance_models.SettlementBatch) -> None:
    send_internal_message(
        channel=settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Les virements du lot {batch.name} ({batch.label}) ont été exécutés.",
                },
            }
        ],
        icon_emoji=":billets_volants:",
    )
