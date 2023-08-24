import typing

from flask import Flask


def i18n_public_account(term: str) -> str:
    match term.lower():
        case ["ko", "ok"]:
            return term.upper()
        case "redirected_to_dms":
            return "Redirigé vers DMS"
        case "underage":
            return "Pass 15-17"
        case "age-18":
            return "Pass 18"
        case "underage+age-18":
            return "Pass 15-17+18"
        case "not-eligible":
            return "Non éligible"
        case "offerer":  # pro
            return "Structure"
        case "venue":  # pro
            return "Lieu"
        case "user":  # pro
            return "Compte pro"
        case "new":  # pro
            return "Nouveau"
        case "pending":  # pro
            return "En attente"
        case "validated":  # pro
            return "Validé"
        case "rejected":  # pro
            return "Rejeté"
        case _:
            return term.replace("_", " ")


def i18n_subscription_type(term: str) -> str:
    match term.lower():
        case "email-validation":
            return "Validation Email"
        case "phone-validation":
            return "Validation N° téléphone"
        case "user-profiling":
            return "Profil Utilisateur"
        case "profile-completion":
            return "Profil Complet"
        case "identity-check":
            return "ID Check"
        case "honor-statement":
            return "Attestation sur l'honneur"
        case _:
            return term.replace("_", " ").capitalize()


def i18n_column_name(term: str) -> str:
    match term.lower():
        case "email":
            return "Email"
        case "firstname":
            return "Prénom"
        case "lastname":
            return "Nom"
        case "validatedbirthdate":
            return "Date de naissance"
        case "postalcode":
            return "Code postal"
        case "phonenumber":
            return "Téléphone"
        case "city":
            return "Ville"
        case "address":
            return "Adresse"
        case "bookingemail":
            return "Email"
        case "contact.email":
            return "Email de contact"
        case "contact.phone_number":
            return "Numéro de téléphone de contact"
        case "ispermanent":
            return "Permanent"
        case "name":
            return "Nom juridique"
        case "publicname":
            return "Nom d'usage"
        case "criteria":
            return "Tags"
        case _:
            return term.replace("_", " ").capitalize()


def i18n_column_value(term: typing.Any) -> str:
    if term is True:
        return "Vrai"

    if term is False:
        return "Faux"

    return term


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["i18n_public_account"] = i18n_public_account
    app.jinja_env.filters["i18n_subscription_type"] = i18n_subscription_type
    app.jinja_env.filters["i18n_column_name"] = i18n_column_name
    app.jinja_env.filters["i18n_column_value"] = i18n_column_value
