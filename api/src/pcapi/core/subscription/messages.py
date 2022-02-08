import datetime

from pcapi import settings
import pcapi.core.users.models as users_models
from pcapi.repository import repository

from . import models


INBOX_URL = "passculture://openInbox"
MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
REDIRECT_TO_DMS_VIEW = "passculture://verification-identite/demarches-simplifiees"
REDIRECT_TO_IDENTIFICATION = "passculture://verification-identite/identification"

MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"

DMS_ERROR_MESSAGE_USER_NOT_FOUND = """Bonjour,

                Nous avons bien reçu ton dossier. Cependant, nous avons remarqué que tu n’es pas passé par l’application  avant de déposer le dossier ou que tu n’utilises pas la même adresse email sur le site Démarches Simplifiées.

                C’est pour cette raison que tu vas devoir poursuivre ton inscription en passant ton application.

                Pour cela, il faut :
                - Télécharger l’application sur ton smartphone
                - Entrer tes informations personnelles (nom, prénom, date de naissance, mail). Tu recevras alors un mail de confirmation (il peut se cacher dans tes spams, n’hésite pas à vérifier).
                - Cliquer sur le lien de validation

                Une fois ton inscription faite, je t’invite à nous contacter pour que nous puissions t’indiquer les étapes à suivre.

                Nous te souhaitons une belle journée.

                L’équipe pass Culture"""

DMS_ERROR_MESSAGE_ERROR_ID_PIECE = """Bonjour,

Nous avons bien reçu ton dossier, mais le numéro de pièce d'identité sur le formulaire ne correspond pas à celui indiqué sur ta pièce d'identité.

Cet article peut t’aider à le trouver sur ta pièce d'identité : <a href="https://aide.passculture.app/fr/articles/5508680-jeunes-ou-puis-je-trouver-le-numero-de-ma-piece-d-identite">https://aide.passculture.app/fr/articles/5508680-jeunes-ou-puis-je-trouver-le-numero-de-ma-piece-d-identite</a>

Peux-tu mettre à jour ton dossier sur le formulaire en ligne ?

Pour t'aider à corriger ton dossier, merci de consulter cet article : <a href="https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees">https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees</a>

Merci et à très vite,

L'équipe du pass Culture"""

DMS_ERROR_MESSAGE_ERROR_POSTAL_CODE = """Bonjour,

            Le champ du code postal doit être rempli par 5 chiffres uniquement, sans lettres ni espace. Si tu as saisi ta ville dans le champ du code postal, merci de ne saisir que ces 5 chiffres.

            Pour corriger ton formulaire, cet article est là pour t'aider : <a href="https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees">https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees</a>

            Très cordialement,

            L'équipe pass du Culture"""

DMS_ERROR_MESSAGE_DOUBLE_ERROR = """Bonjour,

                                 Nous avons bien reçu ton dossier !
                                 Cependant, ton dossier ne peut pas être traiter pour la raison suivante :
                                 Un ou plusieurs champs ont été renseignés au mauvais format :

                                 - le champ Code Postal
                                 - le champ Numéro de la pièce d’identité

                                 Pour que ton dossier soit traité, tu dois le modifier en faisant bien attention de remplir correctement toutes les informations (notamment ton code postal sous format 5 chiffres et le numéro de ta pièce d’identité sous format alphanumérique sans espace et sans caractères spéciaux).

                                 Pour avoir plus d’informations sur les étapes de ton inscription sur Démarches Simplifiées, je t’invite à consulter les articles suivants :

                                 Où puis-je trouver le numéro de ma pièce d'identité ? <a href="https://aide.passculture.app/fr/articles/5508680-jeunes-ou-puis-je-trouver-le-numero-de-ma-piece-d-identite">https://aide.passculture.app/fr/articles/5508680-jeunes-ou-puis-je-trouver-le-numero-de-ma-piece-d-identite</a>
                                 Comment bien renseigner mon adresse et mon code postal lors de l'inscription ? <a href="https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees">https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees</a>


                                 Nous te souhaitons une belle journée.

                                 L’équipe pass Culture"""

DMS_ERROR_MESSSAGE_BIRTH_DATE = """Bonjour,

                        Nous avons bien reçu ton dossier, mais il y a une erreur dans la date de naissance inscrite sur le formulaire en ligne.

                        Merci de corriger ton dossier.
                        Tu trouveras de l'aide dans cet article : <a href="https://aide.passculture.app/hc/fr/sections/4411991878545-Inscription-sur-D%C3%A9marches-Simplifi%C3%A9es">https://aide.passculture.app/hc/fr/sections/4411991878545-Inscription-sur-Démarches-Simplifiées</a>

                        Bonne journée,

                        L'équipe du pass Culture"""


def create_message_jouve_manual_review(user: users_models.User, application_id: int) -> None:
    today = datetime.date.today()
    message = models.SubscriptionMessage(
        user=user,
        userMessage=f"Nous avons reçu ton dossier le {today:%d/%m/%Y} et son analyse est en cours. Cela peut prendre jusqu'à 5 jours.",
        popOverIcon=models.PopOverIcon.CLOCK,
    )
    repository.save(message)


def on_review_pending(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton document d'identité est en cours de vérification.",
        popOverIcon=models.PopOverIcon.CLOCK,
    )
    repository.save(message)


def on_ubble_journey_cannot_continue(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Désolé, la vérification de ton identité n'a pas pu aboutir. Nous t'invitons à passer par le site Démarches-Simplifiées.",
        callToActionTitle="Accéder au site Démarches-Simplifiées",
        callToActionLink=REDIRECT_TO_DMS_VIEW,
        callToActionIcon=models.CallToActionIcon.EXTERNAL,
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


def on_idcheck_document_data_not_matching(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été bloqué : Les informations que tu as renseignées ne correspondent pas à celles de ta pièce d'identité. Tu peux contacter le support pour plus d'informations.",
        callToActionTitle="Contacter le support",
        callToActionLink=MAILTO_SUPPORT + MAILTO_SUPPORT_PARAMS.format(id=user.id),
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_idcheck_document_not_supported(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton document d'identité ne te permet pas de bénéficier du pass Culture. Passe par le site des démarches simplifiées pour renouveler ta demande.",
        callToActionTitle="Accéder au site Démarches-Simplifiées",
        callToActionLink=REDIRECT_TO_DMS_VIEW,
        callToActionIcon=models.CallToActionIcon.EXTERNAL,
    )
    repository.save(message)


def on_idcheck_document_not_supported_with_retry(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton document d'identité ne te permet pas de bénéficier du pass Culture. Réessaye avec un passeport ou une carte d'identité française en cours de validité.",
        callToActionTitle="Réessayer la vérification de mon identité",
        callToActionLink=REDIRECT_TO_IDENTIFICATION,
        callToActionIcon=models.CallToActionIcon.RETRY,
    )
    repository.save(message)


def on_idcheck_invalid_document_date(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton document d'identité est expiré. Passe par le site des démarches simplifiées avec un document en cours de validité pour renouveler ta demande.",
        callToActionTitle="Contacter le support",
        callToActionLink=MAILTO_SUPPORT + MAILTO_SUPPORT_PARAMS.format(id=user.id),
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_idcheck_invalid_document_date_with_retry(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton document d'identité est expiré. Réessaye avec un passeport ou une carte d'identité française en cours de validité.",
        callToActionTitle="Réessayer la vérification de mon identité",
        callToActionLink=REDIRECT_TO_IDENTIFICATION,
        callToActionIcon=models.CallToActionIcon.RETRY,
    )
    repository.save(message)


def on_idcheck_unread_document(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Nous n'avons pas réussi à lire ton document. Passe par le site des démarches simplifiées pour renouveler ta demande.",
        callToActionTitle="Accéder au site Démarches-Simplifiées",
        callToActionLink=REDIRECT_TO_DMS_VIEW,
        callToActionIcon=models.CallToActionIcon.EXTERNAL,
    )
    repository.save(message)


def on_idcheck_unread_document_with_retry(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Nous n'avons pas réussi à lire ton document. Réessaye avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé.",
        callToActionTitle="Réessayer la vérification de mon identité",
        callToActionLink=REDIRECT_TO_IDENTIFICATION,
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


def on_idcheck_rejected(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été bloqué : Les informations que tu as renseignées ne te permettent pas de bénéficier du pass Culture.",
        popOverIcon=models.PopOverIcon.ERROR,
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
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été bloqué : Il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations.",
        callToActionTitle="Contacter le support",
        callToActionLink=MAILTO_SUPPORT + MAILTO_SUPPORT_PARAMS.format(id=user.id),
        callToActionIcon=models.CallToActionIcon.EMAIL,
    )
    repository.save(message)


def on_not_eligible(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="La date de naissance de ton document indique que tu n'es pas éligible.",
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)


def on_age_too_young(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été bloqué : Tu n'as pas encore l'âge pour bénéficier du pass Culture. Reviens à tes 15 ans pour profiter de ton crédit.",
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)


def on_age_too_old(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton dossier a été bloqué : Tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)


def on_already_beneficiary(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Tu es déjà bénéficaire.",
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)


def add_error_message(user: users_models.User, message: str) -> None:
    message = models.SubscriptionMessage(user=user, userMessage=message, popOverIcon=models.PopOverIcon.ERROR)
    repository.save(message)


def _generate_form_field_error(error_text_singular: str, error_text_plural: str, error_fields: list[str]) -> str:
    french_field_name = {
        "id_piece_number": "ta pièce d'identité",
        "postal_code": "ton code postal",
        "birth_date": "ta date de naissance",
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
        "Il semblerait que le champ ‘{formatted_error_fields}’ soit erroné. Tu peux te rendre sur le site Démarche-simplifiées pour le rectifier.",
        "Il semblerait que les champs ‘{formatted_error_fields}’ soient erronés. Tu peux te rendre sur le site Démarche-simplifiées pour les rectifier.",
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


def on_user_subscription_journey_stopped(user: users_models.User) -> None:
    message = models.SubscriptionMessage(
        user=user,
        userMessage="Ton inscription n'a pas pu aboutir.",
        popOverIcon=models.PopOverIcon.ERROR,
    )
    repository.save(message)
