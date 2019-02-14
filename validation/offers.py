from models import RightsType
from models.api_errors import ResourceNotFound
from utils.rest import ensure_current_user_has_rights


def check_user_has_rights_for_query(offerer_id, venue, venue_id):
    if venue_id:
        ensure_current_user_has_rights(RightsType.editor,
                                       venue.managingOffererId)
    elif offerer_id:
        ensure_current_user_has_rights(RightsType.editor,
                                       offerer_id)


def check_venue_exists_when_requested(venue, venue_id):
    if venue_id and venue is None:
        errors = ResourceNotFound()
        errors.addError(
            'global',
            "Ce lieu n'a pas été trouvé"
        )
        raise errors
