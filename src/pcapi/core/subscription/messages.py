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


def on_fraud_review_ko(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été rejeté. Tu n'es pas éligible au pass culture.",
        popOverIcon=models.PopOverIcon.INFO,
    )
    repository.save(message)


def on_redirect_to_dms_from_idcheck(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous n'arrivons toujours pas à lire ton document. Consulte l'e-mail envoyé le {today:%d/%m/%Y} pour plus d'informations.",
        callToActionTitle="Consulter mes e-mails",
        callToActionLink="passculture://openInbox",
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_dms_application_received(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous avons bien reçu ton dossier le {today:%d/%m/%Y}. Rends toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel.",
        popOverIcon=models.PopOverIcon.FILE,
    )
    repository.save(message)


def on_dms_application_refused(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier déposé sur le site Démarches-Simplifiées a été rejeté. Tu n’es malheureusement pas éligible au pass culture.",
        popOverIcon=models.PopOverIcon.WARNING,
    )
    repository.save(message)


def on_duplicate_user(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Ce document a déjà été analysé. Vérifie que tu n’as pas créé de compte avec une autre adresse e-mail. Consulte l’e-mail envoyé le {today:%d/%m/%Y} pour plus d’informations.",
        callToActionLink="passculture://openInbox",
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)
