import argparse
from csv import DictReader
from csv import DictWriter
import datetime
import os

import pytz

from pcapi.app import app
from pcapi.core.users import models as users_models
from pcapi.models import db


app.app_context().push()

output_directory = os.environ.get("OUTPUT_DIRECTORY")
namespace = "set_eligibility_dates"


def eligibility_date_to_utc(row: dict) -> datetime.datetime:
    str_format = "%d/%m/%Y %H:%M:%S"  # 10:00:00
    local_tz = pytz.timezone("Europe/Paris")
    eligibility_date_as_local_tz = local_tz.localize(
        datetime.datetime.strptime(row["eligibility_date UTC PARIS"], str_format)
    )
    eligibility_date_as_utc = eligibility_date_as_local_tz.astimezone(pytz.utc)

    return eligibility_date_as_utc


def set_eligibility_dates() -> None:
    parser = argparse.ArgumentParser(description="Set an `eligibilityDate` for a list of users")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    users = {}
    print(os.listdir(os.path.dirname(os.path.abspath(__file__))))
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/eligibles_beta_test_batch_1.csv", encoding="utf-8") as f:
        reader = DictReader(f, delimiter=",")
        for row in reader:
            eligibility_date_as_utc = eligibility_date_to_utc(row)
            users[int(row["user_id"])] = {"eligibilityDate": eligibility_date_as_utc}

    users_with_no_new_nav_state = users_models.User.query.filter(
        users_models.User.id.in_(users), ~users_models.User.pro_new_nav_state.has()
    ).with_entities(users_models.User.id, users_models.User.email)

    insert_mapping = []
    for sql_row in users_with_no_new_nav_state:
        insert_mapping.append({"userId": sql_row.id, "eligibilityDate": users[sql_row.id]["eligibilityDate"]})
        users[sql_row.id]["email"] = sql_row.email
    db.session.bulk_insert_mappings(users_models.UserProNewNavState, insert_mapping)

    with open(f"{output_directory}/beta_users_email.csv", "w", encoding="utf-8") as f:
        fieldnames = ["user_id", "email"]
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for user_id, values in users.items():
            writer.writerow({"user_id": user_id, "email": values["email"]})

    if args.dry_run:
        db.session.rollback()
    else:
        db.session.commit()


if __name__ == "__main__":
    set_eligibility_dates()
