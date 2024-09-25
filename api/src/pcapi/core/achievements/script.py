import datetime
import random

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
    create_user_with_all_achievements()


def create_some_user_achievements() -> None:

    user_with_one_achievement = User.query.filter_by(email="sebastien.cavalier@example.com").one_or_none()
    if user_with_one_achievement is None:
        user_with_one_achievement = users_factories.BeneficiaryFactory(email="sebastien.cavalier@example.com")

    if user_with_one_achievement.achievements:
        print(f"User with one achievement already exists: {user_with_one_achievement.email}")
        return

    user_achievement = UserAchievement(
        user=user_with_one_achievement,
        achievement=current_achievements[0],
        completionDate=datetime.datetime.utcnow(),
    )
    db.session.add(user_achievement)
    db.session.commit()

    print(f"Created user with one achievement: {user_with_one_achievement.email}")


def create_user_with_all_achievements() -> None:
    try:
        user_with_all_achievements = users_factories.BeneficiaryFactory(
            email="nicolas.durand@example.com",
            firstName="User",
            lastName="WithAllAchievements",
        )
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error while creating user with all achievements: {e}")
        return
    if user_with_all_achievements.achievements:
        print(f"User with all achievements already exists: {user_with_all_achievements.email}")
        return
    for achievement in current_achievements:
        random_date_in_the_past = datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(1, 365))
        with db.session.no_autoflush:
            user_achievement = UserAchievement(
                user=user_with_all_achievements,
                achievement=achievement,
                completionDate=random_date_in_the_past,
            )
            db.session.add(user_achievement)

    db.session.add(user_with_all_achievements)
    db.session.commit()

    print(f"Created user with all achievements: {user_with_all_achievements.email}")
