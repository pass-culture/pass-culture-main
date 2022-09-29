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
        case _:
            return term.replace("_", " ").capitalize()


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["i18n_public_account"] = i18n_public_account
