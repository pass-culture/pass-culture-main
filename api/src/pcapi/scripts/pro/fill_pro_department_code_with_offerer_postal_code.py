from sqlalchemy.orm import joinedload

import pcapi.core.offerers.models as offerers_models
from pcapi.core.users.models import User
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.repository import repository


def fill_pro_department_code_with_offerer_postal_code() -> None:
    pro_user_to_update = (
        User.query.join(offerers_models.UserOfferer)
        .join(offerers_models.Offerer)
        .filter(offerers_models.Offerer.postalCode.startswith("75"))
        .filter(User.departementCode == "93")
        .options(joinedload(User.offerers))
        .all()
    )

    for pro_user in pro_user_to_update:
        offerer = _get_user_initial_linked_offerer(pro_user)
        pro_user.departementCode = PostalCode(offerer.postalCode).get_departement_code()

    repository.save(*pro_user_to_update)


def _get_user_initial_linked_offerer(pro_user: User) -> offerers_models.Offerer:
    return sorted(pro_user.UserOfferers, key=lambda user_offerer: user_offerer.id)[0].offerer
