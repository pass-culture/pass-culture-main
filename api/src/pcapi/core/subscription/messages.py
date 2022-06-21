import datetime

from pcapi import settings
from pcapi.core.subscription.dms import models as dms_models
import pcapi.core.users.models as users_models
from pcapi.repository import repository

from . import models


INBOX_URL = "passculture://openInbox"
MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
REDIRECT_TO_DMS_VIEW = "passculture://verification-identite/demarches-simplifiees"
REDIRECT_TO_IDENTIFICATION = "passculture://verification-identite/identification"

MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"

DMS_ERROR_MESSAGE_USER_NOT_FOUND = """Bonjour,

                Nous avons bien reçu ton dossier. Cependant, nous avons remarqué que tu n’avais pas créé de compte sur l’application pass Culture avec l’adresse email que tu utilises sur le site Démarches Simplifiées.

                Pour cela, il te faut :
                - Télécharger l’application sur ton smartphone ou y accéder en suivant le lien suivant : passculture.app
                - Créer un compte en indiquant la même adresse email que celle que tu utilises sur Démarches Simplifiées.
                - Cliquer sur le lien de validation reçu par mail.

                Ensuite, je t’invite à patienter le temps que ton dossier déposé sur Démarches Simplifiées soit accepté.

                Nous te souhaitons une belle journée !

                L’équipe pass Culture"""

DMS_ERROR_MESSAGE_ERROR_ID_PIECE = """Bonjour,

Nous avons bien reçu ton dossier, mais le numéro de pièce d'identité sur le formulaire ne correspond pas à celui indiqué sur ta pièce d'identité.

Cet article peut t’aider à le trouver sur ta pièce d'identité : <a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité-">https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité-</a>

Peux-tu mettre à jour ton dossier sur le formulaire en ligne ?

Pour t'aider à corriger ton dossier, merci de consulter cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-</a>

Merci et à très vite,

L'équipe du pass Culture"""

DMS_ERROR_MESSAGE_ERROR_POSTAL_CODE = """Bonjour,

            Le champ du code postal doit être rempli par 5 chiffres uniquement, sans lettre ni espace. Si tu as saisi ta ville dans le champ du code postal, merci de ne saisir que ces 5 chiffres.

            Pour corriger ton formulaire, cet article est là pour t'aider : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-</a>

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

                                 Où puis-je trouver le numéro de ma pièce d'identité ? <a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité">https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité</a>
                                 Comment bien renseigner mon adresse et mon code postal lors de l'inscription ? <a href="https://aide.passculture.app/hc/fr/articles/4411998995985--Jeunes-Comment-bien-renseigner-mon-adresse-et-mon-code-postal-lors-de-l-inscription-">https://aide.passculture.app/hc/fr/articles/4411998995985--Jeunes-Comment-bien-renseigner-mon-adresse-et-mon-code-postal-lors-de-l-inscription-</a>


                                 Nous te souhaitons une belle journée.

                                 L’équipe pass Culture"""

DMS_ERROR_MESSSAGE_BIRTH_DATE = """Bonjour,

                        Nous avons bien reçu ton dossier, mais il y a une erreur dans la date de naissance inscrite sur le formulaire en ligne.

                        Merci de corriger ton dossier.
                        Tu trouveras de l'aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-</a>

                        Bonne journée,

                        L'équipe du pass Culture"""

DMS_NAME_INVALID_ERROR_MESSAGE = """Bonjour,

                            Nous avons bien reçu ton dossier !
                            Cependant, ton dossier ne peut pas être traité pour la raison suivante :
                            Les champs "Nom" et / ou "Prénom" ont été renseignés au mauvais format.

                            Pour que ton dossier soit traité, tu dois les modifier en faisant bien attention à remplir correctement toutes les informations. Pour avoir plus d'informations sur les étapes de ton inscription sur Démarches Simplifiées, nous t'invitons à consulter les articles suivants :

                            Jeune de 18 ans : <a href="https://aide.passculture.app/hc/fr/articles/4411991957521--Jeunes-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">https://aide.passculture.app/hc/fr/articles/4411991957521--Jeunes-Comment-remplir-le-formulaire-sur-Démarches-Simplifiées</a>
                            Jeune de 15 à 17 ans : <a href="https://aide.passculture.app/hc/fr/articles/4404373671324--Jeunes-15-17-ans-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">https://aide.passculture.app/hc/fr/articles/4404373671324--Jeunes-15-17-ans-Comment-remplir-le-formulaire-sur-Démarches-Simplifiées-</a>

                            Nous te souhaitons une belle journée,

                            L'équipe du pass Culture"""


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
        userMessage=f"Nous avons bien reçu ton dossier le {today:%d/%m/%Y}. Rends-toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel.",
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


def _generate_form_field_error(
    error_text_singular: str, error_text_plural: str, error_fields: list[dms_models.DmsParsingErrorDetails]
) -> str:
    field_text = ", ".join(field.get_field_label() for field in error_fields)
    if len(error_fields) == 1:
        user_message = error_text_singular.format(formatted_error_fields=field_text)
    else:
        user_message = error_text_plural.format(formatted_error_fields=field_text)

    return user_message


def on_dms_application_parsing_errors(
    user: users_models.User, error_fields: list[dms_models.DmsParsingErrorDetails], is_application_updatable: bool
) -> None:
    if is_application_updatable:
        user_message = _generate_form_field_error(
            "Il semblerait que le champ ‘{formatted_error_fields}’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier.",
            "Il semblerait que les champs ‘{formatted_error_fields}’ soient erronés. Tu peux te rendre sur le site Démarches-simplifiées pour les rectifier.",
            error_fields,
        )
    else:
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
