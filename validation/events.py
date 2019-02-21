from models import ApiErrors, EventType, Event
from models.api_errors import ForbiddenError


def check_has_venue_id(venue_id):
    if venue_id is None:
        api_errors = ApiErrors()
        api_errors.addError('venueId', 'Vous devez préciser un identifiant de lieu')
        raise api_errors

def check_user_can_create_activation_event(user, event: Event):
    if event.type == str(EventType.ACTIVATION):
        if not user.isAdmin:
            error = ForbiddenError()
            error.addError('type', "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation")
            raise error
