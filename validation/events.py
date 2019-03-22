from models import EventType, Event
from models.api_errors import ForbiddenError


def check_user_can_create_activation_event(user, event: Event):
    if event.type == str(EventType.ACTIVATION):
        if not user.isAdmin:
            error = ForbiddenError()
            error.addError('type', "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation")
            raise error
