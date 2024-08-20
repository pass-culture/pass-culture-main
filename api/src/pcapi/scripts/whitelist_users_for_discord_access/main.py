import argparse
import sys

from input_data import FIRST_INPUT  # pylint: disable=import-error

from pcapi.app import app
from pcapi.core.users.models import DiscordUser
from pcapi.core.users.models import User
from pcapi.models import db


app.app_context().push()


def whitelist_users_for_discord_access(user_ids: list[int]) -> None:
    for user_id in user_ids:
        user = User.query.filter(User.id == user_id).first()
        if not user:
            print(f"User with id {user_id} not found")
            continue
        if DiscordUser.query.filter(DiscordUser.userId == user_id).first():
            DiscordUser.query.filter(DiscordUser.userId == user_id).update(
                {"hasAccess": True}, synchronize_session=False
            )
        else:
            discord_user = DiscordUser(userId=user_id, hasAccess=True)
            db.session.add(discord_user)
    db.session.commit()


def blacklist_users_for_discord_access(user_ids: list[int]) -> None:
    DiscordUser.query.filter(DiscordUser.userId.in_(user_ids)).update({"hasAccess": False}, synchronize_session=False)
    db.session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whitelist or blacklist users for discord access")
    parser.add_argument("command", help="Command to execute", choices=["blacklist", "whitelist"])
    parser.add_argument("user_ids", help="List of user ids. 0 to use default ids list ", nargs="+", type=int)
    args = parser.parse_args()

    command = args.command
    ids = args.user_ids

    if ids[0] == 0:
        print("Using default input")
        ids = FIRST_INPUT
    else:
        print(f"Will {command} users with the following ids: {ids}")

    if command == "blacklist":
        blacklist_users_for_discord_access(ids)

    elif command == "whitelist":
        whitelist_users_for_discord_access(ids)

    else:
        print("Invalid command, please provide 'blacklist' or 'whitelist'")
        sys.exit(1)
