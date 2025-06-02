"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-36394-fix-ids-after-typeform-migration/api/src/pcapi/scripts/typeform/main.py

"""

import json
import logging
import os

from pcapi.app import app
from pcapi.core.operations.models import SpecialEvent
from pcapi.models import db


DATA_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/data.json"

logger = logging.getLogger(__name__)


def main() -> None:
    print("starting...")
    with open(DATA_PATH, "r", encoding="utf-8") as fp:
        data = json.loads(fp.read())
    print(f"{len(data)} special event to update")

    for line in data.keys():
        print(f"updating event with id: {line}")
        db.session.query(SpecialEvent).filter(SpecialEvent.id == line).update(
            data[line],
            synchronize_session=False,
        )

    print("commit")
    db.session.commit()
    print("done")


if __name__ == "__main__":
    with app.app_context():
        main()
