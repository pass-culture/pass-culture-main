import pcapi.core.payments.api as payments_api
from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer
from pcapi.repository import repository


def change_pro_users_to_beneficiary(pro_users_ids: list[int]) -> None:
    users = User.query.filter(User.id.in_(pro_users_ids)).all()
    for user in users:
        user.add_beneficiary_role()
        user.remove_pro_role()
        user.needsToFillCulturalSurvey = True
        deposit = payments_api.create_deposit(user, "public")
        repository.save(user, deposit)
        user_offerer = UserOfferer.query.filter_by(user=user).all()
        repository.delete(*user_offerer)
