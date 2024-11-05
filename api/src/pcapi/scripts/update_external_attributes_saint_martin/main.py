from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.offerers.models import Venue
from pcapi.core.users.models import User


if __name__ == "__main__":
    app.app_context().push()

    users = User.query.filter(User.departementCode == "978").all()
    print(len(users), "users found")

    for i, user in enumerate(users):
        print(i, "- Update user ID:", user.id)
        update_external_user(user)

    venues = Venue.query.filter(Venue.departementCode == "978").all()
    print(len(venues), "venues found")

    for i, venue in enumerate(venues):
        print(i, "- Update venue ID:", venue.id)
        update_external_pro(venue.bookingEmail)
