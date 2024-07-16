from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models


def get_email(first_name: str, last_name: str, domain: str) -> str:
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )


# helper to serialize pro user's
def get_pro_user_helper(user: users_models.User) -> dict:
    return {"email": user.email}


def get_pro_user_and_venue_helper(user: users_models.User, venue: offerers_models.Venue) -> dict:
    return {
        "email": user.email,
        "siret": venue.siret,
        "siren": venue.managingOfferer.siren,
        "offerer": venue.managingOfferer.name,
    }
