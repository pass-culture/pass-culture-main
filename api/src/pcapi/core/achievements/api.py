from pcapi.core.users.models import User
from datetime import datetime
from pcapi.core.achievements.models import Achievement, UserAchievement
from pcapi.models import db
from sqlalchemy.exc import IntegrityError

def create_user_achievements(user: User, slug: str) -> None:
        achievement = Achievement.query.filter(Achievement.slug==slug).one()
        user_achievement = UserAchievement(achievement=achievement, user=user, completionDate=datetime.utcnow())
        try:
            db.session.add(user_achievement)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            pass


