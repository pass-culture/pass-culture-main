from urllib.parse import quote

from pcapi.core.users import models as users_models


def get_activation_email_data(user: users_models.User, token: users_models.Token) -> dict:
    first_name = user.firstName.capitalize() if user.firstName else None
    email = user.email

    return {
        "Mj-TemplateID": 994771,
        "Mj-TemplateLanguage": True,
        "Vars": {
            "prenom_user": first_name,
            "token": token.value,
            "email": quote(email),
        },
    }
