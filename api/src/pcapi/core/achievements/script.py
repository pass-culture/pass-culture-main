import datetime

from pcapi.core.achievements.constants import current_achievements
from pcapi.core.achievements.models import Achievement
from pcapi.core.achievements.models import UserAchievement
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User
from pcapi.models import db


def create_achievements() -> None:
    in_db_achievements = db.session.query(Achievement).all()
    if len(in_db_achievements) == len(current_achievements):
        return

    for achievement in current_achievements:
        if achievement.slug in [achievement.slug for achievement in in_db_achievements]:
            continue
        db.session.add(achievement)
        db.session.commit()


def populate_achievement_table():
    create_achievements()
    create_some_user_achievements()


def create_some_user_achievements() -> None:

    user_with_one_achievement = User.query.filter_by(email="sebastien.cavalier@example.com").one_or_none()
    if user_with_one_achievement is None:
        user_with_one_achievement = users_factories.BeneficiaryFactory(email="sebastien.cavalier@example.com")
    # user_with_two_achievements = users_factories.BeneficiaryFactory()
    # user_with_all_achievements = users_factories.BeneficiaryFactory()

    if user_with_one_achievement.achievements:
        return

    user_achievement = UserAchievement(
        user=user_with_one_achievement, achievement=current_achievements[0], completionDate=datetime.datetime.utcnow()
    )
    db.session.add(user_achievement)
    # user_with_two_achievements.achievements = [current_achievements[0], current_achievements[1]]
    # user_with_all_achievements.achievements = current_achievements

    # db.session.add_all([user_with_one_achievement, user_with_two_achievements, user_with_all_achievements])
    db.session.add(user_with_one_achievement)
    db.session.commit()

    print(user_with_one_achievement.achievements)
