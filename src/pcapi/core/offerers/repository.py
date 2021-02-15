from typing import List

from pcapi.core.users.models import User
from pcapi.models import Offerer
from pcapi.models import UserOfferer


def get_all(user: User, filters: dict) -> List[Offerer]:
    query = Offerer.query.distinct()

    if not user.isAdmin:
        query = query.join(UserOfferer, UserOfferer.offererId == Offerer.id).filter(UserOfferer.userId == user.id)

    if "validated" in filters and filters["validated"] is not None:
        if filters["validated"] == True:
            query = query.filter(Offerer.validationToken.is_(None))
        else:
            query = query.filter(Offerer.validationToken.isnot(None))

    return query.all()
