"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37867-script-massive-user-tagging/api/src/pcapi/scripts/user_mass_tagging/main.py

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

AMBASSADEUR_TAG_ID = 18
SAISON5_TAG_ID = 1


def _update_user_tags(user: users_models.User, tags: list) -> None:
    old_tags = {str(tag) for tag in user.tags}
    new_tags = {str(tag) for tag in tags}
    removed_tags = old_tags - new_tags
    added_tags = new_tags - old_tags

    user.tags = tags

    if added_tags or removed_tags:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            user=user,
            comment="PC-37867 - Tag en masse des jeunes",
            modified_info={"tags": {"old_info": sorted(removed_tags) or None, "new_info": sorted(added_tags) or None}},
        )

    db.session.add(user)


def _get_user_city_tag(city: str) -> users_models.UserTag:
    city_tag = db.session.query(users_models.UserTag).filter(users_models.UserTag.name == city).one()
    return city_tag


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        yield from csv_rows


@atomic()
def main(filename: str, not_dry: bool) -> None:
    rows = _read_csv_file(filename)
    ambassadeur_tag = db.session.query(users_models.UserTag).filter(users_models.UserTag.id == AMBASSADEUR_TAG_ID).one()
    saison5_tag = db.session.query(users_models.UserTag).filter(users_models.UserTag.id == SAISON5_TAG_ID).one()

    if not not_dry:
        mark_transaction_as_invalid()

    update_user_count = 0
    for row in rows:
        with atomic():
            user_id = row["ID"]
            user = db.session.query(users_models.User).filter(users_models.User.id == user_id).one_or_none()
            if not user:
                logger.info("User %s not found ", user_id)
            else:
                city = row["Ville"]
                tags = [ambassadeur_tag, saison5_tag, _get_user_city_tag(city)]
                _update_user_tags(user, tags)
                update_user_count += 1
            db.session.flush()

    logger.info("%s users updated", update_user_count)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--filename", type=str, required=True)
    args = parser.parse_args()

    main(filename=args.filename, not_dry=args.not_dry)
