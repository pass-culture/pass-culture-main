from pcapi.core.users.models import User
from pcapi.flask_app import app


with app.app_context():
    last_user = User.query.order_by(User.id.desc()).first()
    print(last_user.id)
