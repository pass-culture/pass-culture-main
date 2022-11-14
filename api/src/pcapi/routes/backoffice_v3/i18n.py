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
        case "offerer":  # pro
            return "Structure"
        case "venue":  # pro
            return "Lieu"
        case "user":  # pro
            return "Compte pro"
        case _:
            return term.replace("_", " ").capitalize()


def i18n_subscription_type(term: str) -> str:
    match term.lower():
        case "email-validation":
            return "Validation E-mail"
        case "phone-validation":
            return "Validation Numéro de téléphone"
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


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["i18n_public_account"] = i18n_public_account
    app.jinja_env.filters["i18n_subscription_type"] = i18n_subscription_type
