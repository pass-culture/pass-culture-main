from sqlalchemy.orm import joinedload

from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import UserSQLEntity
from pcapi.repository import repository


def fill_pro_department_code_with_offerer_postal_code() -> None:
    pro_user_to_update = (
        UserSQLEntity.query.join(UserOfferer)
        .join(Offerer)
        .filter(Offerer.postalCode.startswith("75"))
        .filter(UserSQLEntity.departementCode == "93")
        .options(joinedload(UserSQLEntity.offerers))
        .all()
    )

    for pro_user in pro_user_to_update:
        offerer = _get_user_initial_linked_offerer(pro_user)
        pro_user.departementCode = PostalCode(offerer.postalCode).get_departement_code()

    repository.save(*pro_user_to_update)


def _get_user_initial_linked_offerer(pro_user: UserSQLEntity) -> Offerer:
    return sorted(pro_user.UserOfferers, key=lambda user_offerer: user_offerer.id)[0].offerer
