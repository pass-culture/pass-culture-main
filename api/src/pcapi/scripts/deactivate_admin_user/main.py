from pcapi.app import app
from pcapi.core.users import models
from pcapi.models import db


def deactivate_admin_user_session() -> None:
    admin_users = models.User.query.filter(models.User.roles.contains([models.UserRole.ADMIN]))
    admin_users_ids = set()

    for admin in admin_users:
        admin_users_ids.add(admin.id)

    models.UserSession.query.filter(models.UserSession.userId.in_(admin_users_ids)).delete()
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        deactivate_admin_user_session()
