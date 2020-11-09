from datetime import datetime
from typing import Optional

from pcapi.models import Offer
from pcapi.models import UserOfferer
from pcapi.models.api_errors import ApiErrors


# FIXME (cgaunet, 2020-11-02): I moved this function from validation/routes/offers.py. It
# should not raise HTTP-related exceptions. It should rather raise
# generic exceptions such as `UserHasNotSufficientRights` and the calling
# route should have an exception handler that turns it into the
# desired HTTP-related exception (such as ForbiddenError)
# See also functions below.
def check_user_has_rights_on_offerer(user_offerer: Optional[UserOfferer]) -> None:
    errors = ApiErrors()
    errors.add_error(
        "global",
        "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information.",
    )
    errors.status_code = 403

    if user_offerer is None:
        raise errors

    if not user_offerer.isValidated:
        raise errors


def check_offer_is_editable(offer: Offer):
    if not offer.isEditable:
        error = ApiErrors()
        error.status_code = 400
        error.add_error('global', "Les offres importées ne sont pas modifiables")
        raise error


def check_stocks_are_editable_for_offer(offer: Offer) -> None:
    if offer.isFromProvider:
        api_errors = ApiErrors()
        api_errors.add_error('global', 'Les offres importées ne sont pas modifiables')
        raise api_errors


def check_required_dates_for_stock(
    offer: Offer,
    beginning: Optional[datetime],
    booking_limit_datetime: Optional[datetime],
) -> None:
    if offer.isThing:
        if beginning:
            raise ApiErrors(
                {
                    'global': [
                        "Impossible de mettre une date de début si l'offre "
                        "ne porte pas sur un événement",
                    ]
                }
            )
    else:
        if not beginning:
            raise ApiErrors({'beginningDatetime': ['Ce paramètre est obligatoire']})

        if not booking_limit_datetime:
            raise ApiErrors({'bookingLimitDatetime': ['Ce paramètre est obligatoire']})
