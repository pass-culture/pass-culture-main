from models import Thing, ThingType
from models.api_errors import ForbiddenError


def check_user_can_create_activation_thing(user, thing: Thing):
    if thing.type == str(ThingType.ACTIVATION):
        if not user.isAdmin:
            error = ForbiddenError()
            error.addError('type', "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation")
            raise error
