"""
Fix modified info in ActionHistory.extraData
"""

import argparse
from copy import deepcopy

from pcapi.core.history import models as history_models
from pcapi.models import db


def fix_modified_info(do_update: bool = False) -> None:
    actions = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.actionType == history_models.ActionType.INFO_MODIFIED,
            history_models.ActionHistory.extraData["modified_info"].is_not(None),
        )
        .order_by(history_models.ActionHistory.id)
    )

    for action in actions:
        print(f"\naction {action.id}")
        modified_info_in_db = action.extraData.get("modified_info", {})
        print("  ", modified_info_in_db)

        extra_data_copy = deepcopy(action.extraData)
        updated = False
        for name, data in modified_info_in_db.items():
            for info in ("old_info", "new_info"):
                if data[info] in ("None", "", [], {}):
                    extra_data_copy["modified_info"][name][info] = None
                    updated = True
                elif data[info] == "True":
                    extra_data_copy["modified_info"][name][info] = True
                    updated = True
                elif data[info] == "False":
                    extra_data_copy["modified_info"][name][info] = False
                    updated = True

            if extra_data_copy["modified_info"][name]["old_info"] == extra_data_copy["modified_info"][name]["new_info"]:
                del extra_data_copy["modified_info"][name]
                updated = True

        if updated:
            print("  =>")
            print("  ", extra_data_copy["modified_info"])

            action.extraData = extra_data_copy
            db.session.add(action)
            if do_update:
                db.session.commit()
            else:
                db.session.rollback()
        else:
            print("  ok")


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Fix modified info in action_history table")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    fix_modified_info(do_update=args.not_dry)
