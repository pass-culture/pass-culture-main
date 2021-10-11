import datetime

import pcapi.core.users.models as users_models
from pcapi.repository import repository

from . import models


def create_message_jouve_manual_review(user: users_models.User, application_id: int) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous avons reçu ton dossier le {today:%d/%m/%Y} et son analyse peut prendre jusqu'à 5 jours.",
        popOverIcon=models.PopOverIcon.CLOCK,
    )
    repository.save(message)
