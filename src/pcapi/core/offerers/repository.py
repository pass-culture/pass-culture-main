from typing import List

from pcapi.core.users.models import User
from pcapi.models import Offerer
from pcapi.models import UserOfferer


def get_all_validated(user: User) -> List[Offerer]:
    query = Offerer.query.distinct()

    if not user.isAdmin:
        query = query.join(UserOfferer, UserOfferer.offererId == Offerer.id).filter(UserOfferer.userId == user.id)

    query = query.filter(Offerer.validationToken.is_(None))

    return query.all()
