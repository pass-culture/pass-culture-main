from pcapi.core.users import models as users_models
from pcapi.utils.urls import generate_firebase_dynamic_link


def get_activation_email_data_for_redactor(user: users_models.User, token: users_models.Token) -> dict:
    expiration_timestamp = int(token.expirationDate.timestamp())
    email_confirmation_link = generate_firebase_dynamic_link(
        path="signup-confirmation",
        params={"token": token.value, "expiration_timestamp": expiration_timestamp, "email": user.email},
    )
    return {
        "Mj-TemplateID": 3027506,
        "Mj-TemplateLanguage": True,
        "Mj-trackclick": 1,
        "Vars": {
            "lien_validation_mail": email_confirmation_link,
        },
    }
