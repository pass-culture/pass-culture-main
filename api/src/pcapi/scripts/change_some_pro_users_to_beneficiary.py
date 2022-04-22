import pcapi.core.offerers.models as offerers_models
import pcapi.core.payments.api as payments_api
import pcapi.core.users.models as users_models
from pcapi.repository import repository


def change_pro_users_to_beneficiary(pro_users_ids: list[int]) -> None:
    users = users_models.User.query.filter(users_models.User.id.in_(pro_users_ids)).all()
    for user in users:
        user.add_beneficiary_role()
        user.remove_pro_role()
        user.needsToFillCulturalSurvey = True
        deposit = payments_api.create_deposit(user, "public", users_models.EligibilityType.AGE18)
        repository.save(user, deposit)
        user_offerer = offerers_models.UserOfferer.query.filter_by(user=user).all()
        repository.delete(*user_offerer)
