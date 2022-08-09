import datetime

from pcapi import settings
from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core.subscription.dms import models as dms_models
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
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


def build_field_errors_user_message(field_errors: list[dms_models.DmsFieldErrorDetails]) -> str:
    error_keys = [error.key for error in field_errors]
    field_errors_list_str = "\n".join(f" - {field.get_field_label()}" for field in field_errors)
    message = (
        f"Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant {field_errors[0].get_field_label()}, inscrit sur le formulaire en ligne:\n"
        if len(field_errors) == 1
        else f"Nous avons bien reçu ton dossier, mais il y a une erreur dans les champs suivants, inscrits sur le formulaire en ligne:\n{field_errors_list_str}\n\n"
        "Pour que ton dossier soit traité, tu dois le modifier en faisant bien attention à remplir correctement toutes les informations.\n"
        "Pour avoir plus d’informations sur les étapes de ton inscription sur Démarches Simplifiées, nous t’invitons à consulter les articles suivants :\n"
        'Jeune de 18 ans : <a href="https://aide.passculture.app/hc/fr/articles/4411991957521--Jeunes-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n'
        'Jeune de 15 à 17 ans : <a href="https://aide.passculture.app/hc/fr/articles/4404373671324--Jeunes-15-17-ans-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes 15-17 ans] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n\n'
    )
    if dms_models.DmsFieldErrorKeyEnum.postal_code in error_keys:
        message += "Ton code postal doit être renseigné sous format 5 chiffres uniquement, sans lettre ni espace\n"
        message += '<a href="https://aide.passculture.app/hc/fr/articles/4411998995985--Jeunes-Comment-bien-renseigner-mon-adresse-et-mon-code-postal-lors-de-l-inscription-">Comment bien renseigner mon adresse et mon code postal lors de l’inscription ? </a>\n\n'
    if dms_models.DmsFieldErrorKeyEnum.id_piece_number in error_keys:
        message += "Ton numéro de pièce d’identité doit être renseigné sous format alphanumérique sans espace et sans caractères spéciaux\n"
        message += '<a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité">Où puis-je trouver le numéro de ma pièce d’identité ?</a>\n\n'
    general_help_article_link = '<a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>'

    return (
        "Bonjour,\n\n"
        f"{message}"
        "Merci de corriger ton dossier.\n\n"
        f"Tu trouveras de l’aide dans cet article : {general_help_article_link}\n\n"
        "Nous te souhaitons une belle journée.\n\n"
        "L’équipe du pass Culture"
    )


def build_dms_error_message_user_not_eligible(birth_date: datetime.date) -> str:
    return (
        "Bonjour,\n"
        "\n"
        f"Nous avons bien reçu ton dossier, mais la date de naissance que tu as renseignée ({birth_date.isoformat()}) indique que tu n’as pas l’âge requis pour profiter du pass Culture (tu dois avoir entre 15 et 18 ans).\n"
        f"S’il s’agit d’une erreur, tu peux modifier ton dossier.\n"
        "\n"
        'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>'
        "\n"
        "Bonne journée,\n"
        "\n"
        "L’équipe du pass Culture"
    )


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
        userMessage="Ton dossier a été refusé : tu n’es malheureusement pas éligible au pass Culture.",
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
        userMessage="Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : tu n’es malheureusement pas éligible au pass Culture.",
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


def _add_error_message(user: users_models.User, message: str) -> None:
    message = models.SubscriptionMessage(user=user, userMessage=message, popOverIcon=models.PopOverIcon.ERROR)
    repository.save(message)


def _generate_form_field_error(
    error_text_singular: str, error_text_plural: str, error_fields: list[dms_models.DmsFieldErrorDetails]
) -> str:
    field_text = ", ".join(field.get_field_label() for field in error_fields)
    if len(error_fields) == 1:
        user_message = error_text_singular.format(formatted_error_fields=field_text)
    else:
        user_message = error_text_plural.format(formatted_error_fields=field_text)

    return user_message


def on_dms_application_field_errors(
    user: users_models.User, error_fields: list[dms_models.DmsFieldErrorDetails], is_application_updatable: bool
) -> None:
    if is_application_updatable:
        user_message = _generate_form_field_error(
            "Il semblerait que le champ ‘{formatted_error_fields}’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier.",
            "Il semblerait que les champs ‘{formatted_error_fields}’ soient erronés. Tu peux te rendre sur le site Démarches-simplifiées pour les rectifier.",
            error_fields,
        )
    else:
        user_message = _generate_form_field_error(
            "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : le champ ‘{formatted_error_fields}’ n’est pas valide.",
            "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : les champs ‘{formatted_error_fields}’ ne sont pas valides.",
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


### Educonnect specific messages ###
def on_educonnect_age_not_valid(user: users_models.User, educonnect_user: educonnect_models.EduconnectUser) -> None:
    message = f"Ton dossier a été refusé. La date de naissance enregistrée sur ton compte ÉduConnect ({educonnect_user.birth_date.strftime('%d/%m/%Y')}) indique que tu n'as pas entre {users_constants.ELIGIBILITY_UNDERAGE_RANGE[0]} et {users_constants.ELIGIBILITY_UNDERAGE_RANGE[-1]} ans."
    _add_error_message(user, message)


def on_educonnect_not_eligible(user: users_models.User, educonnect_user: educonnect_models.EduconnectUser) -> None:
    message = f"La date de naissance de ton dossier ÉduConnect ({educonnect_user.birth_date.strftime('%d/%m/%Y')}) indique que tu n'es pas éligible."
    eligibity_start = users_api.get_eligibility_start_datetime(educonnect_user.birth_date)
    if datetime.datetime.utcnow() < eligibity_start:  # type: ignore [operator]
        message += f" Tu seras éligible le {eligibity_start.strftime('%d/%m/%Y')}."  # type: ignore [union-attr]
    _add_error_message(user, message)


def on_educonnect_duplicate_user(user: users_models.User) -> None:
    message = "Ton compte ÉduConnect est déjà rattaché à un compte pass Culture. Vérifie que tu n'as pas déjà créé un compte avec une autre adresse e-mail."
    _add_error_message(user, message)


def on_educonnect_duplicate_ine(user: users_models.User) -> None:
    message = "Ton identificant national INE est déjà rattaché à un autre compte pass Culture. Vérifie que tu n'as pas déjà créé un compte avec une autre adresse mail."
    _add_error_message(user, message)
