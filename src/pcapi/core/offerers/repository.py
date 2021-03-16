from typing import List

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.models import UserOfferer


def get_all_offerers_for_user(user: User, filters: dict) -> List[Offerer]:
    query = Offerer.query.filter(Offerer.isActive.is_(True))

    if not user.isAdmin:
        query = query.join(UserOfferer, UserOfferer.offererId == Offerer.id).filter(UserOfferer.userId == user.id)

    if "validated" in filters and filters["validated"] is not None:
        if filters["validated"] == True:
            query = query.filter(Offerer.validationToken.is_(None))
        else:
            query = query.filter(Offerer.validationToken.isnot(None))

    if "validated_for_user" in filters and filters["validated_for_user"] is not None:
        if filters["validated_for_user"] == True:
            query = query.filter(UserOfferer.validationToken.is_(None))
        else:
            query = query.filter(UserOfferer.validationToken.isnot(None))

    return query.all()
