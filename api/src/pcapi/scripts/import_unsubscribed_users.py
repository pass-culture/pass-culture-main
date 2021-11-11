from pathlib import Path

from pcapi.core.users.external.sendinblue import import_contacts_in_sendinblue
from pcapi.core.users.models import User
from pcapi.flask_app import app
from pcapi.repository import repository
from pcapi.scripts.batch_update_users_attributes import format_sendinblue_users


def _get_emails() -> list[str]:
    unsubscribed_users = []
    script_execution_dir = Path().resolve()

    file_to_open = script_execution_dir / "unsubscribed_users.txt"

    # Expecting unsubscribed_users.txt to be a text file containing one email per line
    with open(file_to_open, "r") as file:
        unsubscribed_users = file.read().splitlines()
    return unsubscribed_users


def synchronize_unsubscribed_users() -> None:
    print("\nPlease execute this script in the same directory as unsubscribed_users.txt")
    print("To check current path:\nfrom pathlib import Path\nPath().resolve()\n")
    unsubscribed_users = _get_emails()
    total_users = len(unsubscribed_users)
    with app.app_context():
        print("Fetching users to update...")
        users_to_update = User.query.filter(User.email.in_(unsubscribed_users))
        users_found_in_db = users_to_update.count()
        print("Found %s users" % users_found_in_db)

        print("Updating users:")
        for index, user in enumerate(users_to_update):
            user.notificationSubscriptions = (
                {**user.notificationSubscriptions, "marketing_email": False}
                if user.notificationSubscriptions is not None
                else {"marketing_email": False}
            )
            print("%s/%s" % (index + 1, users_found_in_db))
        repository.save(*users_to_update)

    print("Updated %s users out of %s" % (users_found_in_db, total_users))

    sendinblue_users_data = format_sendinblue_users(users_to_update.all())
    import_contacts_in_sendinblue(sendinblue_users_data, email_blacklist=True)
