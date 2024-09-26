from datetime import datetime

from flask_sse import sse
from sqlalchemy.exc import IntegrityError

from pcapi.core.achievements.models import Achievement
from pcapi.core.achievements.models import UserAchievement
from pcapi.core.users.models import User
from pcapi.models import db


def create_user_achievements(user: User, slug: str) -> None:
    achievement = Achievement.query.filter(Achievement.slug == slug).one()
    print("found achievement", achievement)
    user_achievement = UserAchievement(achievement=achievement, user=user, completionDate=datetime.utcnow())
    try:
        db.session.add(user_achievement)
        db.session.commit()
        print("Added user achievement")
        sse.publish({"achievementSlug": slug}, type="achievementCompleted")
        print("Published achievement")
    except IntegrityError:
        db.session.rollback()
