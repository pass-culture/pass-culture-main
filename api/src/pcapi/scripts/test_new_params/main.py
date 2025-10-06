"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/mageoffray/bsr-test-new-script-starting/api/src/pcapi/scripts/test_new_params/main.py

"""

import argparse
import logging

from pcapi.app import app


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    pass


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
