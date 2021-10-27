import datetime

import pcapi.core.users.api as users_api
import pcapi.core.users.models as users_models
from pcapi.repository import repository

from . import models


INBOX_URL = "passculture://openInbox"


def create_message_jouve_manual_review(user: users_models.User, application_id: int) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous avons reçu ton dossier le {today:%d/%m/%Y} et son analyse est en cours. Cela peut prendre jusqu'à 5 jours.",
        popOverIcon=models.PopOverIcon.CLOCK,
    )
    repository.save(message)


def on_fraud_review_ko(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été rejeté. Tu n'es malheureusement pas éligible au pass culture.",
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)


def on_redirect_to_dms_from_idcheck(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous n'arrivons pas à lire ton document. Consulte l'e-mail envoyé le {today:%d/%m/%Y} pour plus d'informations.",
        callToActionTitle="Consulter mes e-mails",
        callToActionLink=INBOX_URL,
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_idcheck_invalid_age(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Ton dossier a été refusé : ton document indique que tu n’as pas 18 ans. Consulte l’e-mail envoyé le {today:%d/%m/%Y} pour plus d’informations.",
        callToActionTitle="Consulter mes e-mails",
        callToActionLink=INBOX_URL,
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_idcheck_invalid_document(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Ton dossier a été refusé : le document transmis est invalide. Consulte l’e-mail envoyé le {today:%d/%m/%Y} pour plus d’informations.",
        callToActionTitle="Consulter mes e-mails",
        callToActionLink=INBOX_URL,
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_idcheck_invalid_document_date(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Ton dossier a été refusé : le document que tu as transmis est expiré. Consulte l’e-mail envoyé le {today:%d/%m/%Y} pour plus d’informations.",
        callToActionTitle="Consulter mes e-mails",
        callToActionLink=INBOX_URL,
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_id_check_unread_document(user: users_models.User) -> None:
    token = users_api.create_id_check_token(user)
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier n’a pas pu être validé car la photo que tu as transmise est illisible.",
        callToActionTitle="Essayer avec une autre photo",
        callToActionLink=f"passculture://idcheck?token={token}",
        callToActionIcon=models.CallToActionIcon.RETRY,
    )
    repository.save(message)


def on_idcheck_unread_mrz(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous n'arrivons pas à traiter ton document. Consulte l'e-mail envoyé le {today:%d/%m/%Y} pour plus d'informations.",
        callToActionTitle="Consulter mes e-mails",
        callToActionLink=INBOX_URL,
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
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)


def on_duplicate_user(user: users_models.User) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Ce document a déjà été analysé. Vérifie que tu n’as pas créé de compte avec une autre adresse e-mail. Consulte l’e-mail envoyé le {today:%d/%m/%Y} pour plus d’informations.",
        callToActionLink="passculture://openInbox",
        callToActionTitle="Consulter mes e-mails",
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def _generate_form_field_error(error_text_singular: str, error_text_plural: str, error_fields: list[str]) -> str:
    french_field_name = {
        "id_piece_number": "ta pièce d'identité",
        "postal_code": "ton code postal",
    }

    user_message = error_text_singular.format(
        formatted_error_fields=french_field_name.get(error_fields[0], error_fields[0])
    )
    if len(error_fields) > 1:
        field_text = ", ".join(french_field_name.get(field, field) for field in error_fields)
        user_message = error_text_plural.format(formatted_error_fields=field_text)

    return user_message


def on_dms_application_parsing_errors_but_updatables_values(user: users_models.User, error_fields: list[str]) -> None:
    user_message = _generate_form_field_error(
        "Il semblerait que ‘{formatted_error_fields}’ soit erroné. Tu peux te rendre sur le site Démarche-simplifiées pour le rectifier.",
        "Il semblerait que ‘{formatted_error_fields}’ soient erronés. Tu peux te rendre sur le site Démarche-simplifiées pour les rectifier.",
        error_fields,
    )
    message = models.SubscriptionMessage(
        user=user,
        userMessage=user_message,
        popOverIcon=models.PopOverIcon.WARNING,
    )
    repository.save(message)


def on_dms_application_parsing_errors(user: users_models.User, error_fields: list[str]) -> None:
    user_message = _generate_form_field_error(
        "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé car le champ ‘{formatted_error_fields}’ n’est pas valide.",
        "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé car les champs ‘{formatted_error_fields}’ ne sont pas valides.",
        error_fields,
    )
    message = models.SubscriptionMessage(
        user=user,
        userMessage=user_message,
        popOverIcon=models.PopOverIcon.WARNING,
    )
    repository.save(message)
