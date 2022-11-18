from flask import current_app as app

from pcapi.core.users.models import User


with app.app_context():
    last_user = User.query.order_by(User.id.desc()).first()
    print(last_user.id)
