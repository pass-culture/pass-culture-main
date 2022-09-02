from pcapi.core.fraud import models as fraud_models


DMS_ERROR_MESSAGE_USER_NOT_FOUND = """Bonjour,

                Nous avons bien reçu ton dossier. Cependant, nous avons remarqué que tu n’avais pas créé de compte sur l’application pass Culture avec l’adresse email que tu utilises sur le site Démarches Simplifiées.

                Pour cela, il te faut :
                - Télécharger l’application sur ton smartphone ou y accéder en suivant le lien suivant : passculture.app
                - Créer un compte en indiquant la même adresse email que celle que tu utilises sur Démarches Simplifiées.
                - Cliquer sur le lien de validation reçu par mail.

                Ensuite, je t’invite à patienter le temps que ton dossier déposé sur Démarches Simplifiées soit accepté.

                Nous te souhaitons une belle journée !

                L’équipe pass Culture"""


def build_field_errors_user_message(field_errors: list[fraud_models.DmsFieldErrorDetails]) -> str:
    error_keys = [error.key for error in field_errors]
    field_errors_list_str = "\n".join(f" - {field.get_field_label()}" for field in field_errors)
    message = (
        f"Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant {field_errors[0].get_field_label()}, inscrit sur le formulaire en ligne :\n"
        if len(field_errors) == 1
        else f"Nous avons bien reçu ton dossier, mais il y a une erreur dans les champs suivants, inscrits sur le formulaire en ligne :\n{field_errors_list_str}\n\n"
        "Pour que ton dossier soit traité, tu dois le modifier en faisant bien attention à remplir correctement toutes les informations.\n"
        "Pour avoir plus d’informations sur les étapes de ton inscription sur Démarches Simplifiées, nous t’invitons à consulter les articles suivants :\n"
        'Jeune de 18 ans : <a href="https://aide.passculture.app/hc/fr/articles/4411991957521--Jeunes-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n'
        'Jeune de 15 à 17 ans : <a href="https://aide.passculture.app/hc/fr/articles/4404373671324--Jeunes-15-17-ans-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes 15-17 ans] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n\n'
    )
    if fraud_models.DmsFieldErrorKeyEnum.postal_code in error_keys:
        message += "Ton code postal doit être renseigné sous format 5 chiffres uniquement, sans lettre ni espace\n"
        message += '<a href="https://aide.passculture.app/hc/fr/articles/4411998995985--Jeunes-Comment-bien-renseigner-mon-adresse-et-mon-code-postal-lors-de-l-inscription-">Comment bien renseigner mon adresse et mon code postal lors de l’inscription ? </a>\n\n'
    if fraud_models.DmsFieldErrorKeyEnum.id_piece_number in error_keys:
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


def build_dms_error_message_user_not_eligible(formatted_birth_date: str) -> str:
    return (
        "Bonjour,\n"
        "\n"
        f"Nous avons bien reçu ton dossier, mais la date de naissance que tu as renseignée ({formatted_birth_date}) indique que tu n’as pas l’âge requis pour profiter du pass Culture (tu dois avoir entre 15 et 18 ans).\n"
        f"S’il s’agit d’une erreur, tu peux modifier ton dossier.\n"
        "\n"
        'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>'
        "\n"
        "Bonne journée,\n"
        "\n"
        "L’équipe du pass Culture"
    )
